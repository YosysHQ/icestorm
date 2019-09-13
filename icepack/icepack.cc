//
//  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
//
//  Based on a reference implementation provided by Mathias Lasser
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

#if !defined(_WIN32) && !defined(_GNU_SOURCE)
// for vasprintf()
#define _GNU_SOURCE
#endif

#include <set>
#include <tuple>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <sstream>
#include <cstdint>

#include <stdio.h>
#include <stdarg.h>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

#ifdef _WIN32
#define __PRETTY_FUNCTION__ __FUNCTION__
#endif


using std::vector;
using std::string;

int log_level = 0;
#define log(...) fprintf(stderr, __VA_ARGS__);
#define info(...) do { if (log_level > 0) fprintf(stderr, __VA_ARGS__); } while (0)
#define debug(...) do { if (log_level > 1) fprintf(stderr, __VA_ARGS__); } while (0)
#define error(...) do { fprintf(stderr, "Error: " __VA_ARGS__); exit(1); } while (0)
#define panic(fmt, ...) do { fprintf(stderr, "Internal Error at %s:%d: " fmt, __FILE__, __LINE__, ##__VA_ARGS__); abort(); } while (0)

string vstringf(const char *fmt, va_list ap)
{
	string string;
	char *str = NULL;

#ifdef _WIN32
	int sz = 64, rc;
	while (1) {
		va_list apc;
		va_copy(apc, ap);
		str = (char*)realloc(str, sz);
		rc = vsnprintf(str, sz, fmt, apc);
		va_end(apc);
		if (rc >= 0 && rc < sz)
			break;
		sz *= 2;
	}
#else
	if (vasprintf(&str, fmt, ap) < 0)
		str = NULL;
#endif

	if (str != NULL) {
		string = str;
		free(str);
	}

	return string;
}

string stringf(const char *fmt, ...)
{
	string string;
	va_list ap;

	va_start(ap, fmt);
	string = vstringf(fmt, ap);
	va_end(ap);

	return string;
}

// ==================================================================
// FpgaConfig stuff

struct FpgaConfig
{
	string device;
	string freqrange;
	string nosleep;
	string warmboot;

	// cram[BANK][X][Y]
	int cram_width, cram_height;
	vector<vector<vector<bool>>> cram;

	// bram[BANK][X][Y]
	int bram_width, bram_height;
	vector<vector<vector<bool>>> bram;
        bool skip_bram_initialization;

	// data before preamble
	vector<uint8_t> initblop;

	// bitstream i/o
	void read_bits(std::istream &ifs);
	void write_bits(std::ostream &ofs) const;

	// icebox i/o
	void read_ascii(std::istream &ifs, bool nosleep);
	void write_ascii(std::ostream &ofs) const;

	// netpbm i/o
	void write_cram_pbm(std::ostream &ofs, int bank_num = -1) const;
	void write_bram_pbm(std::ostream &ofs, int bank_num = -1) const;

	// query chip type metadata
	int chip_width() const;
	int chip_height() const;
	vector<int> chip_cols() const;

	// query tile metadata
	string tile_type(int x, int y) const;
	int tile_width(const string &type) const;

	// cram bit manipulation
	void cram_clear();
	void cram_fill_tiles();
	void cram_checkerboard(int m = 0);
};

struct CramIndexConverter
{
	const FpgaConfig *fpga;
	int tile_x, tile_y;

	string tile_type;
	int tile_width;
	int column_width;

	bool left_right_io;
	bool right_half;
	bool top_half;

	int bank_num;
	int bank_tx;
	int bank_ty;
	int bank_xoff;
	int bank_yoff;

	CramIndexConverter(const FpgaConfig *fpga, int tile_x, int tile_y);
	void get_cram_index(int bit_x, int bit_y, int &cram_bank, int &cram_x, int &cram_y) const;
};

struct BramIndexConverter
{
	const FpgaConfig *fpga;
	int tile_x, tile_y;

	int bank_num;
	int bank_off;

	BramIndexConverter(const FpgaConfig *fpga, int tile_x, int tile_y);
	void get_bram_index(int bit_x, int bit_y, int &bram_bank, int &bram_x, int &bram_y) const;
};

static void update_crc16(uint16_t &crc, uint8_t byte)
{
	// CRC-16-CCITT, Initialize to 0xFFFF, No zero padding
	for (int i = 7; i >= 0; i--) {
		uint16_t xor_value = ((crc >> 15) ^ ((byte >> i) & 1)) ? 0x1021 : 0;
		crc = (crc << 1) ^ xor_value;
	}
}

static uint8_t read_byte(std::istream &ifs, uint16_t &crc_value, int &file_offset)
{
	int byte = ifs.get();

	if (byte < 0)
		error("Unexpected end of file.\n");

	file_offset++;
	update_crc16(crc_value, byte);

	return byte;
}

static void write_byte(std::ostream &ofs, uint16_t &crc_value, int &file_offset, uint8_t byte)
{
	ofs << byte;
	file_offset++;
	update_crc16(crc_value, byte);
}

