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
#include <unistd.h>
#include <string.h>
#include <errno.h>

struct ftdi_context ftdic;
bool ftdic_open = false;
bool verbose = false;

void check_rx()
{
	while (1) {
		uint8_t data;
		int rc = ftdi_read_data(&ftdic, &data, 1);
		if (rc <= 0) break;
		printf("unexpected rx byte: %02X\n", data);
	}
}

void error()
{
	check_rx();
	printf("ABORT.\n");
	if (ftdic_open)
		ftdi_usb_close(&ftdic);
	ftdi_deinit(&ftdic);
	exit(1);
}

uint8_t recv_byte()
{
	uint8_t data;
	while (1) {
		int rc = ftdi_read_data(&ftdic, &data, 1);
		if (rc < 0) {
			printf("Read error.\n");
			error();
		}
		if (rc == 1)
			break;
		usleep(100);
	}
	return data;
}

void send_byte(uint8_t data)
{
	int rc = ftdi_write_data(&ftdic, &data, 1);
	if (rc != 1) {
		printf("Write error (single byte, rc=%d, expected %d).\n", rc, 1);
		error();
	}
}

void send_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	send_byte(0x11);
	send_byte(n-1);
	send_byte((n-1) >> 8);

	int rc = ftdi_write_data(&ftdic, data, n);
	if (rc != n) {
		printf("Write error (chunk, rc=%d, expected %d).\n", rc, n);
		error();
	}
}

void xfer_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	send_byte(0x31);
	send_byte(n-1);
	send_byte((n-1) >> 8);

	int rc = ftdi_write_data(&ftdic, data, n);
	if (rc != n) {
		printf("Write error (chunk, rc=%d, expected %d).\n", rc, n);
		error();
	}

	for (int i = 0; i < n; i++)
		data[i] = recv_byte();
}

void set_gpio(int slavesel_b, int creset_b)
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

int get_cdone()
{
	uint8_t data;
	send_byte(0x81);
	data = recv_byte();
	// ADBUS6 (GPIOL2)
	return (data & 0x40) != 0;
}

void flash_read_id()
{
	// printf("read flash ID..\n");

	uint8_t data[21] = { 0x9E };
	set_gpio(0, 0);
	xfer_spi(data, 21);
	set_gpio(1, 0);

	printf("flash ID:");
	for (int i = 1; i < 21; i++)
		printf(" 0x%02X", data[i]);
	printf("\n");
}

