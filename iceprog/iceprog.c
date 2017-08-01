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

	send_byte(0x11);
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

	send_byte(0x31);
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

	send_byte(0x80);
	send_byte(gpio);
	send_byte(0x93);
}

static int get_cdone()
{
	uint8_t data;
	send_byte(0x81);
	data = recv_byte();
	// ADBUS6 (GPIOL2)
	return (data & 0x40) != 0;
}

static void flash_read_id()
{
	// fprintf(stderr, "read flash ID..\n");

	uint8_t data[21] = { 0x9F };
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
	uint8_t data[1] = { 0xAB };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_power_down()
{
	uint8_t data[1] = { 0xB9 };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_write_enable()
{
	if (verbose)
		fprintf(stderr, "write enable..\n");

	uint8_t data[1] = { 0x06 };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_bulk_erase()
{
	fprintf(stderr, "bulk erase..\n");

	uint8_t data[1] = { 0xc7 };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

static void flash_64kB_sector_erase(int addr)
{
	fprintf(stderr, "erase 64kB sector at 0x%06X..\n", addr);

	uint8_t command[4] = { 0xd8, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

	set_gpio(0, 0);
	send_spi(command, 4);
	set_gpio(1, 0);
}

static void flash_prog(int addr, uint8_t *data, int n)
{
	if (verbose)
		fprintf(stderr, "prog 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { 0x02, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

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

	uint8_t command[4] = { 0x03, (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr };

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
		uint8_t data[2] = { 0x05 };

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

static void help(const char *progname)
{
	fprintf(stderr, "Simple programming tool for FTDI-based Lattice iCE programmers.\n");
	fprintf(stderr, "Usage: %s [-b|-n|-c] <input file>\n", progname);
	fprintf(stderr, "       %s -r|-R<bytes> <output file>\n", progname);
	fprintf(stderr, "       %s -S <input file>\n", progname);
	fprintf(stderr, "       %s -t\n", progname);
	fprintf(stderr, "\n");
	fprintf(stderr, "General options:\n");
	fprintf(stderr, "  -d <device string>    use the specified USB device [default: i:0x0403:0x6010]\n");
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
	fprintf(stderr, "  -n                    do not erase flash before writing\n");
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
	int rw_offset = 0;

	bool read_mode = false;
	bool check_mode = false;
	bool bulk_erase = false;
	bool dont_erase = false;
	bool prog_sram = false;
	bool test_mode = false;
	const char *filename = NULL;
	const char *devstr = NULL;
	enum ftdi_interface ifnum = INTERFACE_A;

	static struct option long_options[] = {
		{"help", no_argument, NULL, -2},
		{NULL, 0, NULL, 0}
	};

	int opt;
	char *endptr;
	while ((opt = getopt_long(argc, argv, "d:I:rR:o:cbnStv", long_options, NULL)) != -1) {
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
		case -2:
			help(argv[0]);
			return EXIT_SUCCESS;
		default:
			/* error message has already been printed */
			fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
			return EXIT_FAILURE;
		}
	}

	if (read_mode + check_mode + prog_sram + test_mode > 1) {
		fprintf(stderr, "%s: options `-r'/`-R', `-c', `-S', and `-t' are mutually exclusive\n", my_name);
		return EXIT_FAILURE;
	}

	if (bulk_erase && dont_erase) {
		fprintf(stderr, "%s: options `-b' and `-n' are mutually exclusive\n", my_name);
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
	} else if (bulk_erase) {
		filename = "/dev/null";
	} else if (!test_mode) {
		fprintf(stderr, "%s: missing argument\n", my_name);
		fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
		return EXIT_FAILURE;
	}

	/* open input/output file in advance
	   so we can fail before initializing the hardware */

	FILE *f = NULL;
	long file_size = -1;

	if (test_mode)
		/* nop */;
	else if (read_mode) {
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
		if (ftdi_usb_open(&ftdic, 0x0403, 0x6010)) {
			fprintf(stderr, "Can't find iCE FTDI USB device (vendor_id 0x0403, device_id 0x6010).\n");
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

	if (ftdi_set_bitmode(&ftdic, 0xff, BITMODE_MPSSE) < 0) {
		fprintf(stderr, "Failed to set BITMODE_MPSSE on iCE FTDI USB device.\n");
		error(2);
	}

	// enable clock divide by 5
	send_byte(0x8b);

	// set 6 MHz clock
	send_byte(0x86);
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

		// add 48 dummy bits
		send_byte(0x8f);
		send_byte(0x05);
		send_byte(0x00);

		// add 1 more dummy bit
		send_byte(0x8e);
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
		} else {
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
