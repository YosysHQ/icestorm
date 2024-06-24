//
//  Copyright (C) 2016  Clifford Wolf <clifford@clifford.at>
//  Copyright (C) 2023  Sylvain Munaut <tnt@246tNt.com>
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
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <unistd.h>
#include <sys/time.h>

#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <valarray>
#include <vector>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif



struct app_opts {
	char    *prog;

	int      extra_argc;
	char   **extra_argv;

	bool     generate;
	bool     verbose;
	uint32_t seed_nr;
	bool     seed;
};

static void help(const char *cmd);


// ---------------------------------------------------------------------------
// Update mode
// ---------------------------------------------------------------------------


// Hex Data File
// -------------

class HexFile
{
private:
	std::vector<std::vector<bool>> m_data;
	size_t m_word_size;

	std::vector<bool> parse_digits(std::vector<int> &digits) const;
	bool              parse_line(std::string &line);
public:
	HexFile(const char *filename, bool pad_words);
	virtual ~HexFile() { };

	void pad_words_to(size_t size);
	void pad_to(size_t size);

	size_t size()      const { return this->m_data.size(); };
	size_t word_size() const { return this->m_word_size;   };

	std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> generate_pattern(HexFile &to) const;
};

HexFile::HexFile(const char *filename, bool pad_words=false)
{
	std::ifstream stream(filename);

	if (!stream.is_open()) {
		fprintf(stderr, "Failed to open file %s\n", filename);
		exit(1);
	}

	// Parse file
	std::string line;
	for (int i=1; std::getline(stream, line); i++)
		if (!this->parse_line(line)) {
			fprintf(stderr, "Can't parse line %d of %s: %s\n", i, filename, line.c_str());
			exit(1);
		}

	// Check word size
	this->m_word_size = this->m_data.at(0).size();

	for (auto &w : this->m_data)
	{
		if ((w.size() != this->m_word_size) && !pad_words) {
			fprintf(stderr, "Inconsistent word sizes in %s\n", filename);
			exit(1);
		}
		if (w.size() > this->m_word_size)
			this->m_word_size = w.size();
	}

	// If requested, pad them
	this->pad_words_to(this->m_word_size);
}

std::vector<bool>
HexFile::parse_digits(std::vector<int> &digits) const
{
	std::vector<bool> line_data(digits.size() * 4);

	for (int i = 0; i < int(digits.size()) * 4; i++)
		if ((digits.at(digits.size() - i/4 -1) & (1 << (i%4))) != 0)
			line_data.at(i) = true;

	return line_data;
}

bool
HexFile::parse_line(std::string &line)
{
	std::vector<int> digits;

	for (char c : line) {
		if ('0' <= c && c <= '9')
			digits.push_back(c - '0');
		else if ('a' <= c && c <= 'f')
			digits.push_back(10 + c - 'a');
		else if ('A' <= c && c <= 'F')
			digits.push_back(10 + c - 'A');
		else if ('x' == c || 'X' == c ||
			 'z' == c || 'Z' == c)
			digits.push_back(0);
		else if ('_' == c)
			;
		else if (' ' == c || '\t' == c || '\r' == c) {
			if (digits.size()) {
				this->m_data.push_back(this->parse_digits(digits));
				digits.clear();
			}
		} else {
			return false;
		}
	}

	if (digits.size())
		this->m_data.push_back(this->parse_digits(digits));
	
	return true;
}

void
HexFile::pad_words_to(size_t size)
{
	if (this->m_word_size > size)
		return;

	for (auto &w : this->m_data)
		if (w.size() < size)
			w.resize(size, false);

	this->m_word_size = size;
}

void
HexFile::pad_to(size_t size)
{
	while (this->m_data.size() < size)
		this->m_data.push_back(std::vector<bool>(this->m_word_size));
}

std::map<std::vector<bool>, std::pair<std::vector<bool>, int>>
HexFile::generate_pattern(HexFile &to) const
{
	std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> pattern;

	for (int i=0; i<int(this->m_word_size); i++)
	{
		std::vector<bool> pattern_from, pattern_to;

		for (int j=0; j<int(this->m_data.size()); j++)
		{
			pattern_from.push_back(this->m_data.at(j).at(i));
			pattern_to.push_back(to.m_data.at(j).at(i));

			if (pattern_from.size() == 256) {
				if (pattern.count(pattern_from)) {
					fprintf(stderr, "Conflicting from pattern for bit slice from_hexfile[%d:%d][%d]!\n", j, j-255, i);
					exit(1);
				}
				pattern[pattern_from] = std::make_pair(pattern_to, 0);
				pattern_from.clear(), pattern_to.clear();
			}
		}
	}

	return pattern;
}


