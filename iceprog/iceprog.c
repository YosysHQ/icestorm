/*
 *  iceprog -- simple programming tool for FTDI-based Lattice iCE programmers
 *
 *  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
 *
 *  Permission to use, copy, modify, and/or distribute this software for any
 *  purpose with or without fee is hereby granted, provided that the above
 *  copyright notice and this permission notice appear in all copies.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 *  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 *  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 *  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 *  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 *  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 *  Relevant Documents:
 *  -------------------
 *  http://www.latticesemi.com/~/media/Documents/UserManuals/EI/icestickusermanual.pdf
 *  http://www.micron.com/~/media/documents/products/data-sheet/nor-flash/serial-nor/n25q/n25q_32mb_3v_65nm.pdf
 *  http://www.ftdichip.com/Support/Documents/AppNotes/AN_108_Command_Processor_for_MPSSE_and_MCU_Host_Bus_Emulation_Modes.pdf
 */

#define _GNU_SOURCE

#include <ftdi.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <getopt.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

static struct ftdi_context ftdic;
static bool ftdic_open = false;
static bool verbose = false;
static bool ftdic_latency_set = false;
static unsigned char ftdi_latency;

/* MPSSE engine command definitions */
enum mpsse_cmd
{
	/* Mode commands */
	MC_SETB_LOW = 0x80, /* Set Data bits LowByte */
	MC_READB_LOW = 0x81, /* Read Data bits LowByte */
	MC_SETB_HIGH = 0x82, /* Set Data bits HighByte */
	MC_READB_HIGH = 0x83, /* Read data bits HighByte */
	MC_LOOPBACK_EN = 0x84, /* Enable loopback */
	MC_LOOPBACK_DIS = 0x85, /* Disable loopback */
	MC_SET_CLK_DIV = 0x86, /* Set clock divisor */
	MC_FLUSH = 0x87, /* Flush buffer fifos to the PC. */
	MC_WAIT_H = 0x88, /* Wait on GPIOL1 to go high. */
	MC_WAIT_L = 0x89, /* Wait on GPIOL1 to go low. */
	MC_TCK_X5 = 0x8A, /* Disable /5 div, enables 60MHz master clock */
	MC_TCK_D5 = 0x8B, /* Enable /5 div, backward compat to FT2232D */
	MC_EN_3PH_CLK = 0x8C, /* Enable 3 phase clk, DDR I2C */
	MC_DIS_3PH_CLK = 0x8D, /* Disable 3 phase clk */
	MC_CLK_N = 0x8E, /* Clock every bit, used for JTAG */
	MC_CLK_N8 = 0x8F, /* Clock every byte, used for JTAG */
	MC_CLK_TO_H = 0x94, /* Clock until GPIOL1 goes high */
	MC_CLK_TO_L = 0x95, /* Clock until GPIOL1 goes low */
	MC_EN_ADPT_CLK = 0x96, /* Enable adaptive clocking */
	MC_DIS_ADPT_CLK = 0x97, /* Disable adaptive clocking */
	MC_CLK8_TO_H = 0x9C, /* Clock until GPIOL1 goes high, count bytes */
	MC_CLK8_TO_L = 0x9D, /* Clock until GPIOL1 goes low, count bytes */
	MC_TRI = 0x9E, /* Set IO to only drive on 0 and tristate on 1 */
	/* CPU mode commands */
	MC_CPU_RS = 0x90, /* CPUMode read short address */
	MC_CPU_RE = 0x91, /* CPUMode read extended address */
	MC_CPU_WS = 0x92, /* CPUMode write short address */
	MC_CPU_WE = 0x93, /* CPUMode write extended address */
};

/* Transfer Command bits */

/* All byte based commands consist of:
 * - Command byte
 * - Length lsb
 * - Length msb
 *
 * If data out is enabled the data follows after the above command bytes,
 * otherwise no additional data is needed.
 * - Data * n
 *
 * All bit based commands consist of:
 * - Command byte
 * - Length
 *
 * If data out is enabled a byte containing bitst to transfer follows.
 * Otherwise no additional data is needed. Only up to 8 bits can be transferred
 * per transaction when in bit mode.
 */

