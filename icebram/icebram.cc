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

#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>

using std::map;
using std::vector;
using std::string;
using std::ifstream;
using std::getline;

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

	for (int i = 0; i < digits.size() * 4; i++)
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
	printf("Usage: %s [options] from_hexfile to_hexfile \n", cmd);
	printf("\n");
	// printf("    -S\n");
	// printf("        Disable SIMPLE feedback path mode\n");
	// printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	int opt;
	while ((opt = getopt(argc, argv, "")) != -1)
	{
		switch (opt)
		{
		// case 'i':
		// 	f_pllin = atof(optarg);
		// 	break;
		default:
			help(argv[0]);
		}
	}

	if (optind+2 != argc)
		help(argv[0]);

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

	for (size_t i = 1; i < to_hexfile.size(); i++)
		if (to_hexfile.at(i-1).size() != to_hexfile.at(i).size()) {
			fprintf(stderr, "Inconsistent word width at line %d of %s!\n", int(i+1), to_hexfile_n);
			exit(1);
		}

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

	// FIXME: Do the actual thing

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