// Bitstream File
// --------------

class EBRData
{
private:
	std::vector<bool> m_data;
	int m_read_mode;

	int m_pos[2];
	int m_data_line;
	int m_config_line;
	std::vector<std::string> &m_lines;

	friend class AscFile;

protected:
	void load_data   ();
	void save_data   ();
	void load_config ();

public:
	EBRData(std::vector<std::string> &lines, int pos[2]);
	virtual ~EBRData() { };

	void apply_pattern(std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> &pattern);
};

class AscFile
{
private:
	std::vector<std::string> m_lines;
	std::map<int, EBRData> m_ebr;

	EBRData &get_ebr(int pos[2]);

public:
	AscFile();
	virtual ~AscFile() { };

	void load_config(std::istream &is);
	void save_config(std::ostream &os);

	size_t n_ebrs() const { return this->m_ebr.size(); };

	void apply_pattern(std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> &pattern);
};


EBRData::EBRData(std::vector<std::string> &lines, int pos[2]) :
	m_data(4096),
	m_pos{pos[0], pos[1]},
	m_data_line(-1), m_config_line(-1), m_lines(lines)
{

}

void
EBRData::load_data()
{
	auto si = this->m_lines.begin() + this->m_data_line + 16;
	auto ei = this->m_lines.begin() + this->m_data_line;
	int idx = 4096;

	for (auto line=si; line!=ei; line--) {
		for (char c : *line) {
			int digit;

			if ('0' <= c && c <= '9')
				digit = c - '0';
			else if ('a' <= c && c <= 'f')
				digit = 10 + c - 'a';
			else if ('A' <= c && c <= 'F')
				digit = 10 + c - 'A';
			else {
				fprintf(stderr, "Invalid char in BRAM data\n");
				exit(1);
			}

			idx -= 4;

			for (int subidx=3; subidx>=0; subidx--)
				if (digit & (1 << subidx))
					this->m_data.at(idx+subidx) = true;
		}
	}
}

void
EBRData::save_data()
{
	auto si = this->m_lines.begin() + this->m_data_line + 16;
	auto ei = this->m_lines.begin() + this->m_data_line;
	int idx = 4096;

	for (auto line=si; line!=ei; line--) {
		// Hex String
		char hex[65];
		idx -= 256;
		for (int bit=0; bit<256; bit+=4) {
			int digit = (this->m_data[idx+bit+3] ? 8 : 0) |
			            (this->m_data[idx+bit+2] ? 4 : 0) |
			            (this->m_data[idx+bit+1] ? 2 : 0) |
			            (this->m_data[idx+bit+0] ? 1 : 0);
			hex[63-(bit>>2)] = "0123456789abcdef"[digit];
		}
		hex[64] = 0;

		// Put new line
		*line = std::string(hex);
	}
}

void
EBRData::load_config()
{
	this->m_read_mode = (
		((this->m_lines.at(this->m_config_line+3).at(7) == '1') ? 2 : 0) | // RamConfig.CBIT_2
		((this->m_lines.at(this->m_config_line+4).at(7) == '1') ? 1 : 0)   // RamConfig.CBIT_3
	);
}

void
EBRData::apply_pattern(std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> &pattern)
{
	const std::map<int, std::vector<int>> subidx_map =  {
		{ 0, { 0 } },
		{ 1, { 0, 1 } },
		{ 2, { 0, 2, 1, 3 } },
		{ 3, { 0, 4, 2, 6, 1, 5, 3, 7 } },
	};

	const std::vector<int> &subidx = subidx_map.at(this->m_read_mode);
	int W = 16 >> this->m_read_mode;
	int P = 16 / W;

	for (int blk_base=0; blk_base<4096; blk_base+=4096/P)
	{
		for (int bit_base=0; bit_base<16; bit_base+=P)
		{
			std::vector<bool> fbs(256);

			// Create "From Bit Slice" from local memory
			for (int oaddr=0; oaddr<256/P; oaddr++)
				for (int iaddr=0; iaddr<P; iaddr++)
					fbs.at(oaddr*P+iaddr) = this->m_data.at(blk_base+bit_base+oaddr*16+subidx.at(iaddr));

			// Perform substitution
			auto p = pattern.find(fbs);
			if (p == pattern.end())
				continue;

			auto &tbs = p->second.first;
			p->second.second++;

			// Map "To Bit Slice" back into local memory
			for (int oaddr=0; oaddr<256/P; oaddr++)
				for (int iaddr=0; iaddr<P; iaddr++)
					this->m_data.at(blk_base+bit_base+oaddr*16+subidx.at(iaddr)) = tbs.at(oaddr*P+iaddr);
		}
	}
}


