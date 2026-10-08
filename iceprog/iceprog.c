/*
 *  iceprog -- simple programming tool for FTDI-based Lattice iCE programmers
 *
 *  Copyright (C) 2015  Claire Xenia Wolf <claire@clairexen.net>
 *  Copyright (C) 2018  Piotr Esden-Tempski <piotr@esden.net>
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
 */

#define _GNU_SOURCE

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

#ifdef _WIN32
#include <io.h> /* _setmode() */
#include <fcntl.h> /* _O_BINARY */
#endif

#include "mpsse.h"

static bool verbose = false;

// ---------------------------------------------------------
// FLASH definitions
// ---------------------------------------------------------

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
	FC_RPR = 0x3C, /* Read Sector Protection Registers (adesto) */
	FC_IBL = 0x36, /* Individual Block Lock */
	FC_IBU = 0x39, /* Individual Block Unlock */
	FC_EPS = 0x75, /* Erase / Program Suspend */
	FC_EPR = 0x7A, /* Erase / Program Resume */
	FC_PD = 0xB9, /* Power-down */
	FC_QPI = 0x38, /* Enter QPI mode */
	FC_ERESET = 0x66, /* Enable Reset */
	FC_RESET = 0x99, /* Reset Device */
};

// ---------------------------------------------------------
// Hardware specific CS, CReset, CDone functions
// ---------------------------------------------------------

static void set_cs_creset(int cs_b, int creset_b)
{
	uint8_t gpio = 0;
	uint8_t direction = 0x03;

	if (!cs_b) {
		// ADBUS4 (GPIOL0)
		direction |= 0x10;
	}

	if (!creset_b) {
		// ADBUS7 (GPIOL3)
		direction |= 0x80;
	}

	mpsse_set_gpio(gpio, direction);
}

static bool get_cdone(void)
{
	// ADBUS6 (GPIOL2)
	return (mpsse_readb_low() & 0x40) != 0;
}

// ---------------------------------------------------------
// FLASH function implementations
// ---------------------------------------------------------

// the FPGA reset is released so also FLASH chip select should be deasserted
static void flash_release_reset()
{
	set_cs_creset(1, 1);
}

// FLASH chip select assert
// should only happen while FPGA reset is asserted
static void flash_chip_select()
{
	set_cs_creset(0, 0);
}

// FLASH chip select deassert
static void flash_chip_deselect()
{
	set_cs_creset(1, 0);
}

// SRAM reset is the same as flash_chip_select()
// For ease of code reading we use this function instead
static void sram_reset()
{
	// Asserting chip select and reset lines
	set_cs_creset(0, 0);
}

// SRAM chip select assert
// When accessing FPGA SRAM the reset should be released
static void sram_chip_select()
{
	set_cs_creset(0, 1);
}

static void flash_read_id()
{
	/* JEDEC ID structure:
	 * Byte No. | Data Type
	 * ---------+----------
	 *        0 | FC_JEDECID Request Command
	 *        1 | MFG ID
	 *        2 | Dev ID 1
	 *        3 | Dev ID 2
	 *        4 | Ext Dev Str Len
	 */

	uint8_t data[260] = { FC_JEDECID };
	int len = 5; // command + 4 response bytes

	if (verbose)
		fprintf(stderr, "read flash ID..\n");

	flash_chip_select();

	// Write command and read first 4 bytes
	mpsse_xfer_spi(data, len);

	if (data[4] == 0xFF)
		fprintf(stderr, "Extended Device String Length is 0xFF, "
				"this is likely a read error. Ignoring...\n");
	else {
		// Read extended JEDEC ID bytes
		if (data[4] != 0) {
			len += data[4];
			mpsse_xfer_spi(data + 5, len - 5);
		}
	}

	flash_chip_deselect();

	// TODO: Add full decode of the JEDEC ID.
	fprintf(stderr, "flash ID:");
	for (int i = 1; i < len; i++)
		fprintf(stderr, " 0x%02X", data[i]);
	fprintf(stderr, "\n");
}

