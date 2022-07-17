#include "ftdi_interface.h"
#include "mpsse.h"
#include <stdio.h>

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

const interface_t ftdi_interface = {
	.close = mpsse_close,
	.error = mpsse_error,

	.set_cs_creset = set_cs_creset,
	.get_cdone = get_cdone,

	.send_spi = mpsse_send_spi,
	.xfer_spi = mpsse_xfer_spi,
	.xfer_spi_bits = mpsse_xfer_spi_bits,

	.send_dummy_bytes = mpsse_send_dummy_bytes,
	.send_dummy_bit = mpsse_send_dummy_bit,
};

void ftdi_interface_init(int ifnum, const char *devstr, bool slow_clock) {
	mpsse_init(ifnum, devstr, slow_clock);
}