void FpgaConfig::read_bits(std::istream &ifs)
{
	int file_offset = 0;
	uint16_t crc_value = 0;

	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Parsing bitstream file..\n");

	// skip initial comments until preamble is found

	uint32_t preamble = 0;

	while (1)
	{
		uint8_t byte = read_byte(ifs, crc_value, file_offset);
		preamble = (preamble << 8) | byte;
		if (preamble == 0xffffffff)
			error("No preamble found in bitstream.\n");
		if (preamble == 0x7EAA997E) {
			info("Found preamble at offset %d.\n", file_offset-4);
			break;
		}
		initblop.push_back(byte);
	}

	initblop.pop_back();
	initblop.pop_back();
	initblop.pop_back();

	// main parser loop

	int current_bank = 0;
	int current_width = 0;
	int current_height = 0;
	int current_offset = 0;
	bool wakeup = false;

	this->cram_width = 0;
	this->cram_height = 0;

	this->bram_width = 0;
	this->bram_height = 0;

	while (!wakeup)
	{
		// one command byte. the lower 4 bits of the command byte specify
		// the length of the command payload.

		uint8_t command = read_byte(ifs, crc_value, file_offset);
		uint32_t payload = 0;

		for (int i = 0; i < (command & 0x0f); i++)
			payload = (payload << 8) | read_byte(ifs, crc_value, file_offset);

		debug("Next command at offset %d: 0x%02x 0x%0*x\n", file_offset - 1 - (command & 0x0f),
				command, 2*(command & 0x0f), payload);

		uint16_t end_token;

		switch (command & 0xf0)
		{
		case 0x00:
			switch (payload)
			{
			case 0x01:
				info("CRAM Data [%d]: %d x %d bits = %d bits = %d bytes\n",
						current_bank, current_width, current_height,
						current_height*current_width, (current_height*current_width)/8);

				this->cram_width = std::max(this->cram_width, current_width);
				this->cram_height = std::max(this->cram_height, current_offset + current_height);

				this->cram.resize(4);
				this->cram[current_bank].resize(this->cram_width);
				for (int x = 0; x < current_width; x++)
					this->cram[current_bank][x].resize(this->cram_height);

				for (int i = 0; i < (current_height*current_width)/8; i++) {
					uint8_t byte = read_byte(ifs, crc_value, file_offset);
					for (int j = 0; j < 8; j++) {
						int x = (i*8 + j) % current_width;
						int y = (i*8 + j) / current_width + current_offset;
						this->cram[current_bank][x][y] = ((byte << j) & 0x80) != 0;
					}
				}

				end_token = read_byte(ifs, crc_value, file_offset);
				end_token = (end_token << 8) | read_byte(ifs, crc_value, file_offset);
				if (end_token)
					error("Expeded 0x0000 after CRAM data, got 0x%04x\n", end_token);
				break;

			case 0x03:
				info("BRAM Data [%d]: %d x %d bits = %d bits = %d bytes\n",
						current_bank, current_width, current_height,
						current_height*current_width, (current_height*current_width)/8);

				this->bram_width = std::max(this->bram_width, current_width);
				this->bram_height = std::max(this->bram_height, current_offset + current_height);

				this->bram.resize(4);
				this->bram[current_bank].resize(this->bram_width);
				for (int x = 0; x < current_width; x++)
					this->bram[current_bank][x].resize(this->bram_height);

				for (int i = 0; i < (current_height*current_width)/8; i++) {
					uint8_t byte = read_byte(ifs, crc_value, file_offset);
					for (int j = 0; j < 8; j++) {
						int x = (i*8 + j) % current_width;
						int y = (i*8 + j) / current_width + current_offset;
						this->bram[current_bank][x][y] = ((byte << j) & 0x80) != 0;
					}
				}

				end_token = read_byte(ifs, crc_value, file_offset);
				end_token = (end_token << 8) | read_byte(ifs, crc_value, file_offset);
				if (end_token)
					error("Expected 0x0000 after BRAM data, got 0x%04x\n", end_token);
				break;

			case 0x05:
				debug("Resetting CRC.\n");
				crc_value = 0xffff;
				break;

			case 0x06:
				info("Wakeup.\n");
				wakeup = true;
				break;

			default:
				error("Unknown command: 0x%02x 0x%02x\n", command, payload);
			}
			break;

		case 0x10:
			current_bank = payload;
			debug("Set bank to %d.\n", current_bank);
			break;

		case 0x20:
			if (crc_value != 0)
				error("CRC Check FAILED.\n");
			info("CRC Check OK.\n");
			break;

		case 0x50:
			if (payload == 0)
				this->freqrange = "low";
			else if (payload == 1)
				this->freqrange = "medium";
			else if (payload == 2)
				this->freqrange = "high";
			else
				error("Unknown freqrange payload 0x%02x\n", payload);
			info("Setting freqrange to '%s'.\n", this->freqrange.c_str());
			break;

		case 0x60:
			current_width = payload + 1;
			debug("Setting bank width to %d.\n", current_width);
			break;

		case 0x70:
			current_height = payload;
			debug("Setting bank height to %d.\n", current_height);
			break;

		case 0x80:
			current_offset = payload;
			debug("Setting bank offset to %d.\n", current_offset);
			break;

		case 0x90:
			switch(payload)
			{
				case 0:
					this->warmboot = "disabled";
					this->nosleep = "disabled";
					break;
				case 1:
					this->warmboot = "disabled";
					this->nosleep = "enabled";
					break;
				case 32:
					this->warmboot = "enabled";
					this->nosleep = "disabled";
					break;
				case 33:
					this->warmboot = "enabled";
					this->nosleep = "enabled";
					break;
				default:
					error("Unknown warmboot/nosleep payload 0x%02x\n", payload);
			}
			info("Setting warmboot to '%s', nosleep to '%s'.\n", this->warmboot.c_str(), this->nosleep.c_str());
			break;

		default:
			error("Unknown command: 0x%02x 0x%02x\n", command, payload);
		}
	}

	if (this->cram_width == 182 && this->cram_height == 80)
		this->device = "384";
	else if (this->cram_width == 332 && this->cram_height == 144)
		this->device = "1k";
	else if (this->cram_width == 872 && this->cram_height == 272)
		this->device = "8k";
	else if (this->cram_width == 692 && this->cram_height == 336)
		this->device = "5k";
	else if (this->cram_width == 692 && this->cram_height == 176)
		this->device = "u4k";
	else if (this->cram_width == 656 && this->cram_height == 176)
		this->device = "lm4k";
	else
		error("Failed to detect chip type.\n");

	info("Chip type is '%s'.\n", this->device.c_str());
}