/* b 0000 0000
 *   |||| |||`- Data out negative enable. Update DO on negative clock edge.
 *   |||| ||`-- Bit count enable. When reset count represents bytes.
 *   |||| |`--- Data in negative enable. Latch DI on negative clock edge.
 *   |||| `---- LSB enable. When set clock data out LSB first.
 *   ||||
 *   |||`------ Data out enable
 *   ||`------- Data in enable
 *   |`-------- TMS mode enable
 *   `--------- Special command mode enable. See mpsse_cmd enum.
 */

#define MC_DATA_TMS  (0x40) /* When set use TMS mode */
#define MC_DATA_IN   (0x20) /* When set read data (Data IN) */
#define MC_DATA_OUT  (0x10) /* When set write data (Data OUT) */
#define MC_DATA_LSB  (0x08) /* When set input/output data LSB first. */
#define MC_DATA_ICN  (0x04) /* When set receive data on negative clock edge */
#define MC_DATA_BITS (0x02) /* When set count bits not bytes */
#define MC_DATA_OCN  (0x01) /* When set update data on negative clock edge */

/* Flash command definitions */
/* This command list is based on the Winbond W25Q128JV Datasheet */
enum flash_cmd {
	FC_WE = 0x06, /* Write Enable */
	FC_SRWE = 0x50, /* Volatile SR Write Enable */
	FC_WD = 0x04, /* Write Disable */
	FC_RPD = 0xAB, /* Release Power-Down, returns Device ID */
	FC_MFGID = 0x90, /*  Read Manufacturer/Device ID */
	FC_JEDECID = 0x9F, /* Read JEDEC ID */
	FC_UID = 0x4B, /* Read Unique ID */
	FC_RD = 0x03, /* Read Data */
	FC_FR = 0x0B, /* Fast Read */
	FC_PP = 0x02, /* Page Program */
	FC_SE = 0x20, /* Sector Erase 4kb */
	FC_BE32 = 0x52, /* Block Erase 32kb */
	FC_BE64 = 0xD8, /* Block Erase 64kb */
	FC_CE = 0xC7, /* Chip Erase */
	FC_RSR1 = 0x05, /* Read Status Register 1 */
	FC_WSR1 = 0x01, /* Write Status Register 1 */
	FC_RSR2 = 0x35, /* Read Status Register 2 */
	FC_WSR2 = 0x31, /* Write Status Register 2 */
	FC_RSR3 = 0x15, /* Read Status Register 3 */
	FC_WSR3 = 0x11, /* Write Status Register 3 */
	FC_RSFDP = 0x5A, /* Read SFDP Register */
	FC_ESR = 0x44, /* Erase Security Register */
	FC_PSR = 0x42, /* Program Security Register */
	FC_RSR = 0x48, /* Read Security Register */
	FC_GBL = 0x7E, /* Global Block Lock */
	FC_GBU = 0x98, /* Global Block Unlock */
	FC_RBL = 0x3D, /* Read Block Lock */
	FC_IBL = 0x36, /* Individual Block Lock */
	FC_IBU = 0x39, /* Individual Block Unlock */
	FC_EPS = 0x75, /* Erase / Program Suspend */
	FC_EPR = 0x7A, /* Erase / Program Resume */
	FC_PD = 0xB9, /* Power-down */
	FC_QPI = 0x38, /* Enter QPI mode */
	FC_ERESET = 0x66, /* Enable Reset */
	FC_RESET = 0x99, /* Reset Device */
};

static void check_rx()
{
	while (1) {
		uint8_t data;
		int rc = ftdi_read_data(&ftdic, &data, 1);
		if (rc <= 0)
			break;
		fprintf(stderr, "unexpected rx byte: %02X\n", data);
	}
}

static void error(int status)
{
	check_rx();
	fprintf(stderr, "ABORT.\n");
	if (ftdic_open) {
		if (ftdic_latency_set)
			ftdi_set_latency_timer(&ftdic, ftdi_latency);
		ftdi_usb_close(&ftdic);
	}
	ftdi_deinit(&ftdic);
	exit(status);
}

