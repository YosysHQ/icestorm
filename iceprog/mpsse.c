/*
 *  iceprog -- simple programming tool for FTDI-based Lattice iCE programmers
 *
 *  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
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
 *  http://www.ftdichip.com/Support/Documents/AppNotes/AN_108_Command_Processor_for_MPSSE_and_MCU_Host_Bus_Emulation_Modes.pdf
 */

#define _GNU_SOURCE

#include <ftdi.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>

#include "mpsse.h"

// ---------------------------------------------------------
// MPSSE / FTDI definitions
// ---------------------------------------------------------

/* FTDI bank pinout typically used for iCE dev boards
 * BUS IO | Signal | Control
 * -------+--------+--------------
 * xDBUS0 |    SCK | MPSSE
 * xDBUS1 |   MOSI | MPSSE
 * xDBUS2 |   MISO | MPSSE
 * xDBUS3 |     nc |
 * xDBUS4 |     CS | GPIO
 * xDBUS5 |     nc |
 * xDBUS6 |  CDONE | GPIO
 * xDBUS7 | CRESET | GPIO
 */

struct ftdi_context mpsse_ftdic;
bool mpsse_ftdic_open = false;
bool mpsse_ftdic_latency_set = false;
unsigned char mpsse_ftdi_latency;

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

// ---------------------------------------------------------
// MPSSE / FTDI function implementations
// ---------------------------------------------------------

void mpsse_check_rx()
{
	while (1) {
		uint8_t data;
		int rc = ftdi_read_data(&mpsse_ftdic, &data, 1);
		if (rc <= 0)
			break;
		fprintf(stderr, "unexpected rx byte: %02X\n", data);
	}
}

void mpsse_error(int status)
{
	mpsse_check_rx();
	fprintf(stderr, "ABORT.\n");
	if (mpsse_ftdic_open) {
		if (mpsse_ftdic_latency_set)
			ftdi_set_latency_timer(&mpsse_ftdic, mpsse_ftdi_latency);
		ftdi_usb_close(&mpsse_ftdic);
	}
	ftdi_deinit(&mpsse_ftdic);
	exit(status);
}

uint8_t mpsse_recv_byte()
{
	uint8_t data;
	while (1) {
		int rc = ftdi_read_data(&mpsse_ftdic, &data, 1);
		if (rc < 0) {
			fprintf(stderr, "Read error.\n");
			mpsse_error(2);
		}
		if (rc == 1)
			break;
		usleep(100);
	}
	return data;
}

void mpsse_send_byte(uint8_t data)
{
	int rc = ftdi_write_data(&mpsse_ftdic, &data, 1);
	if (rc != 1) {
		fprintf(stderr, "Write error (single byte, rc=%d, expected %d).\n", rc, 1);
		mpsse_error(2);
	}
}

void mpsse_send_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	/* Output only, update data on negative clock edge. */
	mpsse_send_byte(MC_DATA_OUT | MC_DATA_OCN);
	mpsse_send_byte(n - 1);
	mpsse_send_byte((n - 1) >> 8);

	int rc = ftdi_write_data(&mpsse_ftdic, data, n);
	if (rc != n) {
		fprintf(stderr, "Write error (chunk, rc=%d, expected %d).\n", rc, n);
		mpsse_error(2);
	}
}

void mpsse_xfer_spi(uint8_t *data, int n)
{
	if (n < 1)
		return;

	/* Input and output, update data on negative edge read on positive. */
	mpsse_send_byte(MC_DATA_IN | MC_DATA_OUT | MC_DATA_OCN);
	mpsse_send_byte(n - 1);
	mpsse_send_byte((n - 1) >> 8);

	int rc = ftdi_write_data(&mpsse_ftdic, data, n);
	if (rc != n) {
		fprintf(stderr, "Write error (chunk, rc=%d, expected %d).\n", rc, n);
		mpsse_error(2);
	}

	for (int i = 0; i < n; i++)
		data[i] = mpsse_recv_byte();
}

uint8_t mpsse_xfer_spi_bits(uint8_t data, int n)
{
	if (n < 1)
		return 0;

	/* Input and output, update data on negative edge read on positive, bits. */
	mpsse_send_byte(MC_DATA_IN | MC_DATA_OUT | MC_DATA_OCN | MC_DATA_BITS);
	mpsse_send_byte(n - 1);
	mpsse_send_byte(data);

	return mpsse_recv_byte();
}