void FpgaConfig::write_bits(std::ostream &ofs) const
{
	int file_offset = 0;
	uint16_t crc_value = 0;

	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Writing bitstream file..\n");

	for (auto byte : this->initblop)
		ofs << byte;

	debug("Writing preamble.\n");
	write_byte(ofs, crc_value, file_offset, 0x7E);
	write_byte(ofs, crc_value, file_offset, 0xAA);
	write_byte(ofs, crc_value, file_offset, 0x99);
	write_byte(ofs, crc_value, file_offset, 0x7E);

	debug("Setting freqrange to '%s'.\n", this->freqrange.c_str());
	write_byte(ofs, crc_value, file_offset, 0x51);
	if (this->freqrange == "low")
		write_byte(ofs, crc_value, file_offset, 0x00);
	else if (this->freqrange == "medium")
		write_byte(ofs, crc_value, file_offset, 0x01);
	else if (this->freqrange == "high")
		write_byte(ofs, crc_value, file_offset, 0x02);
	else
		error("Unknown freqrange '%s'.\n", this->freqrange.c_str());

	debug("Resetting CRC.\n");
	write_byte(ofs, crc_value, file_offset, 0x01);
	write_byte(ofs, crc_value, file_offset, 0x05);
	crc_value = 0xffff;

	{
		uint8_t nosleep_flag;
		debug("Setting warmboot to '%s', nosleep to '%s'.\n", this->warmboot.c_str(), this->nosleep.c_str());
		write_byte(ofs, crc_value, file_offset, 0x92);
		write_byte(ofs, crc_value, file_offset, 0x00);

		if (this->nosleep == "disabled")
			nosleep_flag = 0;
		else if (this->nosleep == "enabled")
			nosleep_flag = 1;
		else
			error("Unknown nosleep setting '%s'.\n", this->nosleep.c_str());

		if (this->warmboot == "disabled")
			write_byte(ofs, crc_value, file_offset, 0x00 | nosleep_flag);
		else if (this->warmboot == "enabled")
			write_byte(ofs, crc_value, file_offset, 0x20 | nosleep_flag);
		else
			error("Unknown warmboot setting '%s'.\n", this->warmboot.c_str());
	}

	debug("CRAM: Setting bank width to %d.\n", this->cram_width);
	write_byte(ofs, crc_value, file_offset, 0x62);
	write_byte(ofs, crc_value, file_offset, (this->cram_width-1) >> 8);
	write_byte(ofs, crc_value, file_offset, (this->cram_width-1));
	if(this->device != "5k") {
		debug("CRAM: Setting bank height to %d.\n", this->cram_height);
		write_byte(ofs, crc_value, file_offset, 0x72);
		write_byte(ofs, crc_value, file_offset, this->cram_height >> 8);
		write_byte(ofs, crc_value, file_offset, this->cram_height);
	}

	debug("CRAM: Setting bank offset to 0.\n");
	write_byte(ofs, crc_value, file_offset, 0x82);
	write_byte(ofs, crc_value, file_offset, 0x00);
	write_byte(ofs, crc_value, file_offset, 0x00);

	for (int cram_bank = 0; cram_bank < 4; cram_bank++)
	{
		vector<bool> cram_bits;
		int height = this->cram_height;
		if(this->device == "5k" && ((cram_bank % 2) == 1))
			height = height / 2 + 8;
		for (int cram_y = 0; cram_y < height; cram_y++)
		for (int cram_x = 0; cram_x < this->cram_width; cram_x++)
			cram_bits.push_back(this->cram[cram_bank][cram_x][cram_y]);

		if(this->device == "5k") {
			debug("CRAM: Setting bank height to %d.\n", height);
			write_byte(ofs, crc_value, file_offset, 0x72);
			write_byte(ofs, crc_value, file_offset, height >> 8);
			write_byte(ofs, crc_value, file_offset, height);
		}

		debug("CRAM: Setting bank %d.\n", cram_bank);
		write_byte(ofs, crc_value, file_offset, 0x11);
		write_byte(ofs, crc_value, file_offset, cram_bank);

		debug("CRAM: Writing bank %d data.\n", cram_bank);
		write_byte(ofs, crc_value, file_offset, 0x01);
		write_byte(ofs, crc_value, file_offset, 0x01);
		for (int i = 0; i < int(cram_bits.size()); i += 8) {
			uint8_t byte = 0;
			for (int j = 0; j < 8; j++)
				byte = (byte << 1) | (cram_bits[i+j] ? 1 : 0);
			write_byte(ofs, crc_value, file_offset, byte);
		}

		write_byte(ofs, crc_value, file_offset, 0x00);
		write_byte(ofs, crc_value, file_offset, 0x00);
	}

	int bram_chunk_size = 128;

	if (this->bram_width && this->bram_height)
	{
		if(this->device != "5k") {
			debug("BRAM: Setting bank width to %d.\n", this->bram_width);
			write_byte(ofs, crc_value, file_offset, 0x62);
			write_byte(ofs, crc_value, file_offset, (this->bram_width-1) >> 8);
			write_byte(ofs, crc_value, file_offset, (this->bram_width-1));
		}


		debug("BRAM: Setting bank height to %d.\n", this->bram_height);
		write_byte(ofs, crc_value, file_offset, 0x72);
		write_byte(ofs, crc_value, file_offset, bram_chunk_size >> 8);
		write_byte(ofs, crc_value, file_offset, bram_chunk_size);

		for (int bram_bank = 0; bram_bank < 4; bram_bank++)
		{
			debug("BRAM: Setting bank %d.\n", bram_bank);
			write_byte(ofs, crc_value, file_offset, 0x11);
			write_byte(ofs, crc_value, file_offset, bram_bank);

			for (int offset = 0; offset < this->bram_height; offset += bram_chunk_size)
			{
				vector<bool> bram_bits;
				int width = this->bram_width;
				if(this->device == "5k" && ((bram_bank % 2) == 1))
					width = width / 2;
				for (int bram_y = 0; bram_y < bram_chunk_size; bram_y++)
				for (int bram_x = 0; bram_x < width; bram_x++)
					bram_bits.push_back(this->bram[bram_bank][bram_x][bram_y+offset]);

				debug("BRAM: Setting bank offset to %d.\n", offset);
				write_byte(ofs, crc_value, file_offset, 0x82);
				write_byte(ofs, crc_value, file_offset, offset >> 8);
				write_byte(ofs, crc_value, file_offset, offset);

				if(this->device == "5k") {
					debug("BRAM: Setting bank width to %d.\n", width);
					write_byte(ofs, crc_value, file_offset, 0x62);
					write_byte(ofs, crc_value, file_offset, (width-1) >> 8);
					write_byte(ofs, crc_value, file_offset, (width-1));
				}


                                if (!this->skip_bram_initialization) {
                                    debug("BRAM: Writing bank %d data.\n", bram_bank);
                                    write_byte(ofs, crc_value, file_offset, 0x01);
                                    write_byte(ofs, crc_value, file_offset, 0x03);
                                    for (int i = 0; i < int(bram_bits.size()); i += 8) {
                                            uint8_t byte = 0;
                                            for (int j = 0; j < 8; j++)
                                                    byte = (byte << 1) | (bram_bits[i+j] ? 1 : 0);
                                            write_byte(ofs, crc_value, file_offset, byte);
                                    }

                                    write_byte(ofs, crc_value, file_offset, 0x00);
                                    write_byte(ofs, crc_value, file_offset, 0x00);
                                }
			}
		}
	}

	debug("Writing CRC value.\n");
	write_byte(ofs, crc_value, file_offset, 0x22);
	uint8_t crc_hi = crc_value >> 8, crc_lo = crc_value;
	write_byte(ofs, crc_value, file_offset, crc_hi);
	write_byte(ofs, crc_value, file_offset, crc_lo);

	debug("Wakeup.\n");
	write_byte(ofs, crc_value, file_offset, 0x01);
	write_byte(ofs, crc_value, file_offset, 0x06);

	debug("Padding byte.\n");
	write_byte(ofs, crc_value, file_offset, 0x00);
}