AscFile::AscFile()
{
	// Nothing to do for now
}

EBRData &
AscFile::get_ebr(int pos[2])
{
	int p = pos[0] | (pos[1] << 8);
	return (*this->m_ebr.emplace(p, EBRData{this->m_lines, pos}).first).second;
}

void
AscFile::load_config(std::istream &is)
{
	std::string line;
	int pos[2];

	// Load data and track where each EBR is configured and initialized
	for (int l=0; std::getline(is, line); l++) {
		// Save line
		this->m_lines.push_back(line);

		// Keep position of RAM infos
		if (line.substr(0, 9) == ".ram_data") {
			sscanf(line.substr(10).c_str(), "%d %d", &pos[0], &pos[1]);
			this->get_ebr(pos).m_data_line = l;
		} else if (line.substr(0, 10) == ".ramt_tile") {
			sscanf(line.substr(11).c_str(), "%d %d", &pos[0], &pos[1]);
			pos[1] -= 1;
			this->get_ebr(pos).m_config_line = l;
		}
	}

	// Only keep EBR that are initialized
	for (auto it = this->m_ebr.begin(); it != this->m_ebr.end(); )
		if (it->second.m_data_line < 0)
			it = this->m_ebr.erase(it);
		else
			++it;

	// Load data config for those
	for (auto &ebr : this->m_ebr) {
		ebr.second.load_data();
		ebr.second.load_config();
	}
}

void
AscFile::save_config(std::ostream &os)
{
	// Update all EBRs
	for (auto &ebr : this->m_ebr)
		ebr.second.save_data();

	// Output new config
	for (auto &l: this->m_lines)
		os << l << std::endl;
}

void
AscFile::apply_pattern(std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> &pattern)
{
	for (auto &ebr : this->m_ebr)
		ebr.second.apply_pattern(pattern);
}


// Update process
// ---------------

static int
update(struct app_opts *opts)
{
	if (opts->extra_argc != 2)
		help(opts->prog);

	// Parse two source files
	HexFile hf_from (opts->extra_argv[0]);
	HexFile hf_to   (opts->extra_argv[1], true);

	// Perform checks
	if ((hf_to.word_size() > 0) && (hf_from.word_size() > hf_to.word_size())) {
		if (opts->verbose)
			fprintf(stderr, "Padding to_hexfile words from %zu bits to %zu bits\n",
				hf_to.word_size(), hf_from.word_size());
		hf_to.pad_words_to(hf_from.word_size());
	}

	if (hf_to.word_size() != hf_from.word_size()) {
		fprintf(stderr, "Hexfiles have different word sizes! (%zu bits vs. %zu bits)\n",
			hf_from.word_size(), hf_to.word_size());
		return 1;
	}

	if ((hf_to.size() > 0) && (hf_from.size() > hf_to.size())) {
		if (opts->verbose)
			fprintf(stderr, "Padding to_hexfile from %zu words to %zu\n",
				hf_to.size(), hf_from.size());
		hf_to.pad_to(hf_from.size());
	}

	if (hf_to.size() != hf_from.size()) {
		fprintf(stderr, "Hexfiles have different number of words! (%zu vs. %zu)\n",
			hf_from.size(), hf_to.size());
		return 1;
	}

	if (hf_from.size() % 256 != 0) {
		fprintf(stderr, "Hexfile number of words (%zu) is not divisible by 256!\n",
			hf_from.size());
		return 1;
	}

	if (hf_from.size() == 0 || hf_from.word_size() == 0) {
		fprintf(stderr, "Empty from/to hexfiles!\n");
		return 1;
	}

	// Debug
	if (opts->verbose)
		fprintf(stderr, "Loaded pattern for %zu bits wide and %zu words deep memory.\n",
			hf_from.word_size(), hf_from.size());

	// Generate mapping for slices
	std::map<std::vector<bool>, std::pair<std::vector<bool>, int>> pattern = hf_from.generate_pattern(hf_to);
	if (opts->verbose)
		fprintf(stderr, "Extracted %zu bit slices from from/to hexfile data.\n", pattern.size());

	// Load FPGA config from stdin
	AscFile bitstream;
	bitstream.load_config(std::cin);

	if (opts->verbose)
		fprintf(stderr, "Found %zu initialized bram cells in asc file.\n", bitstream.n_ebrs());

	// Apply pattern
	bitstream.apply_pattern(pattern);

	// Check pattern was applied uniformly
	int min_replace_cnt = INT_MAX;
	int max_replace_cnt = INT_MIN;

	for (auto &it : pattern) {
		max_replace_cnt = std::max(max_replace_cnt, it.second.second);
		min_replace_cnt = std::min(min_replace_cnt, it.second.second);
	}

	if (min_replace_cnt != max_replace_cnt) {
		fprintf(stderr, "Found some bitslices up to %d times, others only %d times!\n", max_replace_cnt, min_replace_cnt);
		return 1;
	}

	if (max_replace_cnt == 0) {
		fprintf(stderr, "No memory instances were replaced.\n");
		return 1;
	}

	if (opts->verbose)
		fprintf(stderr, "Found and replaced %d instances of the memory.\n", max_replace_cnt);

	// Save new FPGA config to stdout
	bitstream.save_config(std::cout);

	return 0;
}


