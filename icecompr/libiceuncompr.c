// This is free and unencumbered software released into the public domain.
//
// Anyone is free to copy, modify, publish, use, compile, sell, or
// distribute this software, either in source code form or as a compiled
// binary, for any purpose, commercial or non-commercial, and by any
// means.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

FILE *ice40_compr_input_file;
FILE *ice40_uncompr_output_file;

static int ice40_read_bitcounter;
static int ice40_read_buffer;

static int ice40_write_bitcounter;
static int ice40_write_buffer;

static int ice40_compr_read_bit()
{
	if (ice40_read_bitcounter == 0) {
		ice40_read_bitcounter = 8;
		ice40_read_buffer = fgetc(ice40_compr_input_file);
	}

	ice40_read_bitcounter--;
	return (ice40_read_buffer >> ice40_read_bitcounter) & 1;
}

static void ice40_uncompr_write_bit(int value)
{
	ice40_write_bitcounter--;

	if (value)
		ice40_write_buffer |= 1 << ice40_write_bitcounter;

	if (ice40_write_bitcounter == 0) {
		fputc(ice40_write_buffer, ice40_uncompr_output_file);
		ice40_write_bitcounter = 8;
		ice40_write_buffer = 0;
	}
}

static int ice40_compr_read_int(int bits)
{
	int ret = 0;
	while (bits-- > 0)
		if (ice40_compr_read_bit())
			ret |= 1 << bits;
	return ret;
}

static void ice40_uncompr_write_zeros(int bits)
{
	while (bits-- > 0)
		ice40_uncompr_write_bit(0);
}

int ice40_uncompress()
{
	ice40_read_bitcounter = 0;
	ice40_read_buffer = 0;

	ice40_write_bitcounter = 8;
	ice40_write_buffer = 0;

#define read_bit()     ice40_compr_read_bit()
#define read_int(x)    ice40_compr_read_int(x)
#define write_bit(x)   ice40_uncompr_write_bit(x)
#define write_zeros(x) ice40_uncompr_write_zeros(x)

	int magic1_ok = read_int(32) == 0x49434543;
	int magic2_ok = read_int(32) == 0x4f4d5052;

	if (!magic1_ok || !magic2_ok) {
		fprintf(stderr, "%s: Missing ICECOMPR magic. Abort!\n",
            __FUNCTION__);
		return 1;
	}

	while (1)
	{
		if (read_bit()) {
			write_zeros(read_int(2));
			write_bit(1);
		} else
		if (read_bit()) {
			write_zeros(read_int(5));
			write_bit(1);
		} else
		if (read_bit()) {
			write_zeros(read_int(8));
			write_bit(1);
		} else
		if (read_bit()) {
			int n = read_int(6);
			while (n--)
				write_bit(read_bit());
			write_bit(1);
		} else
		if (read_bit()) {
			write_zeros(read_int(23));
			write_bit(1);
		} else {
			write_zeros(read_int(23));
			break;
		}
	}

#undef write_zeros
#undef write_bit
#undef read_int
#undef read_bit

	return 0;
}