void FpgaConfig::read_ascii(std::istream &ifs, bool nosleep)
{
	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Parsing ascii file..\n");

	bool got_device = false;
	this->cram.clear();
	this->bram.clear();
	this->freqrange = "low";
	this->warmboot = "enabled";

	bool reuse_line = true;
	string line, command;

	while (reuse_line || getline(ifs, line))
	{
		reuse_line = false;

		std::istringstream is(line);
		is >> command;

		if (command.empty())
			continue;

		debug("Next command: %s\n", line.c_str());

		if (command == ".comment")
		{
			this->initblop.clear();
			this->initblop.push_back(0xff);
			this->initblop.push_back(0x00);

			while (getline(ifs, line))
			{
				if (line.substr(0, 1) == ".") {
					reuse_line = true;
					break;
				}

				for (auto ch : line)
					this->initblop.push_back(ch);
				this->initblop.push_back(0);
			}

			this->initblop.push_back(0x00);
			this->initblop.push_back(0xff);
			continue;
		}

		if (command == ".device")
		{
			if (got_device)
				error("More than one .device statement.\n");

			is >> this->device;

			if (this->device == "384") {
				this->cram_width = 182;
				this->cram_height = 80;
				this->bram_width = 0;
				this->bram_height = 0;
			} else
			if (this->device == "1k") {
				this->cram_width = 332;
				this->cram_height = 144;
				this->bram_width = 64;
				this->bram_height = 2 * 128;
			} else
			if (this->device == "8k") {
				this->cram_width = 872;
				this->cram_height = 272;
				this->bram_width = 128;
				this->bram_height = 2 * 128;
			} else
			if (this->device == "5k") {
				this->cram_width = 692;
				this->cram_height = 336;
				this->bram_width = 160;
				this->bram_height = 2 * 128;
			} else
			if (this->device == "u4k") {
				this->cram_width = 692;
				this->cram_height = 176;
				this->bram_width = 80;
				this->bram_height = 2 * 128;
			} else
			if (this->device == "lm4k") {
				this->cram_width = 656;
				this->cram_height = 176;
				this->bram_width = 80;
				this->bram_height = 2 * 128;
			} else
				error("Unsupported chip type '%s'.\n", this->device.c_str());

			this->cram.resize(4);
			if(this->device == "5k") {
				for (int i = 0; i < 4; i++) {
					this->cram[i].resize(this->cram_width);
					for (int x = 0; x < this->cram_width; x++)
						this->cram[i][x].resize(((i % 2) == 1) ? (this->cram_height / 2 + 8) : this->cram_height);
				}

				this->bram.resize(4);
				for (int i = 0; i < 4; i++) {
					int width = ((i % 2) == 1) ? (this->bram_width / 2) : this->bram_width;
					this->bram[i].resize(width);
					for (int x = 0; x < width; x++)
						this->bram[i][x].resize(this->bram_height);
				}
			} else {
				for (int i = 0; i < 4; i++) {
					this->cram[i].resize(this->cram_width);
					for (int x = 0; x < this->cram_width; x++)
						this->cram[i][x].resize(this->cram_height);
				}

				this->bram.resize(4);
				for (int i = 0; i < 4; i++) {
					this->bram[i].resize(this->bram_width);
					for (int x = 0; x < this->bram_width; x++)
						this->bram[i][x].resize(this->bram_height);
				}
			}


			got_device = true;
			continue;
		}

		if (command == ".warmboot")
		{
			is >> this->warmboot;

			if (this->warmboot != "disabled" &&
			    this->warmboot != "enabled")
				error("Unknown warmboot setting '%s'.\n",
				      this->warmboot.c_str());

			continue;
		}

		// No ".nosleep" section despite sharing the same byte as .warmboot.
		// ".nosleep" is specified when icepack is invoked, which is too late.
		// So we inject the section based on command line argument.
		if (nosleep)
			this->nosleep = "enabled";
		else
			this->nosleep = "disabled";

		if (command == ".io_tile" || command == ".logic_tile" || command == ".ramb_tile" || command == ".ramt_tile" || command.substr(0, 4) == ".dsp" || command == ".ipcon_tile")
		{
			if (!got_device)
				error("Missing .device statement before %s.\n", command.c_str());

			int tile_x, tile_y;
			is >> tile_x >> tile_y;

			CramIndexConverter cic(this, tile_x, tile_y);

			if (("." + cic.tile_type + "_tile") != command)
				error("Got %s statement for %s tile %d %d.\n",
						command.c_str(), cic.tile_type.c_str(), tile_x, tile_y);

			for (int bit_y = 0; bit_y < 16 && getline(ifs, line); bit_y++)
			{
				if (line.substr(0, 1) == ".") {
					reuse_line = true;
					break;
				}

				for (int bit_x = 0; bit_x < int(line.size()) && bit_x < cic.tile_width; bit_x++)
					if (line[bit_x] == '1') {
						int cram_bank, cram_x, cram_y;
						cic.get_cram_index(bit_x, bit_y, cram_bank, cram_x, cram_y);
						this->cram[cram_bank][cram_x][cram_y] = true;
					}
			}

			continue;
		}

		if (command == ".ram_data")
		{
			if (!got_device)
				error("Missing .device statement before %s.\n", command.c_str());

			int tile_x, tile_y;
			is >> tile_x >> tile_y;

			BramIndexConverter bic(this, tile_x, tile_y);

			for (int bit_y = 0; bit_y < 16 && getline(ifs, line); bit_y++)
			{
				if (line.substr(0, 1) == ".") {
					reuse_line = true;
					break;
				}

				for (int bit_x = 256-4, ch_idx = 0; ch_idx < int(line.size()) && bit_x >= 0; bit_x -= 4, ch_idx++)
				{
					int value = -1;
					if ('0' <= line[ch_idx] && line[ch_idx] <= '9')
						value = line[ch_idx] - '0';
					if ('a' <= line[ch_idx] && line[ch_idx] <= 'f')
						value = line[ch_idx] - 'a' + 10;
					if ('A' <= line[ch_idx] && line[ch_idx] <= 'F')
						value = line[ch_idx] - 'A' + 10;
					if (value < 0)
						error("Not a hex character: '%c' (in line '%s')\n", line[ch_idx], line.c_str());

					for (int i = 0; i < 4; i++)
						if ((value & (1 << i)) != 0) {
							int bram_bank, bram_x, bram_y;
							bic.get_bram_index(bit_x+i, bit_y, bram_bank, bram_x, bram_y);
							this->bram[bram_bank][bram_x][bram_y] = true;
						}
				}
			}

			continue;
		}

		if (command == ".extra_bit")
		{
			if (!got_device)
				error("Missing .device statement before %s.\n", command.c_str());

			int cram_bank, cram_x, cram_y;
			is >> cram_bank >> cram_x >> cram_y;
			this->cram[cram_bank][cram_x][cram_y] = true;

			continue;
		}

		if (command == ".sym")
		  continue;

		if (command.substr(0, 1) == ".")
			error("Unknown statement: %s\n", command.c_str());
		error("Unexpected data line: %s\n", line.c_str());
	}
}