void flash_write_enable()
{
	if (verbose)
		printf("write enable..\n");

	uint8_t data[1] = { 0x06 };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

void flash_bulk_erase()
{
	printf("bulk erase..\n");

	uint8_t data[1] = { 0xc7 };
	set_gpio(0, 0);
	xfer_spi(data, 1);
	set_gpio(1, 0);
}

void flash_sector_erase(int addr)
{
	printf("sector erase 0x%06X..\n", addr);

	uint8_t command[4] = { 0xd8, addr >> 16, addr >> 8, addr };
	set_gpio(0, 0);
	send_spi(command, 4);
	set_gpio(1, 0);
}

void flash_prog(int addr, uint8_t *data, int n)
{
	if (verbose)
		printf("prog 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { 0x02, addr >> 16, addr >> 8, addr };
	set_gpio(0, 0);
	send_spi(command, 4);
	send_spi(data, n);
	set_gpio(1, 0);

	if (verbose)
		for (int i = 0; i < n; i++)
			printf("%02x%c", data[i], i == n-1 || i % 32 == 31 ? '\n' : ' ');
}

void flash_read(int addr, uint8_t *data, int n)
{
	if (verbose)
		printf("read 0x%06X +0x%03X..\n", addr, n);

	uint8_t command[4] = { 0x03, addr >> 16, addr >> 8, addr };
	set_gpio(0, 0);
	send_spi(command, 4);
	memset(data, 0, n);
	xfer_spi(data, n);
	set_gpio(1, 0);

	if (verbose)
		for (int i = 0; i < n; i++)
			printf("%02x%c", data[i], i == n-1 || i % 32 == 31 ? '\n' : ' ');
}

void flash_wait()
{
	if (verbose)
		printf("waiting..");

	while (1)
	{
		uint8_t data[2] = { 0x05 };

		set_gpio(0, 0);
		xfer_spi(data, 2);
		set_gpio(1, 0);

		if ((data[1] & 0x01) == 0)
			break;

		if (verbose) {
			printf(".");
			fflush(stdout);
		}
		usleep(250000);
	}

	if (verbose)
		printf("\n");
}

void help(const char *progname)
{
	fprintf(stderr, "\n");
	fprintf(stderr, "iceprog -- simple programming tool for FTDI-based Lattice iCE programmers\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Notes for iCEstick (iCE40HX-1k devel board):\n");
	fprintf(stderr, "  An unmodified iCEstick can only be programmed via the serial flash.\n");
	fprintf(stderr, "  Direct programming of the SRAM is not supported. For direct SRAM\n");
	fprintf(stderr, "  programming the flash chip and one zero ohm resistor must be desoldered\n");
	fprintf(stderr, "  and the FT2232H SI pin must be connected to the iCE SPI_SI pin, as shown\n");
	fprintf(stderr, "  in this picture: http://www.clifford.at/gallery/2014-elektronik/IMG_20141115_183838\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Notes for the iCE40-HX8K Breakout Board:\n");
	fprintf(stderr, "  Make sure that the jumper settings on the board match the selected\n");
	fprintf(stderr, "  mode (SRAM or FLASH). See the iCE40-HX8K user manual for details.\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Usage: %s [options] <filename>\n", progname);
	fprintf(stderr, "\n");
	fprintf(stderr, "    -d <device-string>\n");
	fprintf(stderr, "        use the specified USB device:\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "            d:<devicenode>                (e.g. d:002/005)\n");
	fprintf(stderr, "            i:<vendor>:<product>          (e.g. i:0x0403:0x6010)\n");
	fprintf(stderr, "            i:<vendor>:<product>:<index>  (e.g. i:0x0403:0x6010:0)\n");
	fprintf(stderr, "            s:<vendor>:<product>:<serial-string>\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -r\n");
	fprintf(stderr, "        read entire flash (32Mb / 4MB) and write to file\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -R\n");
	fprintf(stderr, "        read first 256 kB from flash and write to file\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -c\n");
	fprintf(stderr, "        do not write flash, only verify (check)\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -b\n");
	fprintf(stderr, "        bulk erase entire flash before writing\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -n\n");
	fprintf(stderr, "        do not erase flash before writing\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -S\n");
	fprintf(stderr, "        perform SRAM programming\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "    -v\n");
	fprintf(stderr, "        verbose output\n");
	fprintf(stderr, "\n");
	exit(1);
}

int main(int argc, char **argv)
{
	int max_read_size = 4 * 1024 * 1024;
	bool read_mode = false;
	bool check_mode = false;
	bool bulk_erase = false;
	bool dont_erase = false;
	bool prog_sram = false;
	const char *filename = NULL;
	const char *devstr = NULL;

	int opt;
	while ((opt = getopt(argc, argv, "d:rRcbnSv")) != -1)
	{
		switch (opt)
		{
		case 'd':
			devstr = optarg;
			break;
		case 'r':
			read_mode = true;
			break;
		case 'R':
			read_mode = true;
			max_read_size = 256 * 1024;
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
		case 'v':
			verbose = true;
			break;
		default:
			help(argv[0]);
		}
	}

	if (read_mode && check_mode)
		help(argv[0]);

	if (bulk_erase && dont_erase)
		help(argv[0]);

	if (optind+1 != argc)
		help(argv[0]);

	filename = argv[optind];

	// ---------------------------------------------------------
	// Initialize USB connection to FT2232H
	// ---------------------------------------------------------

	printf("init..\n");

	ftdi_init(&ftdic);
	ftdi_set_interface(&ftdic, INTERFACE_A);

	if (devstr != NULL) {
		if (ftdi_usb_open_string(&ftdic, devstr)) {
			printf("Can't find iCE FTDI USB device (device string %s).\n", devstr);
			error();
		}
	} else {
		if (ftdi_usb_open(&ftdic, 0x0403, 0x6010)) {
			printf("Can't find iCE FTDI USB device (vedor_id 0x0403, device_id 0x6010).\n");
			error();
		}
	}

	ftdic_open = true;

	if (ftdi_usb_reset(&ftdic)) {
		printf("Failed to reset iCE FTDI USB device.\n");
		error();
	}

	if (ftdi_usb_purge_buffers(&ftdic)) {
		printf("Failed to purge buffers on iCE FTDI USB device.\n");
		error();
	}

	if (ftdi_set_bitmode(&ftdic, 0xff, BITMODE_MPSSE) < 0) {
		printf("Failed set BITMODE_MPSSE on iCE FTDI USB device.\n");
		error();
	}

	// enable clock divide by 5
	send_byte(0x8b);

	// set 6 MHz clock
	send_byte(0x86);
	send_byte(0x00);
	send_byte(0x00);

	printf("cdone: %s\n", get_cdone() ? "high" : "low");

	set_gpio(1, 1);
	usleep(100000);


	if (prog_sram)
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		printf("reset..\n");

		set_gpio(0, 0);
		usleep(100);

		set_gpio(0, 1);
		usleep(2000);

		printf("cdone: %s\n", get_cdone() ? "high" : "low");


		// ---------------------------------------------------------
		// Program
		// ---------------------------------------------------------

		FILE *f = fopen(filename, "r");
		if (f == NULL) {
			fprintf(stderr, "Error: Can't open '%s' for reading: %s\n", filename, strerror(errno));
			error();
		}

		printf("programming..\n");
		while (1)
		{
			static unsigned char buffer[4096];
			int rc = fread(buffer, 1, 4096, f);
			if (rc <= 0) break;
			if (verbose)
				printf("sending %d bytes.\n", rc);
			send_spi(buffer, rc);
		}

		fclose(f);

		// add 48 dummy bits
		send_byte(0x8f);
		send_byte(0x05);
		send_byte(0x00);

		// add 1 more dummy bit
		send_byte(0x8e);
		send_byte(0x00);

		printf("cdone: %s\n", get_cdone() ? "high" : "low");
	}
	else
	{
		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		printf("reset..\n");

		set_gpio(1, 0);
		usleep(250000);

		printf("cdone: %s\n", get_cdone() ? "high" : "low");

		flash_read_id();


		// ---------------------------------------------------------
		// Program
		// ---------------------------------------------------------

		if (!read_mode && !check_mode)
		{
			FILE *f = fopen(filename, "r");
			if (f == NULL) {
				fprintf(stderr, "Error: Can't open '%s' for reading: %s\n", filename, strerror(errno));
				error();
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
					fseek(f, SEEK_END, 0);
					int file_size = ftell(f);
					rewind(f);

					for (int addr = 0; addr < file_size; addr += 0x1000) {
						flash_write_enable();
						flash_sector_erase(addr);
						flash_wait();
					}
				}
			}

			printf("programming..\n");
			for (int addr = 0; true; addr += 256) {
				uint8_t buffer[256];
				int rc = fread(buffer, 1, 256, f);
				if (rc <= 0) break;
				flash_write_enable();
				flash_prog(addr, buffer, rc);
				flash_wait();
			}

			fclose(f);
		}


		// ---------------------------------------------------------
		// Read/Verify
		// ---------------------------------------------------------

		if (read_mode)
		{
			FILE *f = fopen(filename, "w");
			if (f == NULL) {
				fprintf(stderr, "Error: Can't open '%s' for writing: %s\n", filename, strerror(errno));
				error();
			}

			printf("reading..\n");
			for (int addr = 0; addr < max_read_size; addr += 256) {
				uint8_t buffer[256];
				flash_read(addr, buffer, 256);
				fwrite(buffer, 256, 1, f);
			}

			fclose(f);
		}
		else
		{
			FILE *f = fopen(filename, "r");
			if (f == NULL) {
				fprintf(stderr, "Error: Can't open '%s' for reading: %s\n", filename, strerror(errno));
				error();
			}

			printf("reading..\n");
			for (int addr = 0; true; addr += 256) {
				uint8_t buffer_flash[256], buffer_file[256];
				int rc = fread(buffer_file, 1, 256, f);
				if (rc <= 0) break;
				flash_read(addr, buffer_flash, 256);
				if (memcmp(buffer_file, buffer_flash, rc)) {
					fprintf(stderr, "Found difference between flash and file!\n");
					error();
				}
			}

			printf("VERIFY OK\n");

			fclose(f);
		}


		// ---------------------------------------------------------
		// Reset
		// ---------------------------------------------------------

		set_gpio(1, 1);
		usleep(250000);

		printf("cdone: %s\n", get_cdone() ? "high" : "low");
	}


	// ---------------------------------------------------------
	// Exit
	// ---------------------------------------------------------

	printf("Bye.\n");
	ftdi_disable_bitbang(&ftdic);
	ftdi_usb_close(&ftdic);
	ftdi_deinit(&ftdic);
	return 0;
}