void mpsse_set_gpio(uint8_t gpio, uint8_t direction)
{
	mpsse_send_byte(MC_SETB_LOW);
	mpsse_send_byte(gpio); /* Value */
	mpsse_send_byte(direction); /* Direction */
}

int mpsse_readb_low(void)
{
	uint8_t data;
	mpsse_send_byte(MC_READB_LOW);
	data = mpsse_recv_byte();
	return data;
}

int mpsse_readb_high(void)
{
	uint8_t data;
	mpsse_send_byte(MC_READB_HIGH);
	data = mpsse_recv_byte();
	return data;
}

void mpsse_send_dummy_bytes(uint8_t n)
{
	// add 8 x count dummy bits (aka n bytes)
	mpsse_send_byte(MC_CLK_N8);
	mpsse_send_byte(n - 1);
	mpsse_send_byte(0x00);

}

void mpsse_send_dummy_bit(void)
{
	// add 1  dummy bit
	mpsse_send_byte(MC_CLK_N);
	mpsse_send_byte(0x00);
}

void mpsse_init(int ifnum, const char *devstr, bool slow_clock)
{
	enum ftdi_interface ftdi_ifnum = INTERFACE_A;

	switch (ifnum) {
		case 0:
			ftdi_ifnum = INTERFACE_A;
			break;
		case 1:
			ftdi_ifnum = INTERFACE_B;
			break;
		case 2:
			ftdi_ifnum = INTERFACE_C;
			break;
		case 3:
			ftdi_ifnum = INTERFACE_D;
			break;
		default:
			ftdi_ifnum = INTERFACE_A;
			break;
	}

	ftdi_init(&mpsse_ftdic);
	ftdi_set_interface(&mpsse_ftdic, ftdi_ifnum);

	if (devstr != NULL) {
		if (ftdi_usb_open_string(&mpsse_ftdic, devstr)) {
			fprintf(stderr, "Can't find iCE FTDI USB device (device string %s).\n", devstr);
			mpsse_error(2);
		}
	} else {
		if (ftdi_usb_open(&mpsse_ftdic, 0x0403, 0x6010) && ftdi_usb_open(&mpsse_ftdic, 0x0403, 0x6014)) {
			fprintf(stderr, "Can't find iCE FTDI USB device (vendor_id 0x0403, device_id 0x6010 or 0x6014).\n");
			mpsse_error(2);
		}
	}

	mpsse_ftdic_open = true;

	if (ftdi_usb_reset(&mpsse_ftdic)) {
		fprintf(stderr, "Failed to reset iCE FTDI USB device.\n");
		mpsse_error(2);
	}

	if (ftdi_usb_purge_buffers(&mpsse_ftdic)) {
		fprintf(stderr, "Failed to purge buffers on iCE FTDI USB device.\n");
		mpsse_error(2);
	}

	if (ftdi_get_latency_timer(&mpsse_ftdic, &mpsse_ftdi_latency) < 0) {
		fprintf(stderr, "Failed to get latency timer (%s).\n", ftdi_get_error_string(&mpsse_ftdic));
		mpsse_error(2);
	}

	/* 1 is the fastest polling, it means 1 kHz polling */
	if (ftdi_set_latency_timer(&mpsse_ftdic, 1) < 0) {
		fprintf(stderr, "Failed to set latency timer (%s).\n", ftdi_get_error_string(&mpsse_ftdic));
		mpsse_error(2);
	}

	mpsse_ftdic_latency_set = true;

	/* Enter MPSSE (Multi-Protocol Synchronous Serial Engine) mode. Set all pins to output. */
	if (ftdi_set_bitmode(&mpsse_ftdic, 0xff, BITMODE_MPSSE) < 0) {
		fprintf(stderr, "Failed to set BITMODE_MPSSE on iCE FTDI USB device.\n");
		mpsse_error(2);
	}

	// enable clock divide by 5
	mpsse_send_byte(MC_TCK_D5);

	if (slow_clock) {
		// set 50 kHz clock
		mpsse_send_byte(MC_SET_CLK_DIV);
		mpsse_send_byte(119);
		mpsse_send_byte(0x00);
	} else {
		// set 6 MHz clock
		mpsse_send_byte(MC_SET_CLK_DIV);
		mpsse_send_byte(0x00);
		mpsse_send_byte(0x00);
	}
}

void mpsse_close(void)
{
	ftdi_set_latency_timer(&mpsse_ftdic, mpsse_ftdi_latency);
	ftdi_disable_bitbang(&mpsse_ftdic);
	ftdi_usb_close(&mpsse_ftdic);
	ftdi_deinit(&mpsse_ftdic);
}