static uint8_t recv_byte()
{
	uint8_t data;
	while (1) {
		int rc = ftdi_read_data(&ftdic, &data, 1);
		if (rc < 0) {
			fprintf(stderr, "Read error.\n");
			error(2);
		}
		if (rc == 1)
			break;
		usleep(100);
	}
	return data;
}

static void send_byte(uint8_t data)
{
	int rc = ftdi_write_data(&ftdic, &data, 1);
	if (rc != 1) {
		fprintf(stderr, "Write error (single byte, rc=%d, expected %d).\n", rc, 1);
		error(2);
	}
}

static void send_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	/* Output only, update data on negative clock edge. */
	send_byte(MC_DATA_OUT | MC_DATA_OCN);
	send_byte(n - 1);
	send_byte((n - 1) >> 8);

	int rc = ftdi_write_data(&ftdic, data, n);
	if (rc != n) {
		fprintf(stderr, "Write error (chunk, rc=%d, expected %d).\n", rc, n);
		error(2);
	}
}

static void xfer_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	/* Input and output, update data on negative edge read on positive. */
	send_byte(MC_DATA_IN | MC_DATA_OUT | MC_DATA_OCN);
	send_byte(n - 1);
	send_byte((n - 1) >> 8);

	int rc = ftdi_write_data(&ftdic, data, n);
	if (rc != n) {
		fprintf(stderr, "Write error (chunk, rc=%d, expected %d).\n", rc, n);
		error(2);
	}

	for (int i = 0; i < n; i++)
		data[i] = recv_byte();
}

static void set_gpio(int slavesel_b, int creset_b)
{
	uint8_t gpio = 1;

	if (slavesel_b) {
		// ADBUS4 (GPIOL0)
		gpio |= 0x10;
	}

	if (creset_b) {
		// ADBUS7 (GPIOL3)
		gpio |= 0x80;
	}

	send_byte(MC_SETB_LOW);
	send_byte(gpio); /* Value */
	send_byte(0x93); /* Direction */
}

static int get_cdone()
{
	uint8_t data;
	send_byte(MC_READB_LOW);
	data = recv_byte();
	// ADBUS6 (GPIOL2)
	return (data & 0x40) != 0;
}

static void flash_read_id()
{
	// fprintf(stderr, "read flash ID..\n");

	uint8_t data[21] = { FC_JEDECID };
	set_gpio(0, 0);
	xfer_spi(data, 21);
	set_gpio(1, 0);

	fprintf(stderr, "flash ID:");
	for (int i = 1; i < 21; i++)
		fprintf(stderr, " 0x%02X", data[i]);
	fprintf(stderr, "\n");
}