static void flash_reset()
{
	uint8_t data[8] = { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff };

	// This disables CRM is if it was enabled
	flash_chip_select();
	mpsse_xfer_spi(data, 8);
	flash_chip_deselect();

	// This disables QPI if it was enable
	flash_chip_select();
	mpsse_xfer_spi_bits(0xFF, 2);
	flash_chip_deselect();
}

static void flash_power_up()
{
	uint8_t data_rpd[1] = { FC_RPD };
	flash_chip_select();
	mpsse_xfer_spi(data_rpd, 1);
	flash_chip_deselect();
}

static void flash_power_down()
{
	uint8_t data[1] = { FC_PD };
	flash_chip_select();
	mpsse_xfer_spi(data, 1);
	flash_chip_deselect();
}

static uint8_t flash_read_status()
{
	uint8_t data[2] = { FC_RSR1 };

	flash_chip_select();
	mpsse_xfer_spi(data, 2);
	flash_chip_deselect();

	if (verbose) {
		fprintf(stderr, "SR1: 0x%02X\n", data[1]);
		fprintf(stderr, " - SPRL: %s\n",
			((data[1] & (1 << 7)) == 0) ? 
				"unlocked" : 
				"locked");
		fprintf(stderr, " -  SPM: %s\n",
			((data[1] & (1 << 6)) == 0) ?
				"Byte/Page Prog Mode" :
				"Sequential Prog Mode");
		fprintf(stderr, " -  EPE: %s\n",
			((data[1] & (1 << 5)) == 0) ?
				"Erase/Prog success" :
				"Erase/Prog error");
		fprintf(stderr, "-  SPM: %s\n",
			((data[1] & (1 << 4)) == 0) ?
				"~WP asserted" :
				"~WP deasserted");
		fprintf(stderr, " -  SWP: ");
		switch((data[1] >> 2) & 0x3) {
			case 0:
				fprintf(stderr, "All sectors unprotected\n");
				break;
			case 1:
				fprintf(stderr, "Some sectors protected\n");
				break;
			case 2:
				fprintf(stderr, "Reserved (xxxx 10xx)\n");
				break;
			case 3:
				fprintf(stderr, "All sectors protected\n");
				break;
		}
		fprintf(stderr, " -  WEL: %s\n",
			((data[1] & (1 << 1)) == 0) ?
				"Not write enabled" :
				"Write enabled");
		fprintf(stderr, " - ~RDY: %s\n",
			((data[1] & (1 << 0)) == 0) ?
				"Ready" :
				"Busy");
	}

	usleep(1000);

	return data[1];
}

static void flash_write_enable()
{
	if (verbose) {
		fprintf(stderr, "status before enable:\n");
		flash_read_status();
	}

	if (verbose)
		fprintf(stderr, "write enable..\n");

	uint8_t data[1] = { FC_WE };
	flash_chip_select();
	mpsse_xfer_spi(data, 1);
	flash_chip_deselect();

	if (verbose) {
		fprintf(stderr, "status after enable:\n");
		flash_read_status();
	}
}

static void flash_bulk_erase()
{
	fprintf(stderr, "bulk erase..\n");

	uint8_t data[1] = { FC_CE };
	flash_chip_select();
	mpsse_xfer_spi(data, 1);
	flash_chip_deselect();
}

