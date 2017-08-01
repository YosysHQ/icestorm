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
#include <vector>
#include <map>

int verbose = 0;

static void push_int_bits(std::vector<bool> &outbits, int value, int bits)
{
	while (bits-- > 0)
		outbits.push_back((value >> bits) & 1);
}

static void push_zero_bits(std::vector<bool> &outbits, int bits)
{
	while (bits-- > 0)
		outbits.push_back(false);
}

static int decode_int_from_bits(const std::vector<bool> &inbits, int &cursor, int bits)
{
	int ret = 0;
	while (bits-- > 0)
		if (inbits.at(cursor++))
			ret |= 1 << bits;
	return ret;
}

void ice_compress(std::vector<bool> &outbits, const std::vector<bool> &inbits)
{
	int opcode_stats_d4 = 0;
	int opcode_stats_d32 = 0;
	int opcode_stats_d256 = 0;
	int opcode_stats_raw = 0;
	int opcode_stats_d8M = 0;
	int opcode_stats_end = 0;

	std::vector<int> deltas;
	int numzeros = 0;

	for (auto bit : inbits)
	{
		if (bit) {
			deltas.push_back(numzeros);
			numzeros = 0;
		} else {
			numzeros++;
		}
	}

	for (int i = 0; i < int(deltas.size()); i++)
	{
		int raw_len = 0;
		int compr_len = 0;
		int best_compr_raw_diff = -1;
		int best_compr_raw_idx = -1;
		int best_compr_raw_len = -1;

		for (int j = 0; j+i < int(deltas.size()); j++)
		{
			int delta = deltas.at(i + j);
			raw_len += delta + 1;

			if (delta < 4)
				compr_len += 3;
			else if (delta < 32)
				compr_len += 7;
			else if (delta < 256)
				compr_len += 11;
			else
				compr_len += 26;

			if (compr_len - raw_len < std::max(best_compr_raw_diff - 4, 0) || raw_len > 64)
				break;

			if (compr_len - raw_len > best_compr_raw_diff) {
				best_compr_raw_diff = compr_len - raw_len;
				best_compr_raw_idx = j;
				best_compr_raw_len = raw_len;
			}
		}

		if (best_compr_raw_diff > 9)
		{
			opcode_stats_raw++;
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(true);
			push_int_bits(outbits, best_compr_raw_len-1, 6);

			for (int j = 0; j <= best_compr_raw_idx; j++) {
				int delta = deltas.at(i + j);
				for (int k = 0; k < delta; k++)
					outbits.push_back(false);
				if (j < best_compr_raw_idx)
					outbits.push_back(true);
			}

			i += best_compr_raw_idx;
			continue;
		}

		int delta = deltas.at(i);

		if (delta < 4) {
			opcode_stats_d4++;
			outbits.push_back(true);
			push_int_bits(outbits, delta, 2);
		} else
		if (delta < 32) {
			opcode_stats_d32++;
			outbits.push_back(false);
			outbits.push_back(true);
			push_int_bits(outbits, delta, 5);
		} else
		if (delta < 256) {
			opcode_stats_d256++;
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(true);
			push_int_bits(outbits, delta, 8);
		} else {
			opcode_stats_d8M++;
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(false);
			outbits.push_back(true);
			push_int_bits(outbits, delta, 23);
		}
	}

	opcode_stats_end++;
	outbits.push_back(false);
	outbits.push_back(false);
	outbits.push_back(false);
	outbits.push_back(false);
	outbits.push_back(false);
	push_int_bits(outbits, numzeros, 23);

	if (verbose > 1) {
		fprintf(stderr, "opcode d4   %5d\n", opcode_stats_d4);
		fprintf(stderr, "opcode d32  %5d\n", opcode_stats_d32);
		fprintf(stderr, "opcode d256 %5d\n", opcode_stats_d256);
		fprintf(stderr, "opcode raw  %5d\n", opcode_stats_raw);
		fprintf(stderr, "opcode d8M  %5d\n", opcode_stats_d8M);
		fprintf(stderr, "opcode end  %5d\n", opcode_stats_end);
	}
}

void ice_uncompress(std::vector<bool> &outbits, const std::vector<bool> &inbits)
{
	int cursor = 0;

	while (cursor < int(inbits.size()))
	{
		if (inbits.at(cursor++)) {
			int zeros = decode_int_from_bits(inbits, cursor, 2);
			push_zero_bits(outbits, zeros);
			outbits.push_back(true);
		} else
		if (inbits.at(cursor++)) {
			int zeros = decode_int_from_bits(inbits, cursor, 5);
			push_zero_bits(outbits, zeros);
			outbits.push_back(true);
		} else
		if (inbits.at(cursor++)) {
			int zeros = decode_int_from_bits(inbits, cursor, 8);
			push_zero_bits(outbits, zeros);
			outbits.push_back(true);
		} else
		if (inbits.at(cursor++)) {
			int raw_len = decode_int_from_bits(inbits, cursor, 6);
			while (raw_len--)
				outbits.push_back(inbits.at(cursor++));
			outbits.push_back(true);
		} else
		if (inbits.at(cursor++)) {
			int zeros = decode_int_from_bits(inbits, cursor, 23);
			push_zero_bits(outbits, zeros);
			outbits.push_back(true);
		} else {
			int zeros = decode_int_from_bits(inbits, cursor, 23);
			push_zero_bits(outbits, zeros);
		}
	}
}

void help()
{
	printf("\n");
	printf("Usage: icecompr [-v] [input-file [output-file]]\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	FILE *input_file = stdin;
	FILE *output_file = stdout;

	int opt;
	while ((opt = getopt(argc, argv, "v")) != -1)
	{
		switch (opt)
		{
		case 'v':
			verbose++;
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

	std::vector<bool> original_bits;
	int count_set_bits = 0;

	while (1)
	{
		int byte = fgetc(input_file);

		if (byte < 0)
			break;

		// MSB first
		for (int i = 7; i >= 0; i--) {
			bool bit = (byte >> i) & 1;
			if (bit) count_set_bits++;
			original_bits.push_back(bit);
		}
	}

	int uncompressed_size = original_bits.size();

	if (verbose > 0) {
		fprintf(stderr, "Percentage of set bits: %.2f%%\n", (100.0*count_set_bits) / uncompressed_size);
		fprintf(stderr, "Uncompressed size: %8d bits\n", uncompressed_size);
	}

	std::vector<bool> compressed_bits;
	ice_compress(compressed_bits, original_bits);

	int compressed_size = compressed_bits.size();

	if (verbose > 0) {
		fprintf(stderr, "Compressed size:   %8d bits\n", compressed_size);
		fprintf(stderr, "Space savings: %.2f%%\n", 100 - (100.0*compressed_size) / uncompressed_size);
	}

	std::vector<bool> uncompressed_bits;
	ice_uncompress(uncompressed_bits, compressed_bits);

	bool check_ok = original_bits == uncompressed_bits;

	if (verbose > 0 || !check_ok) {
		fprintf(stderr, "Integrity check: %s\n", check_ok ? "OK" : "ERROR");
		if (!check_ok)
			return 1;
	}

	fprintf(output_file, "ICECOMPR");
	for (int i = 0; i < int(compressed_bits.size()); i += 8) {
		int value = 0;
		for (int j = 0; j < 8 && i+j < int(compressed_bits.size()); j++)
			if (compressed_bits.at(i+j))
				value |= 1 << (7-j);
		fputc(value, output_file);
	}

	return 0;
}