static void flash_power_up()
{
	uint8_t data[1] = { FC_RPD };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_power_down()
{
	uint8_t data[1] = { FC_PD };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_write_enable()
{
	if (verbose)
		fprintf(stderr, "write enable..\n");

	uint8_t data[1] = { FC_WE };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_bulk_erase()
{
	fprintf(stderr, "bulk erase..\n");

	uint8_t data[1] = { FC_CE };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_64kB_sector_erase(int addr)
{
	fprintf(stderr, "erase 64kB sector at 0x%06X..\n", addr);

	uint8_t command[4] = { FC_BE64, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	set_gpio(0, 0);
	send_spi(command, 4);
	set_gpio(1, 0);
}

static void flash_prog(int addr, uint8_t *data, int n)
{
	if (verbose)
		fprintf(stderr, "prog 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { FC_PP, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	set_gpio(0, 0);
	send_spi(command, 4);
	send_spi(data, n);
	set_gpio(1, 0);

	if (verbose)
		for (int i = 0; i < n; i++)
			fprintf(stderr, "%02x%c", data[i], i == n - 1 || i % 32 == 31 ? '\n' : ' ');
}

static void flash_read(int addr, uint8_t *data, int n)
{
	if (verbose)
		fprintf(stderr, "read 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { FC_RD, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	set_gpio(0, 0);
	send_spi(command, 4);
	memset(data, 0, n);
	xfer_spi(data, n);
	set_gpio(1, 0);

	if (verbose)
		for (int i = 0; i < n; i++)
			fprintf(stderr, "%02x%c", data[i], i == n - 1 || i % 32 == 31 ? '\n' : ' ');
}

static void flash_wait()
{
	if (verbose)
		fprintf(stderr, "waiting..");

	while (1)
	{
		uint8_t data[2] = { FC_RSR1 };

		set_gpio(0, 0);
		xfer_spi(data, 2);
		set_gpio(1, 0);

		if ((data[1] & 0x01) == 0)
			break;

		if (verbose) {
			fprintf(stderr, ".");
			fflush(stdout);
		}
		usleep(1000);
	}

	if (verbose)
		fprintf(stderr, "\n");
}

static void flash_disable_protection()
{
	fprintf(stderr, "disable flash protection...\n");

  //WRSR 0x00
	uint8_t data[2] = { 0x01, 0x00 };
	set_gpio(0, 0);
	xfer_spi(data, 2);
	set_gpio(1, 0);
	
	flash_wait();
	
	//RDSR
	data[0] = 0x5;

	set_gpio(0, 0);\
	xfer_spi(data, 2);
	set_gpio(1, 0);

	if(data[1] != 0x00)
		fprintf(stderr, "failed to disable protection, SR now equal to 0x%02x (expected 0x00)\n", data[1]);

}


static void help(const char *progname)
{
	fprintf(stderr, "Simple programming tool for FTDI-based Lattice iCE programmers.\n");
	fprintf(stderr, "Usage: %s [-b|-n|-c] <input file>\n", progname);
	fprintf(stderr, "       %s -r|-R<bytes> <output file>\n", progname);
	fprintf(stderr, "       %s -S <input file>\n", progname);
	fprintf(stderr, "       %s -t\n", progname);
	fprintf(stderr, "\n");
	fprintf(stderr, "General options:\n");
	fprintf(stderr, "  -d <device string>    use the specified USB device [default: i:0x0403:0x6010 or i:0x0403:0x6014]\n");
	fprintf(stderr, "                          d:<devicenode>               (e.g. d:002/005)\n");
	fprintf(stderr, "                          i:<vendor>:<product>         (e.g. i:0x0403:0x6010)\n");
	fprintf(stderr, "                          i:<vendor>:<product>:<index> (e.g. i:0x0403:0x6010:0)\n");
	fprintf(stderr, "                          s:<vendor>:<product>:<serial-string>\n");
	fprintf(stderr, "  -I [ABCD]             connect to the specified interface on the FTDI chip\n");
	fprintf(stderr, "                          [default: A]\n");
	fprintf(stderr, "  -o <offset in bytes>  start address for read/write [default: 0]\n");
	fprintf(stderr, "                          (append 'k' to the argument for size in kilobytes,\n");
	fprintf(stderr, "                          or 'M' for size in megabytes)\n");
	fprintf(stderr, "  -v                    verbose output\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Mode of operation:\n");
	fprintf(stderr, "  [default]             write file contents to flash, then verify\n");
	fprintf(stderr, "  -r                    read first 256 kB from flash and write to file\n");
	fprintf(stderr, "  -R <size in bytes>    read the specified number of bytes from flash\n");
	fprintf(stderr, "                          (append 'k' to the argument for size in kilobytes,\n");
	fprintf(stderr, "                          or 'M' for size in megabytes)\n");
	fprintf(stderr, "  -c                    do not write flash, only verify (`check')\n");
	fprintf(stderr, "  -S                    perform SRAM programming\n");
	fprintf(stderr, "  -t                    just read the flash ID sequence\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Erase mode (only meaningful in default mode):\n");
	fprintf(stderr, "  [default]             erase aligned chunks of 64kB in write mode\n");
	fprintf(stderr, "                          This means that some data after the written data (or\n");
	fprintf(stderr, "                          even before when -o is used) may be erased as well.\n");
	fprintf(stderr, "  -b                    bulk erase entire flash before writing\n");
	fprintf(stderr, "  -e <size in bytes>    erase flash as if we were writing that number of bytes\n");
	fprintf(stderr, "  -n                    do not erase flash before writing\n");
	fprintf(stderr, "  -p                    disable write protection before erasing or writing\n");
	fprintf(stderr, "                          This can be useful if flash memory appears to be\n");
	fprintf(stderr, "                          bricked and won't respond to erasing or programming.\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Miscellaneous options:\n");
	fprintf(stderr, "      --help            display this help and exit\n");
	fprintf(stderr, "  --                    treat all remaining arguments as filenames\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Exit status:\n");
	fprintf(stderr, "  0 on success,\n");
	fprintf(stderr, "  1 if a non-hardware error occurred (e.g., failure to read from or\n");
	fprintf(stderr, "    write to a file, or invoked with invalid options),\n");
	fprintf(stderr, "  2 if communication with the hardware failed (e.g., cannot find the\n");
	fprintf(stderr, "    iCE FTDI USB device),\n");
	fprintf(stderr, "  3 if verification of the data failed.\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Notes for iCEstick (iCE40HX-1k devel board):\n");
	fprintf(stderr, "  An unmodified iCEstick can only be programmed via the serial flash.\n");
	fprintf(stderr, "  Direct programming of the SRAM is not supported. For direct SRAM\n");
	fprintf(stderr, "  programming the flash chip and one zero ohm resistor must be desoldered\n");
	fprintf(stderr, "  and the FT2232H SI pin must be connected to the iCE SPI_SI pin, as shown\n");
	fprintf(stderr, "  in this picture:\n");
	fprintf(stderr, "  http://www.clifford.at/gallery/2014-elektronik/IMG_20141115_183838\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Notes for the iCE40-HX8K Breakout Board:\n");
	fprintf(stderr, "  Make sure that the jumper settings on the board match the selected\n");
	fprintf(stderr, "  mode (SRAM or FLASH). See the iCE40-HX8K user manual for details.\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "If you have a bug report, please file an issue on github:\n");
	fprintf(stderr, "  https://github.com/cliffordwolf/icestorm/issues\n");
}

int main(int argc, char **argv)
{
	/* used for error reporting */
	const char *my_name = argv[0];
	for (size_t i = 0; argv[0][i]; i++)
		if (argv[0][i] == '/')
			my_name = argv[0] + i + 1;

	int read_size = 256 * 1024;
	int erase_size = 0;
	int rw_offset = 0;

	bool read_mode = false;
	bool check_mode = false;
	bool erase_mode = false;
	bool bulk_erase = false;
	bool dont_erase = false;
	bool prog_sram = false;
	bool test_mode = false;
	bool disable_protect = false;
	const char *filename = NULL;
	const char *devstr = NULL;
	enum ftdi_interface ifnum = INTERFACE_A;

	static struct option long_options[] = {
		{"help", no_argument, NULL, -2},
		{NULL, 0, NULL, 0}
	};

	int opt;
	char *endptr;
	while ((opt = getopt_long(argc, argv, "d:I:rR:e:o:cbnStvp", long_options, NULL)) != -1) {
		switch (opt) {
		case 'd':
			devstr = optarg;
			break;
		case 'I':
			if (!strcmp(optarg, "A"))
				ifnum = INTERFACE_A;
			else if (!strcmp(optarg, "B"))
				ifnum = INTERFACE_B;
			else if (!strcmp(optarg, "C"))
				ifnum = INTERFACE_C;
			else if (!strcmp(optarg, "D"))
				ifnum = INTERFACE_D;
			else {
				fprintf(stderr, "%s: `%s' is not a valid interface (must be `A', `B', `C', or `D')\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'r':
			read_mode = true;
			break;
		case 'R':
			read_mode = true;
			read_size = strtol(optarg, &endptr, 0);
			if (*endptr == '\0')
				/* ok */;
			else if (!strcmp(endptr, "k"))
				read_size *= 1024;
			else if (!strcmp(endptr, "M"))
				read_size *= 1024 * 1024;
			else {
				fprintf(stderr, "%s: `%s' is not a valid size\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'e':
			erase_mode = true;
			erase_size = strtol(optarg, &endptr, 0);
			if (*endptr == '\0')
				/* ok */;
			else if (!strcmp(endptr, "k"))
				erase_size *= 1024;
			else if (!strcmp(endptr, "M"))
				erase_size *= 1024 * 1024;
			else {
				fprintf(stderr, "%s: `%s' is not a valid size\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'o':
			rw_offset = strtol(optarg, &endptr, 0);
			if (*endptr == '\0')
				/* ok */;
			else if (!strcmp(endptr, "k"))
				rw_offset *= 1024;
			else if (!strcmp(endptr, "M"))
				rw_offset *= 1024 * 1024;
			else {
				fprintf(stderr, "%s: `%s' is not a valid offset\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'c':
			check_mode = true;
			break;
		case 'b':
			bulk_erase = true;
			break;
		case 'n':
			dont_erase = true;
			break;
		case 'S':
			prog_sram = true;
			break;
		case 't':
			test_mode = true;
			break;
		case 'v':
			verbose = true;
			break;
		case 'p':
			disable_protect = true;
			break;
		case -2:
			help(argv[0]);
			return EXIT_SUCCESS;
		default:
			/* error message has already been printed */
			fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
			return EXIT_FAILURE;
		}
	}

	if (read_mode + erase_mode + check_mode + prog_sram + test_mode > 1) {
		fprintf(stderr, "%s: options `-r'/`-R', `-e`, `-c', `-S', and `-t' are mutually exclusive\n", my_name);
		return EXIT_FAILURE;
	}

	if (bulk_erase && dont_erase) {
		fprintf(stderr, "%s: options `-b' and `-n' are mutually exclusive\n", my_name);
		return EXIT_FAILURE;
	}

	if (disable_protect && (read_mode || check_mode || prog_sram || test_mode)) {
		fprintf(stderr, "%s: option `-p' only valid in programming mode\n", my_name);
		return EXIT_FAILURE;
	}

	if (bulk_erase && (read_mode || check_mode || prog_sram || test_mode)) {
		fprintf(stderr, "%s: option `-b' only valid in programming mode\n", my_name);
		return EXIT_FAILURE;
	}

	if (dont_erase && (read_mode || check_mode || prog_sram || test_mode)) {
		fprintf(stderr, "%s: option `-n' only valid in programming mode\n", my_name);
		return EXIT_FAILURE;
	}

	if (rw_offset != 0 && prog_sram) {
		fprintf(stderr, "%s: option `-o' not supported in SRAM mode\n", my_name);
		return EXIT_FAILURE;
	}

	if (rw_offset != 0 && test_mode) {
		fprintf(stderr, "%s: option `-o' not supported in test mode\n", my_name);
		return EXIT_FAILURE;
	}

	if (optind + 1 == argc) {
		if (test_mode) {
			fprintf(stderr, "%s: test mode doesn't take a file name\n", my_name);
			fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
			return EXIT_FAILURE;
		}
		filename = argv[optind];
	} else if (optind != argc) {
		fprintf(stderr, "%s: too many arguments\n", my_name);
		fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
		return EXIT_FAILURE;
	} else if (bulk_erase || disable_protect) {
		filename = "/dev/null";
	} else if (!test_mode && !erase_mode && !disable_protect) {
		fprintf(stderr, "%s: missing argument\n", my_name);
		fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
		return EXIT_FAILURE;
	}

	/* open input/output file in advance
	   so we can fail before initializing the hardware */

	FILE *f = NULL;
	long file_size = -1;

	if (test_mode) {
		/* nop */;
	} else if (erase_mode) {
		file_size = erase_size;
	} else if (read_mode) {
		f = (strcmp(filename, "-") == 0) ? stdout : fopen(filename, "wb");
		if (f == NULL) {
			fprintf(stderr, "%s: can't open '%s' for writing: ", my_name, filename);
			perror(0);
			return EXIT_FAILURE;
		}
	} else {
		f = (strcmp(filename, "-") == 0) ? stdin : fopen(filename, "rb");
		if (f == NULL) {
			fprintf(stderr, "%s: can't open '%s' for reading: ", my_name, filename);
			perror(0);
			return EXIT_FAILURE;
		}

		/* For regular programming, we need to read the file
		   twice--once for programming and once for verifying--and
		   need to know the file size in advance in order to erase
		   the correct amount of memory.

		   See if we can seek on the input file.  Checking for "-"
		   as an argument isn't enough as we might be reading from a
		   named pipe, or contrarily, the standard input may be an
		   ordinary file. */

		if (!prog_sram && !check_mode) {
			if (fseek(f, 0L, SEEK_END) != -1) {
				file_size = ftell(f);
				if (file_size == -1) {
					fprintf(stderr, "%s: %s: ftell: ", my_name, filename);
					perror(0);
					return EXIT_FAILURE;
				}
				if (fseek(f, 0L, SEEK_SET) == -1) {
					fprintf(stderr, "%s: %s: fseek: ", my_name, filename);
					perror(0);
					return EXIT_FAILURE;
				}
			} else {
				FILE *pipe = f;

				f = tmpfile();
				if (f == NULL) {
					fprintf(stderr, "%s: can't open temporary file\n", my_name);
					return EXIT_FAILURE;
				}
				file_size = 0;

				while (true) {
					static unsigned char buffer[4096];
					size_t rc = fread(buffer, 1, 4096, pipe);
					if (rc <= 0)
						break;
					size_t wc = fwrite(buffer, 1, rc, f);
					if (wc != rc) {
						fprintf(stderr, "%s: can't write to temporary file\n", my_name);
						return EXIT_FAILURE;
					}
					file_size += rc;
				}
				fclose(pipe);

				/* now seek to the beginning so we can
				   start reading again */
				fseek(f, 0, SEEK_SET);
			}
		}
	}

	// ---------------------------------------------------------
	// Initialize USB connection to FT2232H
	// ---------------------------------------------------------

	fprintf(stderr, "init..\n");

	ftdi_init(&ftdic);
	ftdi_set_interface(&ftdic, ifnum);

	if (devstr != NULL) {
		if (ftdi_usb_open_string(&ftdic, devstr)) {
			fprintf(stderr, "Can't find iCE FTDI USB device (device string %s).\n", devstr);
			error(2);
		}
	} else {
		if (ftdi_usb_open(&ftdic, 0x0403, 0x6010) && ftdi_usb_open(&ftdic, 0x0403, 0x6014)) {
			fprintf(stderr, "Can't find iCE FTDI USB device (vendor_id 0x0403, device_id 0x6010 or 0x6014).\n");
			error(2);
		}
	}

	ftdic_open = true;

	if (ftdi_usb_reset(&ftdic)) {
		fprintf(stderr, "Failed to reset iCE FTDI USB device.\n");
		error(2);
	}

	if (ftdi_usb_purge_buffers(&ftdic)) {
		fprintf(stderr, "Failed to purge buffers on iCE FTDI USB device.\n");
		error(2);
	}

	if (ftdi_get_latency_timer(&ftdic, &ftdi_latency) < 0) {
		fprintf(stderr, "Failed to get latency timer (%s).\n", ftdi_get_error_string(&ftdic));
		error(2);
	}

	/* 1 is the fastest polling, it means 1 kHz polling */
	if (ftdi_set_latency_timer(&ftdic, 1) < 0) {
		fprintf(stderr, "Failed to set latency timer (%s).\n", ftdi_get_error_string(&ftdic));
		error(2);
	}

	ftdic_latency_set = true;

	/* Enter MPSSE (Multi-Protocol Synchronous Serial Engine) mode. Set all pins to output. */
	if (ftdi_set_bitmode(&ftdic, 0xff, BITMODE_MPSSE) < 0) {
		fprintf(stderr, "Failed to set BITMODE_MPSSE on iCE FTDI USB device.\n");
		error(2);
	}

	// enable clock divide by 5
	send_byte(MC_TCK_D5);

	// set 6 MHz clock
	send_byte(MC_SET_CLK_DIV);
	send_byte(0x00);
	send_byte(0x00);

	fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

	set_gpio(1, 1);
	usleep(100000);


	if (test_mode)
	{
		fprintf(stderr, "reset..\n");

		set_gpio(1, 0);
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

		flash_power_up();

		flash_read_id();

		flash_power_down();

		set_gpio(1, 1);
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}
	else if (prog_sram)
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		fprintf(stderr, "reset..\n");

		set_gpio(0, 0);
		usleep(100);

		set_gpio(0, 1);
		usleep(2000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");


		// ---------------------------------------------------------
		// Program
		// ---------------------------------------------------------

		fprintf(stderr, "programming..\n");
		while (1) {
			static unsigned char buffer[4096];
			int rc = fread(buffer, 1, 4096, f);
			if (rc <= 0)
				break;
			if (verbose)
				fprintf(stderr, "sending %d bytes.\n", rc);
			send_spi(buffer, rc);
		}

		// add 48 dummy bits (aka 6 bytes)
		send_byte(MC_CLK_N8);
		send_byte(0x05);
		send_byte(0x00);

		// add 1 more dummy bit
		send_byte(MC_CLK_N);
		send_byte(0x00);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}
	else
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		fprintf(stderr, "reset..\n");

		set_gpio(1, 0);
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

		flash_power_up();

		flash_read_id();


		// ---------------------------------------------------------
		// Program
		// ---------------------------------------------------------

		if (!read_mode && !check_mode)
		{
			if (disable_protect)
			{
				flash_write_enable();
				flash_disable_protection();
			}
			
			if (!dont_erase)
			{
				if (bulk_erase)
				{
					flash_write_enable();
					flash_bulk_erase();
					flash_wait();
				}
				else
				{
					fprintf(stderr, "file size: %ld\n", file_size);

					int begin_addr = rw_offset & ~0xffff;
					int end_addr = (rw_offset + file_size + 0xffff) & ~0xffff;

					for (int addr = begin_addr; addr < end_addr; addr += 0x10000) {
						flash_write_enable();
						flash_64kB_sector_erase(addr);
						flash_wait();
					}
				}
			}

			if (!erase_mode)
			{
				fprintf(stderr, "programming..\n");

				for (int rc, addr = 0; true; addr += rc) {
					uint8_t buffer[256];
					int page_size = 256 - (rw_offset + addr) % 256;
					rc = fread(buffer, 1, page_size, f);
					if (rc <= 0)
						break;
					flash_write_enable();
					flash_prog(rw_offset + addr, buffer, rc);
					flash_wait();
				}

				/* seek to the beginning for second pass */
				fseek(f, 0, SEEK_SET);
			}
		}

		// ---------------------------------------------------------
		// Read/Verify
		// ---------------------------------------------------------

		if (read_mode) {
			fprintf(stderr, "reading..\n");
			for (int addr = 0; addr < read_size; addr += 256) {
				uint8_t buffer[256];
				flash_read(rw_offset + addr, buffer, 256);
				fwrite(buffer, read_size - addr > 256 ? 256 : read_size - addr, 1, f);
			}
		} else if (!erase_mode) {
			fprintf(stderr, "reading..\n");
			for (int addr = 0; true; addr += 256) {
				uint8_t buffer_flash[256], buffer_file[256];
				int rc = fread(buffer_file, 1, 256, f);
				if (rc <= 0)
					break;
				flash_read(rw_offset + addr, buffer_flash, rc);
				if (memcmp(buffer_file, buffer_flash, rc)) {
					fprintf(stderr, "Found difference between flash and file!\n");
					error(3);
				}
			}

			fprintf(stderr, "VERIFY OK\n");
		}


		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		flash_power_down();

		set_gpio(1, 1);
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}

	if (f != NULL && f != stdin && f != stdout)
		fclose(f);

	// ---------------------------------------------------------
	// Exit
	// ---------------------------------------------------------

	fprintf(stderr, "Bye.\n");
	ftdi_set_latency_timer(&ftdic, ftdi_latency);
	ftdi_disable_bitbang(&ftdic);
	ftdi_usb_close(&ftdic);
	ftdi_deinit(&ftdic);
	return 0;
}