void FpgaConfig::write_ascii(std::ostream &ofs) const
{
	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Writing ascii file..\n");

	ofs << ".comment";
	bool insert_newline = true;
	for (auto ch : this->initblop) {
		if (ch == 0) {
			insert_newline = true;
		} else if (ch == 0xff) {
			insert_newline = false;
		} else {
			if (insert_newline)
				ofs << '\n';
			ofs << ch;
			insert_newline = false;
		}
	}

	ofs << stringf("\n.device %s\n", this->device.c_str());
	if (this->warmboot != "enabled")
		ofs << stringf(".warmboot %s\n", this->warmboot.c_str());

	// As "nosleep" is an icepack command, we do not write out a ".nosleep"
	// section. However, we parse it in read_bits() and notify the user in
	// info.

	typedef std::tuple<int, int, int> tile_bit_t;
	std::set<tile_bit_t> tile_bits;

	for (int y = 0; y <= this->chip_height()+1; y++)
	for (int x = 0; x <= this->chip_width()+1; x++)
	{
		CramIndexConverter cic(this, x, y);

		if (cic.tile_type == "corner" || cic.tile_type == "unsupported")
			continue;

		ofs << stringf(".%s_tile %d %d\n", cic.tile_type.c_str(), x, y);

		for (int bit_y = 0; bit_y < 16; bit_y++) {
			for (int bit_x = 0; bit_x < cic.tile_width; bit_x++) {
				int cram_bank, cram_x, cram_y;
				cic.get_cram_index(bit_x, bit_y, cram_bank, cram_x, cram_y);
				tile_bits.insert(tile_bit_t(cram_bank, cram_x, cram_y));
				if (cram_x > int(this->cram[cram_bank].size())) {
					error("cram_x %d (bit %d, %d) larger than bank size %lu\n", cram_x, bit_x, bit_y, this->cram[cram_bank].size());
				}
				if (cram_y > int(this->cram[cram_bank][cram_x].size())) {
					error("cram_y %d (bit %d, %d) larger than bank %d size %lu\n", cram_y, bit_x, bit_y, cram_bank, this->cram[cram_bank][cram_x].size());
				}
				ofs << (this->cram[cram_bank][cram_x][cram_y] ? '1' : '0');
			}
			ofs << '\n';
		}

		if (cic.tile_type == "ramb" && !this->bram.empty())
		{
			BramIndexConverter bic(this, x, y);
			ofs << stringf(".ram_data %d %d\n", x, y);

			for (int bit_y = 0; bit_y < 16; bit_y++) {
				for (int bit_x = 256-4; bit_x >= 0; bit_x -= 4) {
					int value = 0;
					for (int i = 0; i < 4; i++) {
						int bram_bank, bram_x, bram_y;
						bic.get_bram_index(bit_x+i, bit_y, bram_bank, bram_x, bram_y);
						if (bram_x >= int(this->bram[bram_bank].size())) {
							error("%d %d bram_x %d higher than loaded bram size %lu\n",bit_x+i, bit_y, bram_x,  this->bram[bram_bank].size());
							break;
						}
						if (bram_y >= int(this->bram[bram_bank][bram_x].size())) {
							error("bram_y %d higher than loaded bram size %lu\n", bram_y,  this->bram[bram_bank][bram_x].size());
							break;
						}
						if (this->bram[bram_bank][bram_x][bram_y])
							value += 1 << i;
					}
					ofs << "0123456789abcdef"[value];
				}
				ofs << '\n';
			}
		}
	}

	for (int i = 0; i < 4; i++)
	for (int x = 0; x < this->cram_width; x++)
	for (int y = 0; y < this->cram_height; y++)
		if (this->cram[i][x][y] && tile_bits.count(tile_bit_t(i, x, y)) == 0)
			ofs << stringf(".extra_bit %d %d %d\n", i, x, y);

#if 0
	for (int i = 0; i < 4; i++) {
		ofs << stringf(".bram_bank %d\n", i);
		for (int x = 0; x < this->bram_width; x++) {
			for (int y = 0; y < this->bram_height; y += 4)
				ofs << "0123456789abcdef"[(this->bram[i][x][y] ? 1 : 0) + (this->bram[i][x][y+1] ? 2 : 0) +
						(this->bram[i][x][y+2] ? 4 : 0) + (this->bram[i][x][y+3] ? 8 : 0)];
			ofs << '\n';
		}
	}
#endif
}

