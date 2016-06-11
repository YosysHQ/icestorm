//
//  Copyright (C) 2016  Clifford Wolf <clifford@clifford.at>
//
//  Permission to use, copy, modify, and/or distribute this software for any
//  purpose with or without fee is hereby granted, provided that the above
//  copyright notice and this permission notice appear in all copies.
//
//  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
//  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
//  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
//  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
//  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
//  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
//  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
//

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <sys/time.h>

#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>

using std::map;
using std::pair;
using std::vector;
using std::string;
using std::ifstream;
using std::getline;

uint64_t x;
uint64_t xorshift64star(void) {
	x ^= x >> 12; // a
	x ^= x << 25; // b
	x ^= x >> 27; // c
	return x * UINT64_C(2685821657736338717);
}

void parse_hexfile_line(const char *filename, int linenr, vector<vector<bool>> &hexfile, string &line)
{
	vector<int> digits;

	for (char c : line) {
		if ('0' <= c && c <= '9')
			digits.push_back(c - '0');
		else if ('a' <= c && c <= 'f')
			digits.push_back(10 + c - 'a');
		else if ('A' <= c && c <= 'F')
			digits.push_back(10 + c - 'A');
		else goto error;
	}

	hexfile.push_back(vector<bool>(digits.size() * 4));

	for (int i = 0; i < int(digits.size()) * 4; i++)
		if ((digits.at(digits.size() - i/4 -1) & (1 << (i%4))) != 0)
			hexfile.back().at(i) = true;

	return;

error:
	fprintf(stderr, "Can't parse line %d of %s: %s\n", linenr, filename, line.c_str());
	exit(1);
}