// ---------------------------------------------------------------------------
// Generate mode
// ---------------------------------------------------------------------------

static uint64_t
xorshift64star(uint64_t *x)
{
	*x ^= *x >> 12; // a
	*x ^= *x << 25; // b
	*x ^= *x >> 27; // c
	return *x * UINT64_C(2685821657736338717);
}

static int
generate(struct app_opts *opts)
{
	if (opts->extra_argc != 2)
		help(opts->prog);

	int width = atoi(opts->extra_argv[0]);
	int depth = atoi(opts->extra_argv[1]);

	if (width <= 0 || width % 4 != 0) {
		fprintf(stderr, "Hexfile width (%d bits) is not divisible by 4 or nonpositive!\n", width);
		exit(1);
	}

	if (depth <= 0 || depth % 256 != 0) {
		fprintf(stderr, "Hexfile number of words (%d) is not divisible by 256 or nonpositive!\n", depth);
		exit(1);
	}

	if (opts->verbose && opts->seed)
		fprintf(stderr, "Seed: %d\n", opts->seed_nr);


	if (!opts->seed) {
#if defined(__wasm)
		opts->seed_nr = 0;
#else
		opts->seed_nr = getpid();
#endif
	}

	uint64_t x;

	x =  uint64_t(opts->seed_nr) << 32;
	x ^= uint64_t(depth) << 16;
	x ^= uint64_t(width) << 10;

	xorshift64star(&x);
	xorshift64star(&x);
	xorshift64star(&x);

	if (!opts->seed) {
		struct timeval tv;
		gettimeofday(&tv, NULL);
		x ^= uint64_t(tv.tv_sec) << 20;
		x ^= uint64_t(tv.tv_usec);
	}

	xorshift64star(&x);
	xorshift64star(&x);
	xorshift64star(&x);

	for (int i = 0; i < depth; i++) {
		for (int j = 0; j < width / 4; j++) {
			int digit = xorshift64star(&x) & 15;
			std::cout << "0123456789abcdef"[digit];
		}
		std::cout << std::endl;
	}

	return 0;
}


// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

static void
help(const char *cmd)
{
	printf("\n");
	printf("Usage: %s [options] <from_hexfile> <to_hexfile>\n", cmd);
	printf("       %s [options] -g [-s <seed>] <width> <depth>\n", cmd);
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
	printf("    -s <seed>\n");
	printf("        seed random generator with fixed value.\n");
	printf("\n");
	printf("    -v\n");
	printf("        verbose output\n");
	printf("\n");
	exit(1);
}

static void
opts_defaults(struct app_opts *opts)
{
	// Clear
	memset(opts, 0x00, sizeof(*opts));
}

static void
opts_parse(struct app_opts *opts, int argc, char *argv[])
{
	int opt;

	opts->prog = argv[0];

	while ((opt = getopt(argc, argv, "vgs:")) != -1)
	{
		switch (opt)
		{
		case 'v':
			opts->verbose = true;
			break;
		case 'g':
			opts->generate = true;
			break;
		case 's':
			opts->seed = true;
			opts->seed_nr = atoi(optarg);
			break;
		default:
			help(argv[0]);
		}
	}

	opts->extra_argc = argc - optind;
	opts->extra_argv = &argv[optind];
}

int main(int argc, char **argv)
{
	struct app_opts opts;

#ifdef __EMSCRIPTEN__
	EM_ASM(
		if (ENVIRONMENT_IS_NODE)
		{
			FS.mkdir('/hostcwd');
			FS.mount(NODEFS, { root: '.' }, '/hostcwd');
			FS.mkdir('/hostfs');
			FS.mount(NODEFS, { root: '/' }, '/hostfs');
		}
	);
#endif

	opts_defaults(&opts);
	opts_parse(&opts, argc, argv);

	if (opts.generate)
		return generate(&opts);
	else
		return update(&opts);
}