void FpgaConfig::write_cram_pbm(std::ostream &ofs, int bank_num) const
{
	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Writing cram pbm file..\n");

	ofs << "P3\n";
	ofs << stringf("%d %d\n", 2*this->cram_width, 2*this->cram_height);
	ofs << "255\n";
	uint32_t tile_type[4][this->cram_width][this->cram_height];
	for (int y = 0; y <= this->chip_height()+1; y++)
	for (int x = 0; x <= this->chip_width()+1; x++)
	{
		CramIndexConverter cic(this, x, y);

		uint32_t color = 0x000000;
		if (cic.tile_type == "io") {
			color = 0x00aa00;
		} else if (cic.tile_type == "logic") {
			if ((x + y) % 2 == 0) {
				color = 0x0000ff;
			} else {
				color = 0x0000aa;
			}
			if (x == 12 && y == 25) {
				color = 0xaa00aa;
			}
			if (x == 12 && y == 24) {
				color = 0x888888;
			}
		} else if (cic.tile_type == "ramt") {
			color = 0xff0000;
		} else if (cic.tile_type == "ramb") {
			color = 0xaa0000;
		} else if (cic.tile_type == "unsupported") {
			color = 0x333333;
		} else {
			info("%s\n", cic.tile_type.c_str());
		}

		for (int bit_y = 0; bit_y < 16; bit_y++)
		for (int bit_x = 0; bit_x < cic.tile_width; bit_x++) {
			int cram_bank, cram_x, cram_y;
			cic.get_cram_index(bit_x, bit_y, cram_bank, cram_x, cram_y);
			tile_type[cram_bank][cram_x][cram_y] = color;
		}
	}
	for (int y = 2*this->cram_height-1; y >= 0; y--) {
		for (int x = 0; x < 2*this->cram_width; x++) {
			int bank = 0, bank_x = x, bank_y = y;
			if (bank_x >= this->cram_width)
				bank |= 1, bank_x = 2*this->cram_width - bank_x - 1;
			if (bank_y >= this->cram_height)
				bank |= 2, bank_y = 2*this->cram_height - bank_y - 1;
			if (bank_num >= 0 && bank != bank_num)
				ofs << "   255 255 255";
			else if (this->cram[bank][bank_x][bank_y]) {
				ofs << "   255 255 255";
			} else {
				uint32_t color = tile_type[bank][bank_x][bank_y];
				uint8_t r = color >> 16;
				uint8_t g = color >> 8;
				uint8_t b = color & 0xff;
				ofs << stringf(" %d %d %d", r, g, b);
			}
		}
		ofs << '\n';
	}
}

void FpgaConfig::write_bram_pbm(std::ostream &ofs, int bank_num) const
{
	debug("## %s\n", __PRETTY_FUNCTION__);
	info("Writing bram pbm file..\n");

	ofs << "P1\n";
	ofs << stringf("%d %d\n", 2*this->bram_width, 2*this->bram_height);
	for (int y = 2*this->bram_height-1; y >= 0; y--) {
		for (int x = 0; x < 2*this->bram_width; x++) {
			int bank = 0, bank_x = x, bank_y = y;
			if (bank_x >= this->bram_width)
				bank |= 1, bank_x = 2*this->bram_width - bank_x - 1;
			if (bank_y >= this->bram_height)
				bank |= 2, bank_y = 2*this->bram_height - bank_y - 1;
			info("%d %d %d\n", bank, bank_x, bank_y);
			if (bank_num >= 0 && bank != bank_num)
				ofs << " 0";
			else
				ofs << (this->bram[bank][bank_x][bank_y] ? " 1" : " 0");
		}
		ofs << '\n';
	}
}

int FpgaConfig::chip_width() const
{
	if (this->device == "384") return 6;
	if (this->device == "1k") return 12;
	if (this->device == "5k") return 24;
	if (this->device == "u4k") return 24;
	if (this->device == "lm4k") return 24;
	if (this->device == "8k") return 32;
	panic("Unknown chip type '%s'.\n", this->device.c_str());
}

int FpgaConfig::chip_height() const
{
	if (this->device == "384") return 8;
	if (this->device == "1k") return 16;
	if (this->device == "5k") return 30;
	if (this->device == "u4k") return 20;
	if (this->device == "lm4k") return 20;
	if (this->device == "8k") return 32;
	panic("Unknown chip type '%s'.\n", this->device.c_str());
}

vector<int> FpgaConfig::chip_cols() const
{
	if (this->device == "384") return vector<int>({18, 54, 54, 54, 54});
	if (this->device == "1k") return vector<int>({18, 54, 54, 42, 54, 54, 54});
	if (this->device == "u4k") return vector<int>({54, 54, 54, 54, 54, 54, 42, 54, 54, 54, 54, 54, 54});
	if (this->device == "lm4k") return vector<int>({18, 54, 54, 54, 54, 54, 42, 54, 54, 54, 54, 54, 54});
	// Its IPConnect or Mutiplier block, five logic, ram, six logic.
	if (this->device == "5k") return vector<int>({54, 54, 54, 54, 54, 54, 42, 54, 54, 54, 54, 54, 54});
	if (this->device == "8k") return vector<int>({18, 54, 54, 54, 54, 54, 54, 54, 42, 54, 54, 54, 54, 54, 54, 54, 54});
	panic("Unknown chip type '%s'.\n", this->device.c_str());
}

