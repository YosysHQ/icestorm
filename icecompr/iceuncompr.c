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

FILE *input_file;
FILE *output_file;

int read_bitcounter;
int read_buffer;

int write_bitcounter;
int write_buffer;

static int read_bit()
{
	if (read_bitcounter == 0) {
		read_bitcounter = 8;
		read_buffer = fgetc(input_file);
	}

	read_bitcounter--;
	return (read_buffer >> read_bitcounter) & 1;
}

static void write_bit(int value)
{
	write_bitcounter--;

	if (value)
		write_buffer |= 1 << write_bitcounter;

	if (write_bitcounter == 0) {
		fputc(write_buffer, output_file);
		write_bitcounter = 8;
		write_buffer = 0;
	}
}

static int read_int(int bits)
{
	int ret = 0;
	while (bits-- > 0)
		if (read_bit())
			ret |= 1 << bits;
	return ret;
}

static void write_zeros(int bits)
{
	while (bits-- > 0)
		write_bit(0);
}

int ice_uncompress()
{
	read_bitcounter = 0;
	read_buffer = 0;

	write_bitcounter = 8;
	write_buffer = 0;

	int magic1_ok = read_int(32) == 0x49434543;
	int magic2_ok = read_int(32) == 0x4f4d5052;

	if (!magic1_ok || !magic2_ok) {
		fprintf(stderr, "Missing ICECOMPR magic. Abort!\n");
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

	return 0;
}

void help()
{
	printf("\n");
	printf("Usage: iceuncompr [input-file [output-file]]\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	input_file = stdin;
	output_file = stdout;

	int opt;
	while ((opt = getopt(argc, argv, "v")) != -1)
	{
		switch (opt)
		{
		case 'v':
			break;
		default:
			help();
		}
	}

	if (optind < argc) {
		input_file = fopen(argv[optind], "rb");
		if (input_file == NULL) {
			fprintf(stderr, "Failed to open input file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind < argc) {
		output_file = fopen(argv[optind], "wb");
		if (output_file == NULL) {
			fprintf(stderr, "Failed to open output file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind != argc)
		help();

	if (optind != argc)
		help();

	return ice_uncompress();
}