static void flash_4kB_sector_erase(int addr)
{
	fprintf(stderr, "erase 4kB sector at 0x%06X..\n", addr);

	uint8_t command[4] = { FC_SE, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	flash_chip_select();
	mpsse_send_spi(command, 4);
	flash_chip_deselect();
}

static void flash_32kB_sector_erase(int addr)
{
	fprintf(stderr, "erase 64kB sector at 0x%06X..\n", addr);

	uint8_t command[4] = { FC_BE32, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	flash_chip_select();
	mpsse_send_spi(command, 4);
	flash_chip_deselect();
}

static void flash_64kB_sector_erase(int addr)
{
	fprintf(stderr, "erase 64kB sector at 0x%06X..\n", addr);

	uint8_t command[4] = { FC_BE64, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	flash_chip_select();
	mpsse_send_spi(command, 4);
	flash_chip_deselect();
}

static void flash_prog(int addr, uint8_t *data, int n)
{
	if (verbose)
		fprintf(stderr, "prog 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { FC_PP, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	flash_chip_select();
	mpsse_send_spi(command, 4);
	mpsse_send_spi(data, n);
	flash_chip_deselect();

	if (verbose)
		for (int i = 0; i < n; i++)
			fprintf(stderr, "%02x%c", data[i], i == n - 1 || i % 32 == 31 ? '\n' : ' ');
}

static void flash_read(int addr, uint8_t *data, int n)
{
	if (verbose)
		fprintf(stderr, "read 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { FC_RD, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	flash_chip_select();
	mpsse_send_spi(command, 4);
	memset(data, 0, n);
	mpsse_xfer_spi(data, n);
	flash_chip_deselect();

	if (verbose)
		for (int i = 0; i < n; i++)
			fprintf(stderr, "%02x%c", data[i], i == n - 1 || i % 32 == 31 ? '\n' : ' ');
}

static void flash_wait()
{
	if (verbose)
		fprintf(stderr, "waiting..");

	int count = 0;
	while (1)
	{
		uint8_t data[2] = { FC_RSR1 };

		flash_chip_select();
		mpsse_xfer_spi(data, 2);
		flash_chip_deselect();

		if ((data[1] & 0x01) == 0) {
			if (count < 2) {
				count++;
				if (verbose) {
					fprintf(stderr, "r");
					fflush(stderr);
				}
			} else {
				if (verbose) {
					fprintf(stderr, "R");
					fflush(stderr);
				}
				break;
			}
		} else {
			if (verbose) {
				fprintf(stderr, ".");
				fflush(stderr);
			}
			count = 0;
		}

		usleep(1000);
	}

	if (verbose)
		fprintf(stderr, "\n");

}

static void flash_disable_protection()
{
	fprintf(stderr, "disable flash protection...\n");

	// Write Status Register 1 <- 0x00
	uint8_t data[2] = { FC_WSR1, 0x00 };
	flash_chip_select();
	mpsse_xfer_spi(data, 2);
	flash_chip_deselect();
	
	flash_wait();
	
	// Read Status Register 1
	data[0] = FC_RSR1;

	flash_chip_select();
	mpsse_xfer_spi(data, 2);
	flash_chip_deselect();

	if (data[1] != 0x00)
		fprintf(stderr, "failed to disable protection, SR now equal to 0x%02x (expected 0x00)\n", data[1]);

}

static void flash_enable_quad()
{
	fprintf(stderr, "Enabling Quad operation...\n");

	// Allow write
	flash_write_enable();

	// Write Status Register 2 <- 0x02
	uint8_t data[2] = { FC_WSR2, 0x02 };
	flash_chip_select();
	mpsse_xfer_spi(data, 2);
	flash_chip_deselect();

	flash_wait();

	// Read Status Register 1
	data[0] = FC_RSR2;

	flash_chip_select();
	mpsse_xfer_spi(data, 2);
	flash_chip_deselect();

	if ((data[1] & 0x02) != 0x02)
		fprintf(stderr, "failed to set QE=1, SR2 now equal to 0x%02x (expected 0x%02x)\n", data[1], data[1] | 0x02);

	fprintf(stderr, "SR2: %08x\n", data[1]);
}

// ---------------------------------------------------------
// iceprog implementation
// ---------------------------------------------------------

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
	fprintf(stderr, "  -s                    slow SPI (50 kHz instead of 6 MHz)\n");
	fprintf(stderr, "  -k                    keep flash in powered up state (i.e. skip power down command)\n");
	fprintf(stderr, "  -v                    verbose output\n");
	fprintf(stderr, "  -i [4,32,64]          select erase block size [default: 64k]\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Mode of operation:\n");
	fprintf(stderr, "  [default]             write file contents to flash, then verify\n");
	fprintf(stderr, "  -X                    write file contents to flash only\n");	
	fprintf(stderr, "  -r                    read first 256 kB from flash and write to file\n");
	fprintf(stderr, "  -R <size in bytes>    read the specified number of bytes from flash\n");
	fprintf(stderr, "                          (append 'k' to the argument for size in kilobytes,\n");
	fprintf(stderr, "                          or 'M' for size in megabytes)\n");
	fprintf(stderr, "  -c                    do not write flash, only verify (`check')\n");
	fprintf(stderr, "  -S                    perform SRAM programming\n");
	fprintf(stderr, "  -t                    just read the flash ID sequence\n");
	fprintf(stderr, "  -Q                    just set the flash QE=1 bit\n");
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
	fprintf(stderr, "  https://github.com/yosyshq/icestorm/blob/master/docs/source/_static/images/icestick.jpg\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Notes for the iCE40-HX8K Breakout Board:\n");
	fprintf(stderr, "  Make sure that the jumper settings on the board match the selected\n");
	fprintf(stderr, "  mode (SRAM or FLASH). See the iCE40-HX8K user manual for details.\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "If you have a bug report, please file an issue on github:\n");
	fprintf(stderr, "  https://github.com/YosysHQ/icestorm/issues\n");
}

int main(int argc, char **argv)
{
	/* used for error reporting */
	const char *my_name = argv[0];
	for (size_t i = 0; argv[0][i]; i++)
		if (argv[0][i] == '/')
			my_name = argv[0] + i + 1;

	int read_size = 256 * 1024;
	int erase_block_size = 64;
	int erase_size = 0;
	int rw_offset = 0;

	bool read_mode = false;
	bool check_mode = false;
	bool erase_mode = false;
	bool bulk_erase = false;
	bool dont_erase = false;
	bool prog_sram = false;
	int  test_mode = 0;
	bool slow_clock = false;
	bool disable_protect = false;
	bool disable_verify = false;
	bool disable_powerdown = false;
	const char *filename = NULL;
	const char *devstr = NULL;
	int ifnum = 0;

#ifdef _WIN32
	_setmode(_fileno(stdin), _O_BINARY);
	_setmode(_fileno(stdout), _O_BINARY);
#endif

	static struct option long_options[] = {
		{"help", no_argument, NULL, -2},
		{NULL, 0, NULL, 0}
	};

	/* Decode command line parameters */
	int opt;
	char *endptr;
	while ((opt = getopt_long(argc, argv, "d:i:I:rR:e:o:cbnStQvspXk", long_options, NULL)) != -1) {
		switch (opt) {
		case 'd': /* device string */
			devstr = optarg;
			break;
		case 'i': /* block erase size */
			if (!strcmp(optarg, "4"))
				erase_block_size = 4;
			else if (!strcmp(optarg, "32"))
				erase_block_size = 32;
			else if (!strcmp(optarg, "64"))
				erase_block_size = 64;
			else {
				fprintf(stderr, "%s: `%s' is not a valid erase block size (must be `4', `32' or `64')\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'I': /* FTDI Chip interface select */
			if (!strcmp(optarg, "A"))
				ifnum = 0;
			else if (!strcmp(optarg, "B"))
				ifnum = 1;
			else if (!strcmp(optarg, "C"))
				ifnum = 2;
			else if (!strcmp(optarg, "D"))
				ifnum = 3;
			else {
				fprintf(stderr, "%s: `%s' is not a valid interface (must be `A', `B', `C', or `D')\n", my_name, optarg);
				return EXIT_FAILURE;
			}
			break;
		case 'r': /* Read 256 bytes to file */
			read_mode = true;
			break;
		case 'R': /* Read n bytes to file */
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
		case 'e': /* Erase blocks as if we were writing n bytes */
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
		case 'o': /* set address offset */
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
		case 'c': /* do not write just check */
			check_mode = true;
			break;
		case 'b': /* bulk erase before writing */
			bulk_erase = true;
			break;
		case 'n': /* do not erase before writing */
			dont_erase = true;
			break;
		case 'S': /* write to sram directly */
			prog_sram = true;
			break;
		case 't': /* just read flash id */
			test_mode = 1;
			break;
		case 'Q': /* just read flash id */
			test_mode = 2;
			break;
		case 'v': /* provide verbose output */
			verbose = true;
			break;
		case 's': /* use slow SPI clock */
			slow_clock = true;
			break;
		case 'p': /* disable flash protect before erase/write */
			disable_protect = true;
			break;
		case 'X': /* disable verification */
			disable_verify = true;
			break;
		case 'k': /* disable power down command */
			disable_powerdown = true;
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

	/* Make sure that the combination of provided parameters makes sense */

	if (read_mode + erase_mode + check_mode + prog_sram + !!test_mode > 1) {
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

	mpsse_init(ifnum, devstr, slow_clock);

	fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

	flash_release_reset();
	usleep(100000);

	if (test_mode)
	{
		fprintf(stderr, "reset..\n");

		flash_chip_deselect();
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

		flash_reset();
		flash_power_up();

		if (test_mode == 1)
			flash_read_id();
		else
			flash_enable_quad();

		flash_power_down();

		flash_release_reset();
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}
	else if (prog_sram)
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		fprintf(stderr, "reset..\n");

		sram_reset();
		usleep(100);

		sram_chip_select();
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
			mpsse_send_spi(buffer, rc);
		}

		mpsse_send_dummy_bytes(6);
		mpsse_send_dummy_bit();

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}
	else /* program flash */
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		fprintf(stderr, "reset..\n");

		flash_chip_deselect();
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");

		flash_reset();
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

					int block_size = erase_block_size << 10;
					int block_mask = block_size - 1;
					int begin_addr = rw_offset & ~block_mask;
					int end_addr = (rw_offset + file_size + block_mask) & ~block_mask;

					for (int addr = begin_addr; addr < end_addr; addr += block_size) {
						flash_write_enable();
						switch(erase_block_size) {
							case 4:
								flash_4kB_sector_erase(addr);
								break;
							case 32:
								flash_32kB_sector_erase(addr);
								break;
							case 64:
								flash_64kB_sector_erase(addr);
								break;
						}
						if (verbose) {
							fprintf(stderr, "Status after block erase:\n");
							flash_read_status();
						}
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
					fprintf(stderr, "                      \r");
					fprintf(stderr, "addr 0x%06X %3ld%%\r", rw_offset + addr, 100 * addr / file_size);
					fflush(stderr);
					flash_write_enable();
					flash_prog(rw_offset + addr, buffer, rc);
					flash_wait();
				}
				fprintf(stderr, "                      \r");
				fprintf(stderr, "done.\n");

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
				fprintf(stderr, "                      \r");
				fprintf(stderr, "addr 0x%06X %3d%%\r", rw_offset + addr, 100 * addr / read_size);
				fflush(stderr);
				flash_read(rw_offset + addr, buffer, 256);
				fwrite(buffer, read_size - addr > 256 ? 256 : read_size - addr, 1, f);
			}
			fprintf(stderr, "                      \r");
			fprintf(stderr, "done.\n");
		} else if (!erase_mode && !disable_verify) {
			fprintf(stderr, "reading..\n");
			for (int addr = 0; true; addr += 256) {
				uint8_t buffer_flash[256], buffer_file[256];
				int rc = fread(buffer_file, 1, 256, f);
				if (rc <= 0)
					break;
				fprintf(stderr, "                      \r");
				fprintf(stderr, "addr 0x%06X %3ld%%\r", rw_offset + addr, 100 * addr / file_size);
				fflush(stderr);
				flash_read(rw_offset + addr, buffer_flash, rc);
				if (memcmp(buffer_file, buffer_flash, rc)) {
					fprintf(stderr, "Found difference between flash and file!\n");
					if (!disable_powerdown)
					  flash_power_down();
					flash_release_reset();
					usleep(250000);
					mpsse_error(3);
				}
			}

			fprintf(stderr, "                      \r");
			fprintf(stderr, "VERIFY OK\n");
		}


		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		if (!disable_powerdown)
			flash_power_down();

		flash_release_reset();
		usleep(250000);

		fprintf(stderr, "cdone: %s\n", get_cdone() ? "high" : "low");
	}

	if (f != NULL && f != stdin && f != stdout)
		fclose(f);

	// ---------------------------------------------------------
	// Exit
	// ---------------------------------------------------------

	fprintf(stderr, "Bye.\n");
	mpsse_close();
	return 0;
}