string FpgaConfig::tile_type(int x, int y) const
{
	if ((x == 0 || x == this->chip_width()+1) && (y == 0 || y == this->chip_height()+1)) return "corner";
	// The sides on the 5k devices are IPConnect or DSP tiles
	if (this->device == "5k" && (x == 0 || x == this->chip_width()+1)) {
		if( (y == 5) || (y == 10) || (y == 15) || (y == 23))
			return "dsp0";
		if( (y == 6) || (y == 11) || (y == 16) || (y == 24))
			return "dsp1";
		if( (y == 7) || (y == 12) || (y == 17) || (y == 25))
			return "dsp2";
		if( (y == 8) || (y == 13) || (y == 18) || (y == 26))
			return "dsp3";
		return "ipcon";
	}
	
	if (this->device == "u4k" && (x == 0 || x == this->chip_width()+1)) {
		if( (y == 5) || (y == 13))
			return "dsp0";
		if( (y == 6) || (y == 14))
			return "dsp1";
		if( (y == 7) || (y == 15))
			return "dsp2";
		if( (y == 8) || (y == 16))
			return "dsp3";
		return "ipcon";
	}
	
	if ((x == 0 || x == this->chip_width()+1) || (y == 0 || y == this->chip_height()+1)) return "io";

	if (this->device == "384") return "logic";

	if (this->device == "1k") {
		if (x == 3 || x == 10) return y % 2 == 1 ? "ramb" : "ramt";
		return "logic";
	}

	if (this->device == "5k" || this->device == "u4k" || this->device == "lm4k") {
		if (x == 6 || x == 19) return y % 2 == 1 ? "ramb" : "ramt";
		return "logic";
	}

	if (this->device == "8k") {
		if (x == 8 || x == 25) return y % 2 == 1 ? "ramb" : "ramt";
		return "logic";
	}

	panic("Unknown chip type '%s'.\n", this->device.c_str());
}

int FpgaConfig::tile_width(const string &type) const
{
	if (type == "corner")        return 0;
	if (type == "logic")         return 54;
	if (type == "ramb")          return 42;
	if (type == "ramt")          return 42;
	if (type == "io")            return 18;
	if (type.substr(0, 3) == "dsp")   return 54;
	if (type == "ipcon")   return 54;

	panic("Unknown tile type '%s'.\n", type.c_str());
}

void FpgaConfig::cram_clear()
{
	for (int i = 0; i < 4; i++)
	for (int x = 0; x < this->cram_width; x++)
	for (int y = 0; y < this->cram_height; y++)
		this->cram[i][x][y] = false;
}

void FpgaConfig::cram_fill_tiles()
{
	for (int y = 0; y <= this->chip_height()+1; y++)
	for (int x = 0; x <= this->chip_width()+1; x++)
	{
		CramIndexConverter cic(this, x, y);

		for (int bit_y = 0; bit_y < 16; bit_y++)
		for (int bit_x = 0; bit_x < cic.tile_width; bit_x++) {
			int cram_bank, cram_x, cram_y;
			cic.get_cram_index(bit_x, bit_y, cram_bank, cram_x, cram_y);
			this->cram[cram_bank][cram_x][cram_y] = true;
		}
	}
}

void FpgaConfig::cram_checkerboard(int m)
{
	for (int y = 0; y <= this->chip_height()+1; y++)
	for (int x = 0; x <= this->chip_width()+1; x++)
	{
		if ((x+y) % 2 == m)
			continue;

		CramIndexConverter cic(this, x, y);

		for (int bit_y = 0; bit_y < 16; bit_y++)
		for (int bit_x = 0; bit_x < cic.tile_width; bit_x++) {
			int cram_bank, cram_x, cram_y;
			cic.get_cram_index(bit_x, bit_y, cram_bank, cram_x, cram_y);
			this->cram[cram_bank][cram_x][cram_y] = true;
		}
	}
}

CramIndexConverter::CramIndexConverter(const FpgaConfig *fpga, int tile_x, int tile_y)
{
	this->fpga = fpga;
	this->tile_x = tile_x;
	this->tile_y = tile_y;


	this->tile_type = fpga->tile_type(this->tile_x, this->tile_y);
	this->tile_width = fpga->tile_width(this->tile_type);

	auto chip_width = fpga->chip_width();
	auto chip_height = fpga->chip_height();
	auto chip_cols = fpga->chip_cols();

	this->left_right_io = this->tile_x == 0 || this->tile_x == chip_width+1;
	this->right_half = this->tile_x > chip_width / 2;
	if (this->fpga->device == "5k") {
		this->top_half = this->tile_y > (chip_height * 2 / 3);
	} else {
		this->top_half = this->tile_y > chip_height / 2;
	}

	this->bank_num = 0;
	if (this->top_half) this->bank_num |= 1;
	if (this->right_half) this->bank_num |= 2;

	this->bank_tx = this->right_half ? chip_width  + 1 - this->tile_x : this->tile_x;
	this->bank_ty = this->top_half   ? chip_height + 1 - this->tile_y : this->tile_y;

	this->bank_xoff = 0;
	for (int i = 0; i < this->bank_tx; i++)
		this->bank_xoff += chip_cols.at(i);

	this->bank_yoff = 16 * this->bank_ty;

	this->column_width = chip_cols.at(this->bank_tx);
}

void CramIndexConverter::get_cram_index(int bit_x, int bit_y, int &cram_bank, int &cram_x, int &cram_y) const
{
	static const int io_top_bottom_permx[18] = {23, 25, 26, 27, 16, 17, 18, 19, 20, 14, 32, 33, 34, 35, 36, 37, 4, 5};
	static const int io_top_bottom_permy[16] = {0, 1, 3, 2, 4, 5, 7, 6, 8, 9, 11, 10, 12, 13, 15, 14};

	cram_bank = bank_num;

	if (tile_type == "io")
	{
		if (left_right_io)
		{
			cram_x = bank_xoff + column_width - 1 - bit_x;

			if (top_half)
				cram_y = bank_yoff + 15 - bit_y;
			else
				cram_y = bank_yoff + bit_y;
		}
		else
		{
			cram_y = bank_yoff + 15 - io_top_bottom_permy[bit_y];

			if (right_half)
				cram_x = bank_xoff + column_width - 1 - io_top_bottom_permx[bit_x];
			else
				cram_x = bank_xoff + io_top_bottom_permx[bit_x];
		}
	}
	else
	{
		if (right_half)
			cram_x = bank_xoff + column_width - 1 - bit_x;
		else
			cram_x = bank_xoff + bit_x;

		if (top_half)
			cram_y = bank_yoff + (15 - bit_y);
		else
			cram_y = bank_yoff + bit_y;
	}
}