void help(const char *cmd)
{
	printf("\n");
	printf("Usage: %s [options] <from_hexfile> <to_hexfile>\n", cmd);
	printf("       %s [options] -g <width> <depth>\n", cmd);
	printf("\n");
	printf("Replace BRAM initialization data in a .asc file. This can be used\n");
	printf("for example to replace firmware images without re-running synthesis\n");
	printf("and place&route.\n");
	printf("\n");
	printf("    -g\n");
	printf("        generate a hex file with random contents.\n");
	printf("        use this to generate the hex file used during synthesis, then\n");
	printf("        use the same file as <from_hexfile> later.\n");
	printf("\n");
	printf("    -v\n");
	printf("        verbose output\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	bool verbose = false;
	bool generate = false;

	int opt;
	while ((opt = getopt(argc, argv, "vg")) != -1)
	{
		switch (opt)
		{
		case 'v':
			verbose = true;
			break;
		case 'g':
			generate = true;
			break;
		default:
			help(argv[0]);
		}
	}

	if (generate)
	{
		if (optind+2 != argc)
			help(argv[0]);

		int width = atoi(argv[optind]);
		int depth = atoi(argv[optind+1]);

		if (width <= 0 || width % 4 != 0) {
			fprintf(stderr, "Hexfile width (%d bits) is not divisible by 4 or nonpositive!\n", width);
			exit(1);
		}

		if (depth <= 0 || depth % 256 != 0) {
			fprintf(stderr, "Hexfile number of words (%d) is not divisible by 256 or nonpositive!\n", depth);
			exit(1);
		}

		x = uint64_t(getpid()) << 32;
		x ^= uint64_t(depth) << 16;
		x ^= uint64_t(width) << 10;

		xorshift64star();
		xorshift64star();
		xorshift64star();

		struct timeval tv;
		gettimeofday(&tv, NULL);
		x ^= uint64_t(tv.tv_sec) << 20;
		x ^= uint64_t(tv.tv_usec);

		xorshift64star();
		xorshift64star();
		xorshift64star();

		for (int i = 0; i < depth; i++) {
			for (int j = 0; j < width / 4; j++) {
				int digit = xorshift64star() & 15;
				std::cout << "0123456789abcdef"[digit];
			}
			std::cout << std::endl;
		}

		exit(0);
	}

	if (optind+2 != argc)
		help(argv[0]);


	// -------------------------------------------------------
	// Load from_hexfile and to_hexfile

	const char *from_hexfile_n = argv[optind];
	ifstream from_hexfile_f(from_hexfile_n);
	vector<vector<bool>> from_hexfile;

	const char *to_hexfile_n = argv[optind+1];
	ifstream to_hexfile_f(to_hexfile_n);
	vector<vector<bool>> to_hexfile;

	string line;

	for (int i = 1; getline(from_hexfile_f, line); i++)
		parse_hexfile_line(from_hexfile_n, i, from_hexfile, line);

	for (int i = 1; getline(to_hexfile_f, line); i++)
		parse_hexfile_line(to_hexfile_n, i, to_hexfile, line);

	if (from_hexfile.size() != to_hexfile.size()) {
		fprintf(stderr, "Hexfiles have different number of words! (%d vs. %d)\n", int(from_hexfile.size()), int(to_hexfile.size()));
		exit(1);
	}

	if (from_hexfile.size() % 256 != 0) {
		fprintf(stderr, "Hexfile number of words (%d) is not divisible by 256!\n", int(from_hexfile.size()));
		exit(1);
	}

	for (size_t i = 1; i < from_hexfile.size(); i++)
		if (from_hexfile.at(i-1).size() != from_hexfile.at(i).size()) {
			fprintf(stderr, "Inconsistent word width at line %d of %s!\n", int(i), from_hexfile_n);
			exit(1);
		}

	for (size_t i = 1; i < to_hexfile.size(); i++) {
		while (to_hexfile.at(i-1).size() > to_hexfile.at(i).size())
			to_hexfile.at(i).push_back(false);
		if (to_hexfile.at(i-1).size() != to_hexfile.at(i).size()) {
			fprintf(stderr, "Inconsistent word width at line %d of %s!\n", int(i+1), to_hexfile_n);
			exit(1);
		}
	}

	if (from_hexfile.size() == 0 || from_hexfile.at(0).size() == 0) {
		fprintf(stderr, "Empty from/to hexfiles!\n");
		exit(1);
	}

	if (verbose)
		fprintf(stderr, "Loaded pattern for %d bits wide and %d words deep memory.\n", int(from_hexfile.at(0).size()), int(from_hexfile.size()));


	// -------------------------------------------------------
	// Create bitslices from pattern data

	map<vector<bool>, pair<vector<bool>, int>> pattern;

	for (int i = 0; i < int(from_hexfile.at(0).size()); i++)
	{
		vector<bool> pattern_from, pattern_to;

		for (int j = 0; j < int(from_hexfile.size()); j++)
		{
			pattern_from.push_back(from_hexfile.at(j).at(i));
			pattern_to.push_back(to_hexfile.at(j).at(i));

			if (pattern_from.size() == 256) {
				if (pattern.count(pattern_from)) {
					fprintf(stderr, "Conflicting from pattern for bit slice from_hexfile[%d:%d][%d]!\n", j, j-255, i);
					exit(1);
				}
				pattern[pattern_from] = std::make_pair(pattern_to, 0);
				pattern_from.clear(), pattern_to.clear();
			}
		}

		assert(pattern_from.empty());
		assert(pattern_to.empty());
	}

	if (verbose)
		fprintf(stderr, "Extracted %d bit slices from from/to hexfile data.\n", int(pattern.size()));


	// -------------------------------------------------------
	// Read ascfile from stdin

	vector<string> ascfile_lines;
	map<string, vector<vector<bool>>> ascfile_hexdata;

	for (int i = 1; getline(std::cin, line); i++)
	{
	next_asc_stmt:
		ascfile_lines.push_back(line);

		if (line.substr(0, 9) == ".ram_data")
		{
			auto &hexdata = ascfile_hexdata[line];

			for (; getline(std::cin, line); i++) {
				if (line.substr(0, 1) == ".")
					goto next_asc_stmt;
				parse_hexfile_line("stdin", i, hexdata, line);
			}
		}
	}

	if (verbose)
		fprintf(stderr, "Found %d initialized bram cells in asc file.\n", int(ascfile_hexdata.size()));


	// -------------------------------------------------------
	// Replace bram data

	int max_replace_cnt = 0;

	for (auto &bram_it : ascfile_hexdata)
	{
		auto &bram_data = bram_it.second;

		for (int i = 0; i < 16; i++)
		{
			vector<bool> from_bitslice;

			for (int j = 0; j < 256; j++)
				from_bitslice.push_back(bram_data.at(j / 16).at(16 * (j % 16) + i));

			auto p = pattern.find(from_bitslice);
			if (p != pattern.end())
			{
				auto &to_bitslice = p->second.first;

				for (int j = 0; j < 256; j++)
					bram_data.at(j / 16).at(16 * (j % 16) + i) = to_bitslice.at(j);

				max_replace_cnt = std::max(++p->second.second, max_replace_cnt);
			}
		}
	}

	int min_replace_cnt = max_replace_cnt;
	for (auto &it : pattern)
		min_replace_cnt = std::min(min_replace_cnt, it.second.second);

	if (min_replace_cnt != max_replace_cnt) {
		fprintf(stderr, "Found some bitslices up to %d times, others only %d times!\n", max_replace_cnt, min_replace_cnt);
		exit(1);
	}

	if (verbose)
		fprintf(stderr, "Found and replaced %d instances of the memory.\n", max_replace_cnt);


	// -------------------------------------------------------
	// Write ascfile to stdout

	for (size_t i = 0; i < ascfile_lines.size(); i++) {
		auto &line = ascfile_lines.at(i);
		std::cout << line << std::endl;
		if (ascfile_hexdata.count(line)) {
			for (auto &word : ascfile_hexdata.at(line)) {
				for (int k = word.size()-4; k >= 0; k -= 4) {
					int digit = (word[k+3] ? 8 : 0) + (word[k+2] ? 4 : 0) + (word[k+1] ? 2 : 0) + (word[k] ? 1 : 0);
					std::cout << "0123456789abcdef"[digit];
				}
				std::cout << std::endl;
			}
		}
	}

	return 0;
}