BramIndexConverter::BramIndexConverter(const FpgaConfig *fpga, int tile_x, int tile_y)
{
	this->fpga = fpga;
	this->tile_x = tile_x;
	this->tile_y = tile_y;

	auto chip_width = fpga->chip_width();
	auto chip_height = fpga->chip_height();

	bool right_half = this->tile_x > chip_width / 2;
	bool top_half = this->tile_y > chip_height / 2;
	// The UltraPlus 5k line is special because the top quarter of the chip is
	// used for SRAM instead of logic. Therefore the bitstream for the top two
	// quadrants are half the height of the bottom.
	if (this->fpga->device == "5k") {
		top_half = this->tile_y > (2 * chip_height / 3);
	}

	this->bank_num = 0;
	int y_offset = this->tile_y - 1;
	if (this->fpga->device == "5k") {
		if (top_half) {
			this->bank_num |= 1;
			y_offset = this->tile_y - (2 * chip_height / 3);
		} else {
			//y_offset = this->tile_y - (2 * chip_height / 3);
		}
	} else if (top_half) {
		this->bank_num |= 1;
		y_offset = this->tile_y - chip_height / 2;
	}
	if (right_half) this->bank_num |= 2;

	this->bank_off = 16 * (y_offset / 2);
}

void BramIndexConverter::get_bram_index(int bit_x, int bit_y, int &bram_bank, int &bram_x, int &bram_y) const
{
	int index = 256 * bit_y + (16*(bit_x/16) + 15 - bit_x%16);
	bram_bank = bank_num;
	bram_x = bank_off + index % 16;
	bram_y = index / 16;
}


// ==================================================================
// Main program

void usage()
{
	log("\n");
	log("Usage: icepack [options] [input-file [output-file]]\n");
	log("\n");
	log("    -u\n");
	log("        unpack mode (implied when called as 'iceunpack')\n");
	log("\n");
	log("    -v\n");
	log("        verbose (repeat to increase verbosity)\n");
	log("\n");
	log("    -s\n");
	log("        disable final deep-sleep SPI flash command after bitstream is loaded\n");
	log("\n");
	log("    -b\n");
	log("        write cram bitmap as netpbm file\n");
	log("\n");
	log("    -f\n");
	log("        write cram bitmap (fill tiles) as netpbm file\n");
	log("\n");
	log("    -c\n");
	log("        write cram bitmap (checkerboard) as netpbm file\n");
	log("        repeat to flip the selection of tiles\n");
	log("\n");
	log("    -r\n");
	log("        write bram data, not cram, to the netpbm file\n");
	log("\n");
	log("    -B0, -B1, -B2, -B3\n");
	log("        only include the specified bank in the netpbm file\n");
	log("\n");
	log("    -n\n");
	log("        skip initializing BRAM\n");
	log("\n");
	exit(1);
}

int main(int argc, char **argv)
{
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

	vector<string> parameters;
	bool unpack_mode = false;
	bool nosleep_mode = false;
	bool netpbm_mode = false;
	bool netpbm_bram = false;
	bool netpbm_fill_tiles = false;
	bool netpbm_checkerboard = false;
        bool skip_bram_initialization = false;
	int netpbm_banknum = -1;
	int checkerboard_m = 1;

	for (int i = 0; argv[0][i]; i++)
		if (string(argv[0]+i) == "iceunpack")
			unpack_mode = true;

	for (int i = 1; i < argc; i++)
	{
		string arg(argv[i]);

		if (arg[0] == '-' && arg.size() > 1) {
			for (int i = 1; i < int(arg.size()); i++)
				if (arg[i] == 'u') {
					unpack_mode = true;
				} else if (arg[i] == 'b') {
					netpbm_mode = true;
				} else if (arg[i] == 'r') {
					netpbm_mode = true;
					netpbm_bram = true;
				} else if (arg[i] == 'f') {
					netpbm_mode = true;
					netpbm_fill_tiles = true;
				} else if (arg[i] == 'c') {
					netpbm_mode = true;
					netpbm_checkerboard = true;
					checkerboard_m = !checkerboard_m;
				} else if (arg[i] == 'B') {
					netpbm_mode = true;
					netpbm_banknum = arg[++i] - '0';
				} else if (arg[i] == 's') {
					nosleep_mode = true;
				} else if (arg[i] == 'v') {
					log_level++;
				} else if (arg[i] == 'n') {
					skip_bram_initialization = true;
				} else
					usage();
			continue;
		}

		parameters.push_back(arg);
	}

	std::ifstream ifs;
	std::ofstream ofs;

	std::istream *isp;
	std::ostream *osp;

	if (parameters.size() >= 1 && parameters[0] != "-") {
		ifs.open(parameters[0], std::ios::binary);
		if (!ifs.is_open())
			error("Failed to open input file.\n");
		isp = &ifs;
	} else {
		isp = &std::cin;
	}

	if (parameters.size() >= 2 && parameters[1] != "-") {
		ofs.open(parameters[1], std::ios::binary);
		if (!ofs.is_open())
			error("Failed to open output file.\n");
		osp = &ofs;
	} else {
		osp = &std::cout;
	}

	if (parameters.size() > 2)
		usage();

	FpgaConfig fpga_config;
        
        fpga_config.skip_bram_initialization = skip_bram_initialization;

	if (unpack_mode) {
		fpga_config.read_bits(*isp);
		if (!netpbm_mode)
			fpga_config.write_ascii(*osp);
	} else {
		fpga_config.read_ascii(*isp, nosleep_mode);
		if (!netpbm_mode)
			fpga_config.write_bits(*osp);
	}

	if (netpbm_checkerboard) {
		fpga_config.cram_clear();
		fpga_config.cram_checkerboard(checkerboard_m);
	}

	info("netpbm\n");

	if (netpbm_fill_tiles)
		fpga_config.cram_fill_tiles();

	info("fill done\n");

	if (netpbm_mode) {
		if (netpbm_bram)
			fpga_config.write_bram_pbm(*osp, netpbm_banknum);
		else
			fpga_config.write_cram_pbm(*osp, netpbm_banknum);
	}

	info("Done.\n");
	return 0;
}
