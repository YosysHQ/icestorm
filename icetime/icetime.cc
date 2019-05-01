//
//  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
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

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <string.h>
#include <stdarg.h>

#include <algorithm>
#include <functional>
#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

std::string find_chipdb(std::string config_device);

// add this number of ns as estimate for clock distribution mismatch
#define GLOBAL_CLK_DIST_JITTER 0.1

FILE *fin = nullptr, *fout = nullptr, *frpt = nullptr;
FILE *fjson = nullptr;
bool verbose = false;
bool max_span_hack = false;
bool json_firstentry = true;

std::string config_device, device_type, selected_package, chipdbfile;
std::vector<std::vector<std::string>> config_tile_type;
std::vector<std::vector<std::vector<std::vector<bool>>>> config_bits;
std::map<std::tuple<int, int, int>, std::string> pin_pos;
std::map<std::string, std::string> pin_names;
std::set<std::tuple<int, int, int>> extra_bits;
std::set<std::string> io_names;

std::map<int, std::string> net_symbols;

bool get_config_bit(int tile_x, int tile_y, int bit_row, int bit_col)
{
	if (int(config_bits.size()) < tile_x)
		return false;

	if (int(config_bits[tile_x].size()) < tile_y)
		return false;

	if (int(config_bits[tile_x][tile_y].size()) < bit_row)
		return false;

	if (int(config_bits[tile_x][tile_y][bit_row].size()) < bit_col)
		return false;

	return config_bits[tile_x][tile_y][bit_row][bit_col];
}

struct net_segment_t
{
	int x, y, net;
	std::string name;

	net_segment_t() :
		x(-1), y(-1), net(-1) { }

	net_segment_t(int x, int y, int net, std::string name) :
		x(x), y(y), net(net), name(name) { }

	bool operator==(const net_segment_t &other) const {
		return (x == other.x) && (y == other.y) && (name == other.name);
	}

	bool operator!=(const net_segment_t &other) const {
		return (x != other.x) || (y != other.y) || (name != other.name);
	}

	bool operator<(const net_segment_t &other) const {
		if (x != other.x)
			return x < other.x;
		if (y != other.y)
			return y < other.y;
		return name < other.name;
	}
};

std::set<net_segment_t> segments;
std::map<int, std::set<net_segment_t>> net_to_segments;
std::map<std::tuple<int, int, std::string>, int> x_y_name_net;
std::map<std::tuple<int, int, int>, net_segment_t> x_y_net_segment;
std::map<int, std::set<int>> net_buffers, net_rbuffers, net_routing;
std::map<std::pair<int, int>, std::pair<int, int>> connection_pos;
std::set<int> used_nets, graph_nets;

std::set<net_segment_t> interconn_src, interconn_dst;
std::set<int> no_interconn_net;
int tname_cnt = 0;

// netlist_cell_ports[cell_name][port_name] = port_expr
std::map<std::string, std::map<std::string, std::string>> netlist_cell_ports;
std::map<std::string, std::map<std::string, std::string>> netlist_cell_params;
std::map<std::string, std::string> netlist_cell_types;

std::set<std::string> extra_wires;
std::vector<std::string> extra_vlog;
std::map<std::string, std::string> net_assignments;
std::set<int> declared_nets;
int dangling_cnt = 0;

std::map<std::string, std::vector<std::pair<int, int>>> logic_tile_bits,
		io_tile_bits, ramb_tile_bits, ramt_tile_bits, ipcon_tile_bits, dsp0_tile_bits,
		dsp1_tile_bits, dsp2_tile_bits, dsp3_tile_bits;

std::map<std::tuple<std::string, int, int, int>,
				 std::map<std::string, std::tuple<int, int, std::string>>> extra_cells;

std::string vstringf(const char *fmt, va_list ap)
{
	std::string string;
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

std::string stringf(const char *fmt, ...)
{
	std::string string;
	va_list ap;

	va_start(ap, fmt);
	string = vstringf(fmt, ap);
	va_end(ap);

	return string;
}

std::string tname()
{
	return stringf("t%d", tname_cnt++);
}

std::string net_name(int net)
{
	declared_nets.insert(net);
	return stringf("net_%d", net);
}

std::string seg_name(const net_segment_t &seg, int idx = 0)
{
	std::string str = stringf("seg_%d_%d_%s_%d", seg.x, seg.y, seg.name.c_str(), seg.net);
	for (auto &ch : str)
		if (ch == '/') ch = '_';
	if (idx != 0)
		str += stringf("_i%d", idx);
	extra_wires.insert(str);
	return str;
}

void read_pcf(const char *filename)
{
	FILE *f = fopen(filename, "r");
	if (f == nullptr) {
		perror("Can't open pcf file");
		exit(1);
	}

	char buffer[128];

	while (fgets(buffer, 128, f))
	{
		for (int i = 0; buffer[i]; i++)
			if (buffer[i] == '#') {
				buffer[i] = 0;
				break;
			}

		const char *tok = strtok(buffer, " \t\r\n");
		if (tok == nullptr || strcmp(tok, "set_io"))
			continue;

		std::vector<std::string> args;
		while ((tok = strtok(nullptr, " \t\r\n")) != nullptr) {
			if (!strcmp(tok, "--warn-no-port"))
				continue;
			args.push_back(tok);
		}

		assert(args.size() == 2);
		pin_names[args[1]] = args[0];
	}

	fclose(f);
}

void read_config()
{
	constexpr size_t line_buf_size = 65536;
	char buffer[line_buf_size];
	int tile_x, tile_y, line_nr = -1;

	while (fgets(buffer, line_buf_size, fin))
	{
		if (buffer[strlen(buffer) - 1] != '\n')
		{
			fprintf(stderr, "Input file contains very long lines.\n");
			fprintf(stderr, "icetime cannot process it.\n");
			exit(1);
		}

		if (buffer[0] == '.')
		{
			line_nr = -1;
			const char *tok = strtok(buffer, " \t\r\n");

			if (!strcmp(tok, ".device"))
			{
				config_device = strtok(nullptr, " \t\r\n");
			} else
			if (!strcmp(tok, ".io_tile") || !strcmp(tok, ".logic_tile") ||
					!strcmp(tok, ".ramb_tile") || !strcmp(tok, ".ramt_tile") ||
				  !strcmp(tok, ".ipcon_tile") || !strcmp(tok, ".dsp0_tile") ||
				  !strcmp(tok, ".dsp1_tile") || !strcmp(tok, ".dsp2_tile") ||
				  !strcmp(tok, ".dsp3_tile"))
			{
				line_nr = 0;
				tile_x = atoi(strtok(nullptr, " \t\r\n"));
				tile_y = atoi(strtok(nullptr, " \t\r\n"));

				if (tile_x >= int(config_tile_type.size())) {
					config_tile_type.resize(tile_x+1);
					config_bits.resize(tile_x+1);
				}

				if (tile_y >= int(config_tile_type.at(tile_x).size())) {
					config_tile_type.at(tile_x).resize(tile_y+1);
					config_bits.at(tile_x).resize(tile_y+1);
				}

				if (!strcmp(tok, ".io_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "io";
				if (!strcmp(tok, ".logic_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "logic";
				if (!strcmp(tok, ".ramb_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "ramb";
				if (!strcmp(tok, ".ramt_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "ramt";
				if (!strcmp(tok, ".dsp0_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "dsp0";
				if (!strcmp(tok, ".dsp1_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "dsp1";
				if (!strcmp(tok, ".dsp2_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "dsp2";
				if (!strcmp(tok, ".dsp3_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "dsp3";
				if (!strcmp(tok, ".ipcon_tile"))
					config_tile_type.at(tile_x).at(tile_y) = "ipcon";
			} else
			if (!strcmp(tok, ".extra_bit")) {
				int b = atoi(strtok(nullptr, " \t\r\n"));
				int x = atoi(strtok(nullptr, " \t\r\n"));
				int y = atoi(strtok(nullptr, " \t\r\n"));
				std::tuple<int, int, int> key(b, x, y);
				extra_bits.insert(key);
			} else
			if (!strcmp(tok, ".sym")) {
				int net = atoi(strtok(nullptr, " \t\r\n"));
				const char *name = strtok(nullptr, " \t\r\n");
				net_symbols[net] = name;
			}
		} else
		if (line_nr >= 0)
		{
			assert(int(config_bits.at(tile_x).at(tile_y).size()) == line_nr);
			config_bits.at(tile_x).at(tile_y).resize(line_nr+1);
			for (int i = 0; buffer[i] == '0' || buffer[i] == '1'; i++)
				config_bits.at(tile_x).at(tile_y).at(line_nr).push_back(buffer[i] == '1');
			line_nr++;
		}
	}
}

void read_chipdb()
{
	char buffer[1024];
	std::string filepath = chipdbfile;

	if (filepath.empty())
		filepath = find_chipdb(config_device);
	if (filepath.empty()) {
		fprintf(stderr, "Can't find chipdb file for device %s\n", config_device.c_str());
		exit(1);
	}

	FILE *fdb = fopen(filepath.c_str(), "r");
	if (fdb == nullptr) {
		perror("Can't open chipdb file");
		exit(1);
	}

	std::string mode;
	int current_net = -1;
	int tile_x = -1, tile_y = -1, cell_z = -1;
	std::string thiscfg;
	std::string cellname;

	std::vector<std::vector<int>> gbufin;
	std::vector<std::vector<int>> gbufpin;
	std::set<std::string> extrabitfunc;

	while (fgets(buffer, 1024, fdb))
	{
		if (buffer[0] == '#')
			continue;

		const char *tok = strtok(buffer, " \t\r\n");
		if (tok == nullptr)
			continue;

		if (tok[0] == '.')
		{
			mode = tok;

			if (mode == ".pins")
			{
				if (strtok(nullptr, " \t\r\n") != selected_package)
					mode = "";
				continue;
			}

			if (mode == ".net")
			{
				current_net = atoi(strtok(nullptr, " \t\r\n"));
				continue;
			}

			if (mode == ".buffer" || mode == ".routing")
			{
				tile_x = atoi(strtok(nullptr, " \t\r\n"));
				tile_y = atoi(strtok(nullptr, " \t\r\n"));
				current_net = atoi(strtok(nullptr, " \t\r\n"));

				thiscfg = "";
				while ((tok = strtok(nullptr, " \t\r\n")) != nullptr) {
					int bit_row, bit_col, rc;
					rc = sscanf(tok, "B%d[%d]", &bit_row, &bit_col);
					assert(rc == 2);
					thiscfg.push_back(get_config_bit(tile_x, tile_y, bit_row, bit_col) ? '1' : '0');
				}
				continue;
			}

			if (mode == ".extra_cell") {
				tile_x = atoi(strtok(nullptr, " \t\r\n"));
				tile_y = atoi(strtok(nullptr, " \t\r\n"));
				// For legacy reasons, extra_cell may be X Y name or X Y Z name
				const char *z_or_name = strtok(nullptr, " \t\r\n");
				if(isdigit(z_or_name[0])) {
					cell_z = atoi(z_or_name);
					cellname = std::string(strtok(nullptr, " \t\r\n"));
				} else {
					cell_z = 0;
					cellname = std::string(z_or_name);
				}
				extra_cells[std::make_tuple(cellname, tile_x, tile_y, cell_z)] = {};
				continue;
			}

			continue;
		}

		if (mode == ".pins") {
			int pos_x = atoi(strtok(nullptr, " \t\r\n"));
			int pos_y = atoi(strtok(nullptr, " \t\r\n"));
			int pos_z = atoi(strtok(nullptr, " \t\r\n"));
			std::tuple<int, int, int> key(pos_x, pos_y, pos_z);
			pin_pos[key] = tok;
		}

		if (mode == ".net") {
			int tile_x = atoi(tok);
			int tile_y = atoi(strtok(nullptr, " \t\r\n"));
			std::string segment_name = strtok(nullptr, " \t\r\n");
			net_segment_t seg(tile_x, tile_y, current_net, segment_name);
			std::tuple<int, int, std::string> x_y_name(tile_x, tile_y, segment_name);
			net_to_segments[current_net].insert(seg);
			segments.insert(seg);
		}

		if (mode == ".buffer" && !strcmp(tok, thiscfg.c_str())) {
			int other_net = atoi(strtok(nullptr, " \t\r\n"));
			net_rbuffers[current_net].insert(other_net);
			net_buffers[other_net].insert(current_net);
			connection_pos[std::pair<int, int>(current_net, other_net)] =
					connection_pos[std::pair<int, int>(other_net, current_net)] =
					std::pair<int, int>(tile_x, tile_y);
			used_nets.insert(current_net);
			used_nets.insert(other_net);
		}

		if (mode == ".routing" && !strcmp(tok, thiscfg.c_str())) {
			int other_net = atoi(strtok(nullptr, " \t\r\n"));
			net_routing[current_net].insert(other_net);
			net_routing[other_net].insert(current_net);
			connection_pos[std::pair<int, int>(current_net, other_net)] =
					connection_pos[std::pair<int, int>(other_net, current_net)] =
					std::pair<int, int>(tile_x, tile_y);
			used_nets.insert(current_net);
			used_nets.insert(other_net);
		}

		if (mode == ".gbufin" || mode == ".gbufpin") {
			std::vector<int> items;
			while (tok != nullptr) {
				items.push_back(atoi(tok));
				tok = strtok(nullptr, " \t\r\n");
			}
			if (mode == ".gbufin")
				gbufin.push_back(items);
			else
				gbufpin.push_back(items);
		}

		if (mode == ".logic_tile_bits" || mode == ".io_tile_bits" || mode == ".ramb_tile_bits" || mode == ".ramt_tile_bits" ||
				mode == ".ipcon_tile_bits" || mode == ".dsp0_tile_bits" || mode == ".dsp1_tile_bits" || mode == ".dsp2_tile_bits" || mode == ".dsp3_tile_bits") {
			std::vector<std::pair<int, int>> items;
			while (1) {
				const char *s = strtok(nullptr, " \t\r\n");
				if (s == nullptr)
					break;
				std::pair<int, int> item;
				int rc = sscanf(s, "B%d[%d]", &item.first, &item.second);
				assert(rc == 2);
				items.push_back(item);
			}
			if (mode == ".logic_tile_bits")
				logic_tile_bits[tok] = items;
			if (mode == ".io_tile_bits")
				io_tile_bits[tok] = items;
			if (mode == ".ramb_tile_bits")
				ramb_tile_bits[tok] = items;
			if (mode == ".ramt_tile_bits")
				ramt_tile_bits[tok] = items;
			if (mode == ".ipcon_tile_bits")
				ipcon_tile_bits[tok] = items;
			if (mode == ".dsp0_tile_bits")
				dsp0_tile_bits[tok] = items;
			if (mode == ".dsp1_tile_bits")
				dsp1_tile_bits[tok] = items;
			if (mode == ".dsp2_tile_bits")
				dsp2_tile_bits[tok] = items;
			if (mode == ".dsp3_tile_bits")
				dsp3_tile_bits[tok] = items;
		}

		if (mode == ".extra_bits") {
			int b = atoi(strtok(nullptr, " \t\r\n"));
			int x = atoi(strtok(nullptr, " \t\r\n"));
			int y = atoi(strtok(nullptr, " \t\r\n"));
			std::tuple<int, int, int> key(b, x, y);
			if (extra_bits.count(key))
				extrabitfunc.insert(tok);
		}

		if(mode == ".extra_cell") {
			std::string key = std::string(tok);
			if(key != "LOCKED") {
				int x = atoi(strtok(nullptr, " \t\r\n"));
				int y = atoi(strtok(nullptr, " \t\r\n"));
				std::string name = std::string(strtok(nullptr, " \t\r\n"));
				extra_cells[make_tuple(cellname, tile_x, tile_y, cell_z)][key] = make_tuple(x, y, name);
			}

		}
	}

	fclose(fdb);

	// purge unused nets from memory
	int max_net = net_to_segments.rbegin()->first;
	for (int net = 0; net <= max_net; net++)
	{
		if (used_nets.count(net))
			continue;

		for (auto seg : net_to_segments[net])
			segments.erase(seg);
		net_to_segments.erase(net);

		for (auto other : net_buffers[net])
			net_rbuffers[other].erase(net);
		net_buffers.erase(net);

		for (auto other : net_rbuffers[net])
			net_buffers[other].erase(net);
		net_rbuffers.erase(net);

		for (auto other : net_routing[net])
			net_routing[other].erase(net);
		net_routing.erase(net);
	}

	// create index
	for (auto seg : segments) {
		std::tuple<int, int, int> key(seg.x, seg.y, seg.net);
		x_y_net_segment[key] = seg;
	}
	for (auto seg : segments) {
		std::tuple<int, int, std::string> key(seg.x, seg.y, seg.name);
		x_y_name_net[key] = seg.net;
	}

	for (auto &it : gbufin)
	{
		int x = it[0], y = it[1], g = it[2];

		std::tuple<int, int, std::string> fabout_x_y_name(x, y, "fabout");
		std::tuple<int, int, std::string> glbl_x_y_name(x, y, stringf("glb_netwk_%d", g));

		if (!x_y_name_net.count(fabout_x_y_name) || !x_y_name_net.count(glbl_x_y_name))
			continue;

		int fabout_net = x_y_name_net.at(fabout_x_y_name);
		int glbl_net = x_y_name_net.at(glbl_x_y_name);

		assert(used_nets.count(fabout_net));
		assert(used_nets.count(glbl_net));

		net_rbuffers[glbl_net].insert(fabout_net);
		net_buffers[fabout_net].insert(glbl_net);
		connection_pos[std::pair<int, int>(glbl_net, fabout_net)] =
				connection_pos[std::pair<int, int>(fabout_net, glbl_net)] =
				std::pair<int, int>(x, y);
	}

	if (verbose)
	{
		for (int net : used_nets)
		{
			printf("// NET %d:\n", net);
			for (auto seg : net_to_segments[net])
				printf("//  SEG %d %d %s\n", seg.x, seg.y, seg.name.c_str());
			for (auto other : net_buffers[net])
				printf("//  BUFFER %d %d %d\n", connection_pos[std::pair<int, int>(net, other)].first,
						connection_pos[std::pair<int, int>(net, other)].second, other);
			for (auto other : net_rbuffers[net])
				printf("//  RBUFFER %d %d %d\n", connection_pos[std::pair<int, int>(net, other)].first,
						connection_pos[std::pair<int, int>(net, other)].second, other);
			for (auto other : net_routing[net])
				printf("//  ROUTE %d %d %d\n", connection_pos[std::pair<int, int>(net, other)].first,
						connection_pos[std::pair<int, int>(net, other)].second, other);
		}
	}
}

bool is_primary(std::string cell_name, std::string out_port)
{
	auto cell_type = netlist_cell_types[cell_name];

	if (cell_type == "SB_RAM40_4K")
		return true;

	if (cell_type == "LogicCell40" && out_port == "lcout")
	{
		// SEQ_MODE = "4'bX...";
		bool dff_enable = netlist_cell_params[cell_name]["SEQ_MODE"][3] == '1';
		return dff_enable;
	}

	if (cell_type == "PRE_IO")
		return true;

	if (cell_type == "SB_SPRAM256KA")
		return true;

	std::string dsp_prefix = "SB_MAC16";
	if(cell_type.substr(0, dsp_prefix.length()) == dsp_prefix)
			return (cell_type != "SB_MAC16_MUL_U_16X16_BYPASS" && cell_type != "SB_MAC16_MUL_U_8X8_BYPASS"
							&& cell_type != "SB_MAC16_ADS_U_16P16_BYPASS" && cell_type != "SB_MAC16_ADS_U_32P32_BYPASS");

	return false;
}

const std::set<std::string> &get_inports(std::string cell_type)
{
	static bool first_call = true;
	static std::map<std::string, std::set<std::string>> inports_map;

	if (first_call)
	{
		first_call = false;

		inports_map["Span4Mux_h0"] = { "I" };
		inports_map["Span4Mux_h1"] = { "I" };
		inports_map["Span4Mux_h2"] = { "I" };
		inports_map["Span4Mux_h3"] = { "I" };
		inports_map["Span4Mux_h4"] = { "I" };

		inports_map["Span4Mux_v0"] = { "I" };
		inports_map["Span4Mux_v1"] = { "I" };
		inports_map["Span4Mux_v2"] = { "I" };
		inports_map["Span4Mux_v3"] = { "I" };
		inports_map["Span4Mux_v4"] = { "I" };

		inports_map["Span12Mux_h0"] = { "I" };
		inports_map["Span12Mux_h1"] = { "I" };
		inports_map["Span12Mux_h2"] = { "I" };
		inports_map["Span12Mux_h3"] = { "I" };
		inports_map["Span12Mux_h4"] = { "I" };
		inports_map["Span12Mux_h5"] = { "I" };
		inports_map["Span12Mux_h6"] = { "I" };
		inports_map["Span12Mux_h7"] = { "I" };
		inports_map["Span12Mux_h8"] = { "I" };
		inports_map["Span12Mux_h9"] = { "I" };
		inports_map["Span12Mux_h10"] = { "I" };
		inports_map["Span12Mux_h11"] = { "I" };
		inports_map["Span12Mux_h12"] = { "I" };

		inports_map["Span12Mux_v0"] = { "I" };
		inports_map["Span12Mux_v1"] = { "I" };
		inports_map["Span12Mux_v2"] = { "I" };
		inports_map["Span12Mux_v3"] = { "I" };
		inports_map["Span12Mux_v4"] = { "I" };
		inports_map["Span12Mux_v5"] = { "I" };
		inports_map["Span12Mux_v6"] = { "I" };
		inports_map["Span12Mux_v7"] = { "I" };
		inports_map["Span12Mux_v8"] = { "I" };
		inports_map["Span12Mux_v9"] = { "I" };
		inports_map["Span12Mux_v10"] = { "I" };
		inports_map["Span12Mux_v11"] = { "I" };
		inports_map["Span12Mux_v12"] = { "I" };

		inports_map["Odrv4"] = { "I" };
		inports_map["Odrv12"] = { "I" };
		inports_map["Sp12to4"] = { "I" };

		inports_map["InMux"] = { "I" };
		inports_map["IoInMux"] = { "I" };
		inports_map["IoSpan4Mux"] = { "I" };
		inports_map["IpInMux"] = { "I" };
		inports_map["IpOutMux"] = { "I" };
		inports_map["LocalMux"] = { "I" };
		inports_map["CEMux"] = { "I" };
		inports_map["SRMux"] = { "I" };
		inports_map["ClkMux"] = { "I" };
		inports_map["CascadeBuf"] = { "I" };
		inports_map["CascadeMux"] = { "I" };
		inports_map["GlobalMux"] = { "I" };
		inports_map["gio2CtrlBuf"] = { "I" };

		inports_map["ICE_GB"] = { "USERSIGNALTOGLOBALBUFFER" };
		inports_map["ICE_CARRY_IN_MUX"] = { "carryinitin" };

		inports_map["LogicCell40"] = { "clk", "carryin", "in0", "in1", "in2", "in3", "sr", "ce" };
		inports_map["PRE_IO"] = { "INPUTCLK", "OUTPUTCLK", "LATCHINPUTVALUE", "CLOCKENABLE", "OUTPUTENABLE", "DOUT1", "DOUT0", "PADIN" };

		inports_map["SB_RAM40_4K"] = { "RCLK", "RCLKE", "RE", "WCLK", "WCLKE", "WE" };

		for (int i = 0; i < 16; i++) {
			inports_map["SB_RAM40_4K"].insert(stringf("MASK[%d]", i));
			inports_map["SB_RAM40_4K"].insert(stringf("WDATA[%d]", i));
		}

		for (int i = 0; i < 11; i++) {
			inports_map["SB_RAM40_4K"].insert(stringf("RADDR[%d]", i));
			inports_map["SB_RAM40_4K"].insert(stringf("WADDR[%d]", i));
		}

		inports_map["SB_MAC16"] = { "CLK", "CE", "AHOLD", "BHOLD", "CHOLD", "DHOLD", "IRSTTOP", "IRSTBOT", "ORSTTOP", "ORSTBOT",
																"OLOADTOP", "OLOADBOT", "ADDSUBTOP", "ADDSUBBOT", "OHOLDTOP", "OHOLDBOT", "CI", "ACCUMCI",
																"SIGNEXTIN"};
		for (int i = 0; i < 16; i++) {
			inports_map["SB_MAC16"].insert(stringf("C[%d]", i));
			inports_map["SB_MAC16"].insert(stringf("A[%d]", i));
			inports_map["SB_MAC16"].insert(stringf("B[%d]", i));
			inports_map["SB_MAC16"].insert(stringf("D[%d]", i));
		}

		inports_map["SB_SPRAM256KA"] = { "WREN", "CHIPSELECT", "CLOCK", "STANDBY", "SLEEP", "POWEROFF",
																		 "MASKWREN[0]", "MASKWREN[1]", "MASKWREN[2]", "MASKWREN[3]"};

	  for (int i = 0; i < 16; i++) {
			inports_map["SB_SPRAM256KA"].insert(stringf("DATAIN[%d]", i));
		}

		for (int i = 0; i < 14; i++) {
			inports_map["SB_SPRAM256KA"].insert(stringf("ADDRESS[%d]", i));
		}

		inports_map["INTERCONN"] = { "I" };
	}


	std::string dsp_prefix = "SB_MAC16";

	if(cell_type.substr(0, dsp_prefix.length()) == dsp_prefix)
		cell_type = "SB_MAC16";

	if (inports_map.count(cell_type) == 0) {
		fprintf(stderr, "Missing entry in inports_map for cell type %s!\n", cell_type.c_str());
		exit(1);
	}


	return inports_map.at(cell_type);
}

double get_delay_lp384(std::string cell_type, std::string in_port, std::string out_port);
double get_delay_lp1k(std::string cell_type, std::string in_port, std::string out_port);
double get_delay_lp8k(std::string cell_type, std::string in_port, std::string out_port);
double get_delay_hx1k(std::string cell_type, std::string in_port, std::string out_port);
double get_delay_hx8k(std::string cell_type, std::string in_port, std::string out_port);
double get_delay_up5k(std::string cell_type, std::string in_port, std::string out_port);

double get_delay(std::string cell_type, std::string in_port, std::string out_port)
{
	if (cell_type == "INTERCONN")
		return 0;

	if (device_type == "lp384")
		return get_delay_lp384(cell_type, in_port, out_port);

	if (device_type == "lp1k")
		return get_delay_lp1k(cell_type, in_port, out_port);

	if (device_type == "lp8k")
		return get_delay_lp8k(cell_type, in_port, out_port);

	if (device_type == "hx1k")
		return get_delay_hx1k(cell_type, in_port, out_port);

	if (device_type == "hx8k")
		return get_delay_hx8k(cell_type, in_port, out_port);

	if (device_type == "up5k")
		return get_delay_up5k(cell_type, in_port, out_port);
	fprintf(stderr, "No built-in timing database for '%s' devices!\n", device_type.c_str());
	exit(1);
}

struct TimingAnalysis
{
	// net_driver[<net_name>] = { <cell_name>, <cell_port> }
	std::map<std::string, std::pair<std::string, std::string>> net_driver;

	// net_max_setup[<net_name>] = { <setup_time>, <cell_name>, <cell_port> }
	std::map<std::string, std::tuple<double, std::string, std::string>> net_max_setup;

	// net_max_path_parent[<net_name>] = { <parent_net>, <cell_name>, <inport>, <outport>, <delay> }
	std::map<std::string, std::tuple<std::string, std::string, std::string, std::string, double>> net_max_path_parent;

	std::map<std::string, double> net_max_path_delay;
	std::string global_max_path_net;
	double global_max_path_delay;

	bool interior_timing;
	std::set<std::string> interior_nets;

	double calc_net_max_path_delay(const std::string &net)
	{
		if (net_max_path_delay.count(net))
			return net_max_path_delay.at(net);

		if (net_driver.count(net) == 0)
			return 0;

		double max_path_delay = -1e6;
		net_max_path_delay[net] = 1e6;

		auto &driver_cell = net_driver.at(net).first;
		auto &driver_port = net_driver.at(net).second;
		auto &driver_type = netlist_cell_types.at(driver_cell);

		if (is_primary(driver_cell, driver_port)) {
			if (interior_timing && driver_type == "PRE_IO")
				net_max_path_delay[net] = -1e3;
			else
				net_max_path_delay[net] = get_delay(driver_type, "*clkedge*", driver_port) + GLOBAL_CLK_DIST_JITTER;
			return net_max_path_delay[net];
		}

		for (auto &inport : get_inports(driver_type))
		{
			if (inport == "clk" || inport == "INPUTCLK" || inport == "OUTPUTCLK" || inport == "PADIN")
				continue;

			if (driver_type == "LogicCell40" && driver_port == "carryout") {
				if (inport == "in0" || inport == "in3" || inport == "ce" || inport == "sr")
					continue;
			}

			if (driver_type == "LogicCell40" && (driver_port == "ltout" || driver_port == "lcout")) {
				if (inport == "carryin")
					continue;
			}

			if (driver_type == "LogicCell40" && driver_port == "ltout") {
				if (inport == "ce" || inport == "sr")
					continue;
			}

			std::string *in_net = &netlist_cell_ports.at(driver_cell).at(inport);
			while (net_assignments.count(*in_net))
				in_net = &net_assignments.at(*in_net);

			if (*in_net == "" || *in_net == "vcc" || *in_net == "gnd")
				continue;

			double this_cell_delay = get_delay(driver_type, inport, driver_port);
			double this_path_delay = calc_net_max_path_delay(*in_net) + this_cell_delay;

			if (this_path_delay >= max_path_delay) {
				net_max_path_parent[net] = std::make_tuple(*in_net, driver_cell, inport, driver_port, this_cell_delay);
				max_path_delay = this_path_delay;
			}
		}

		net_max_path_delay[net] = max_path_delay;
		return net_max_path_delay.at(net);
	}

	void mark_interior(std::string net)
	{
		if (net.empty())
			return;

		while (net_assignments.count(net)) {
			interior_nets.insert(net);
			net = net_assignments.at(net);
		}

		interior_nets.insert(net);
	}

	TimingAnalysis(bool interior_timing) : interior_timing(interior_timing)
	{
		std::set<std::string> all_nets;

		for (auto &it : netlist_cell_ports)
		for (auto &it2 : it.second)
		{
			auto &cell_name = it.first;
			auto &port_name = it2.first;
			auto &net_name = it2.second;

			if (net_name == "")
				continue;

			auto &cell_type = netlist_cell_types.at(cell_name);

			if (get_inports(cell_type).count(port_name)) {
				std::string n = net_name;
				while (1) {
					double setup_time = get_delay(cell_type, port_name, "*setup*");
					if (setup_time >= std::get<0>(net_max_setup[n]))
						net_max_setup[n] = std::make_tuple(setup_time, cell_name, port_name);
					if (net_assignments.count(n) == 0)
						break;
					n = net_assignments.at(n);
				}
				if (interior_timing && cell_type != "PRE_IO" && is_primary(cell_name, "lcout"))
					mark_interior(net_name);
				continue;
			}

			net_driver[net_name] = { cell_name, port_name };
			all_nets.insert(net_name);
		}

		global_max_path_delay = 0;

		for (auto &net : all_nets) {
			if (interior_timing && interior_nets.count(net) == 0)
				continue;
			double d = calc_net_max_path_delay(net) + std::get<0>(net_max_setup[net]);
			if (d > global_max_path_delay) {
				global_max_path_delay = d;
				global_max_path_net = net;
			}
		}
	}

	double report(std::string n = std::string())
	{
		std::vector<std::string> rpt_lines;
		std::vector<std::string> json_lines;
		std::set<std::string> visited_nets;

		if (n.empty()) {
			n = global_max_path_net;
			if (n.empty()) {
				fprintf(stderr, "This design is empty. It contains no paths!\n");
				exit(1);
			}
			if (frpt) {
				int i = fprintf(frpt, "Report for critical path:\n");
				while (--i) fputc('-', frpt);
				fprintf(frpt, "\n\n");
			}
		} else
		if (frpt) {
			int i = fprintf(frpt, "Report for %s:\n", n.c_str());
			while (--i) fputc('-', frpt);
			fprintf(frpt, "\n\n");
		}

		if (net_max_path_delay.count(n) == 0) {
			fprintf(stderr, "Net not found: %s\n", n.c_str());
			exit(1);
		}

		double delay = net_max_path_delay.at(n);

		std::string net_sym;
		std::vector<std::pair<double, std::string>> sym_list;
		std::map<std::string, std::string> outsym_list;

		int logic_levels = 0;
		bool last_line = true;

		auto &user = net_max_setup[n];

		if (!std::get<1>(user).empty())
		{
			delay += std::get<0>(user);
			std::string outnet, outnethw, outnetsym;

			auto &inports = get_inports(netlist_cell_types.at(std::get<1>(user)));

			for (auto &it : netlist_cell_ports.at(std::get<1>(user)))
			{
				if (inports.count(it.first) || it.second.empty())
					continue;

				int netidx;
				char dummy_ch;

				outnetsym = outnethw = outnet = it.second;
				if (sscanf(it.second.c_str(), "net_%d%c", &netidx, &dummy_ch) == 1 && net_symbols.count(netidx)) {
					outnetsym = outsym_list[it.first] = net_symbols[netidx];
					outnet += stringf(" (%s)", outnetsym.c_str());
				}
			}

			rpt_lines.push_back(stringf("%10.3f ns %s", delay, outnet.c_str()));
			rpt_lines.push_back(stringf("        %s (%s) %s [setup]: %.3f ns", std::get<1>(user).c_str(),
					netlist_cell_types.at(std::get<1>(user)).c_str(), std::get<2>(user).c_str(), std::get<0>(user)));

			std::string netprop = outnetsym == outnethw ? "" : stringf("\"net\": \"%s\", ", outnetsym.c_str());
			json_lines.push_back(stringf("    { %s\"hwnet\": \"%s\", \"cell\": \"%s\", \"cell_type\": \"%s\", \"cell_in_port\": \"%s\", \"cell_out_port\": \"[setup]\", \"delay_ns\": %.3f },",
					netprop.c_str(), outnethw.c_str(), std::get<1>(user).c_str(), netlist_cell_types.at(std::get<1>(user)).c_str(), std::get<2>(user).c_str(), delay));
		}

		while (1)
		{
			int netidx;
			char dummy_ch;
			std::string outnetsym = n;

			if (sscanf(n.c_str(), "net_%d%c", &netidx, &dummy_ch) == 1 && net_symbols.count(netidx)) {
				sym_list.push_back(std::make_pair(calc_net_max_path_delay(n), net_symbols[netidx]));
				if (net_sym.empty() || net_sym[0] == '$')
					net_sym = sym_list.back().second;
			}

			if (net_max_path_parent.count(n) == 0)
			{
				rpt_lines.push_back(stringf("%10.3f ns %s", calc_net_max_path_delay(n), n.c_str()));

				if (!net_sym.empty()) {
					rpt_lines.back() += stringf(" (%s)", net_sym.c_str());
					outnetsym = net_sym;
					net_sym.clear();
				}

				if (net_driver.count(n)) {
					auto &driver_cell = net_driver.at(n).first;
					auto &driver_port = net_driver.at(n).second;
					auto &driver_type = netlist_cell_types.at(driver_cell);
					std::string netprop = outnetsym == n ? "" : stringf("\"net\": \"%s\", ", outnetsym.c_str());
					json_lines.push_back(stringf("    { %s\"hwnet\": \"%s\", \"cell\": \"%s\", \"cell_type\": \"%s\", \"cell_in_port\": \"[clk]\", \"cell_out_port\": \"%s\", \"delay_ns\": %.3f },",
							netprop.c_str(), n.c_str(), driver_cell.c_str(), driver_type.c_str(), driver_port.c_str(), calc_net_max_path_delay(n)));
					rpt_lines.push_back(stringf("        %s (%s) [clk] -> %s: %.3f ns", driver_cell.c_str(),
							driver_type.c_str(), driver_port.c_str(), calc_net_max_path_delay(n)));
				} else {
					rpt_lines.push_back(stringf("        no driver model at %s", n.c_str()));
				}
				break;
			}

			if (visited_nets.count(n)) {
				rpt_lines.push_back(stringf("        loop-start at %s", n.c_str()));
				break;
			}

			auto &entry = net_max_path_parent.at(n);

			if (last_line || netlist_cell_types.at(std::get<1>(entry)) == "LogicCell40")
			{
				rpt_lines.push_back(stringf("%10.3f ns %s", calc_net_max_path_delay(n), n.c_str()));
				logic_levels++;

				if (!net_sym.empty()) {
					rpt_lines.back() += stringf(" (%s)", net_sym.c_str());
					outnetsym = net_sym;
					net_sym.clear();
				}
			}

			std::string netprop = outnetsym == n ? "" : stringf("\"net\": \"%s\", ", outnetsym.c_str());
			json_lines.push_back(stringf("    { %s\"hwnet\": \"%s\", \"cell\": \"%s\", \"cell_type\": \"%s\", \"cell_in_port\": \"%s\", \"cell_out_port\": \"%s\", \"delay_ns\": %.3f },",
					netprop.c_str(), n.c_str(), std::get<1>(entry).c_str(), netlist_cell_types.at(std::get<1>(entry)).c_str(),
					std::get<2>(entry).c_str(), std::get<3>(entry).c_str(), calc_net_max_path_delay(n)));

			rpt_lines.push_back(stringf("        %s (%s) %s -> %s: %.3f ns", std::get<1>(entry).c_str(),
					netlist_cell_types.at(std::get<1>(entry)).c_str(), std::get<2>(entry).c_str(),
					std::get<3>(entry).c_str(), std::get<4>(entry)));

			visited_nets.insert(n);
			n = std::get<0>(entry);
			last_line = false;
		}

		if (fjson)
		{
			if (!json_firstentry)
				fprintf(fjson, "  ],\n");
			fprintf(fjson, "  [\n");
			for (int i = int(json_lines.size())-1; i >= 0; i--) {
				std::string line = json_lines[i];
				if (i == 0 && line.back() == ',')
					line.pop_back();
				fprintf(fjson, "%s\n", line.c_str());
			}
			json_firstentry = false;
		}

		if (frpt)
		{
			for (int i = int(rpt_lines.size())-1; i >= 0; i--)
				fprintf(frpt, "%s\n", rpt_lines[i].c_str());

			if (!sym_list.empty() || !outsym_list.empty())
			{
				fprintf(frpt, "\n");
				fprintf(frpt, "Resolvable net names on path:\n");

				std::string last_net;
				double first_time = 0.0, last_time = 0.0;

				for (int i = int(sym_list.size())-1; i >= 0; i--) {
					if (last_net != sym_list[i].second) {
						if (!last_net.empty())
							fprintf(frpt, "%10.3f ns ..%7.3f ns %s\n", first_time, last_time, last_net.c_str());
						first_time = sym_list[i].first;
						last_net = sym_list[i].second;
					}
					last_time = sym_list[i].first;
				}

				if (!last_net.empty())
					fprintf(frpt, "%10.3f ns ..%7.3f ns %s\n", first_time, last_time, last_net.c_str());

				for (auto &it : outsym_list)
					fprintf(frpt, "%23s -> %s\n", it.first.c_str(), it.second.c_str());
			}

			fprintf(frpt, "\n");
			fprintf(frpt, "Total number of logic levels: %d\n", logic_levels);
			fprintf(frpt, "Total path delay: %.2f ns (%.2f MHz)\n", delay, 1000.0 / delay);
			fprintf(frpt, "\n");
		}

		return delay;
	}
};

void register_interconn_src(int x, int y, int net)
{
	std::tuple<int, int, int> key(x, y, net);
	interconn_src.insert(x_y_net_segment.at(key));
}

void register_interconn_dst(int x, int y, int net)
{
	std::tuple<int, int, int> key(x, y, net);
	interconn_dst.insert(x_y_net_segment.at(key));
}

std::string make_seg_pre_io(int x, int y, int z)
{
	auto cell = stringf("pre_io_%d_%d_%d", x, y, z);

	if (netlist_cell_types.count(cell))
		return cell;

	netlist_cell_types[cell] = "PRE_IO";
	netlist_cell_ports[cell]["PADIN"] = stringf("io_pad_%d_%d_%d_dout", x, y, z);
	netlist_cell_ports[cell]["PADOUT"] = stringf("io_pad_%d_%d_%d_din", x, y, z);
	netlist_cell_ports[cell]["PADOEN"] = stringf("io_pad_%d_%d_%d_oe", x, y, z);
	netlist_cell_ports[cell]["LATCHINPUTVALUE"] = "";
	netlist_cell_ports[cell]["CLOCKENABLE"] = "";
	netlist_cell_ports[cell]["INPUTCLK"] = "";
	netlist_cell_ports[cell]["OUTPUTCLK"] = "";
	netlist_cell_ports[cell]["OUTPUTENABLE"] = "";
	netlist_cell_ports[cell]["DOUT1"] = "";
	netlist_cell_ports[cell]["DOUT0"] = "";
	netlist_cell_ports[cell]["DIN1"] = "";
	netlist_cell_ports[cell]["DIN0"] = "";

	std::string pintype;
	std::pair<int, int> bitpos;

	for (int i = 0; i < 6; i++) {
		bitpos = io_tile_bits[stringf("IOB_%d.PINTYPE_%d", z, 5-i)][0];
		pintype.push_back(get_config_bit(x, y, bitpos.first, bitpos.second) ? '1' : '0');
	}

	bitpos = io_tile_bits["NegClk"][0];
	char negclk = get_config_bit(x, y, bitpos.first, bitpos.second) ? '1' : '0';

	netlist_cell_params[cell]["NEG_TRIGGER"] = stringf("1'b%c", negclk);
	netlist_cell_params[cell]["PIN_TYPE"] = stringf("6'b%s", pintype.c_str());

	std::string io_name;
	std::tuple<int, int, int> key(x, y, z);

	if (pin_pos.count(key)) {
		io_name = pin_pos.at(key);
		io_name = pin_names.count(io_name) ? pin_names.at(io_name) : "io_" + io_name;
	} else {
		io_name = stringf("io_%d_%d_%d", x, y, z);
	}

	io_names.insert(io_name);
	extra_vlog.push_back(stringf("  inout %s;\n", io_name.c_str()));
	extra_vlog.push_back(stringf("  wire io_pad_%d_%d_%d_din;\n", x, y, z));
	extra_vlog.push_back(stringf("  wire io_pad_%d_%d_%d_dout;\n", x, y, z));
	extra_vlog.push_back(stringf("  wire io_pad_%d_%d_%d_oe;\n", x, y, z));
	extra_vlog.push_back(stringf("  IO_PAD io_pad_%d_%d_%d (\n", x, y, z));
	extra_vlog.push_back(stringf("    .DIN(io_pad_%d_%d_%d_din),\n", x, y, z));
	extra_vlog.push_back(stringf("    .DOUT(io_pad_%d_%d_%d_dout),\n", x, y, z));
	extra_vlog.push_back(stringf("    .OE(io_pad_%d_%d_%d_oe),\n", x, y, z));
	extra_vlog.push_back(stringf("    .PACKAGEPIN(%s)\n", io_name.c_str()));
	extra_vlog.push_back(stringf("  );\n"));

	return cell;
}

std::string make_lc40(int x, int y, int z)
{
	assert(0 <= x && 0 < y && 0 <= z && z < 8);

	auto cell = stringf("lc40_%d_%d_%d", x, y, z);

	if (netlist_cell_types.count(cell))
		return cell;

	netlist_cell_types[cell] = "LogicCell40";
	netlist_cell_ports[cell]["carryin"] = "gnd";
	netlist_cell_ports[cell]["ce"] = "";
	netlist_cell_ports[cell]["clk"] = "gnd";
	netlist_cell_ports[cell]["in0"] = "gnd";
	netlist_cell_ports[cell]["in1"] = "gnd";
	netlist_cell_ports[cell]["in2"] = "gnd";
	netlist_cell_ports[cell]["in3"] = "gnd";
	netlist_cell_ports[cell]["sr"] = "gnd";
	netlist_cell_ports[cell]["carryout"] = "";
	netlist_cell_ports[cell]["lcout"] = "";
	netlist_cell_ports[cell]["ltout"] = "";

	char lcbits[20];
	auto &lcbits_pos = logic_tile_bits[stringf("LC_%d", z)];

	for (int i = 0; i < 20; i++)
		lcbits[i] = get_config_bit(x, y, lcbits_pos[i].first, lcbits_pos[i].second) ? '1' : '0';

	// FIXME: fill in the '0'
	netlist_cell_params[cell]["C_ON"] = stringf("1'b%c", lcbits[8]);
	netlist_cell_params[cell]["SEQ_MODE"] = stringf("4'b%c%c%c%c", lcbits[9], '0', '0', '0');
	netlist_cell_params[cell]["LUT_INIT"] = stringf("16'b%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c",
			lcbits[0], lcbits[10], lcbits[11], lcbits[1],
			lcbits[2], lcbits[12], lcbits[13], lcbits[3],
			lcbits[7], lcbits[17], lcbits[16], lcbits[6],
			lcbits[5], lcbits[15], lcbits[14], lcbits[4]);

	if (lcbits[8] == '1')
	{
		if (z == 0)
		{
			auto co_cell = 1 < y ? make_lc40(x, y-1, 7) : std::string();
			std::string n1, n2;

			char cinit_1 = get_config_bit(x, y, 1, 49) ? '1' : '0';
			char cinit_0 = get_config_bit(x, y, 1, 50) ? '1' : '0';

			if (cinit_1 == '1') {
				std::tuple<int, int, std::string> key(x, y-1, "lutff_7/cout");
				if (x_y_name_net.count(key)) {
					n1 = net_name(x_y_name_net.at(key));
				} else {
					n1 = tname();
					assert(!co_cell.empty());
					netlist_cell_ports[co_cell]["carryout"] = n1;
					extra_wires.insert(n1);
				}
			}

			std::tuple<int, int, std::string> key(x, y, "carry_in_mux");
			if (x_y_name_net.count(key)) {
				n2 = net_name(x_y_name_net.at(key));
			} else {
				n2 = tname();
				extra_wires.insert(n2);
			}

			std::string tn = tname();
			netlist_cell_types[tn] = "ICE_CARRY_IN_MUX";
			netlist_cell_params[tn]["C_INIT"] = stringf("2'b%c%c", cinit_1, cinit_0);
			netlist_cell_ports[tn]["carryinitin"] = n1;
			netlist_cell_ports[tn]["carryinitout"] = n2;

			netlist_cell_ports[cell]["carryin"] = n2;
		}
		else
		{
			auto co_cell = make_lc40(x, y, z-1);
			std::tuple<int, int, std::string> key(x, y, stringf("lutff_%d/cout", z-1));
			auto n = x_y_name_net.count(key) ? net_name(x_y_name_net.at(key)) : tname();

			netlist_cell_ports[co_cell]["carryout"] = n;
			netlist_cell_ports[cell]["carryin"] = n;
			extra_wires.insert(n);
		}

		std::tuple<int, int, std::string> key(x, y, stringf("lutff_%d/cout", z-1));
	}

	return cell;
}

bool get_dsp_ip_cbit(std::tuple<int, int, std::string> cbit) {
	std::string name = "IpConfig." + std::get<2>(cbit);
	// DSP0 contains all CBITs, the same as any DSP/IP tile
	if(dsp0_tile_bits.count(name)) {
		auto bitpos = dsp0_tile_bits.at(name)[0];
		return get_config_bit(std::get<0>(cbit), std::get<1>(cbit), bitpos.first, bitpos.second);
	}
	return false;
}

std::string ecnetname_to_vlog(std::string ec_name)
{
	// Convert a net name from the form A_0 used in the chipdb for extra cells to
  // verilog form A[0]
	size_t last_ = ec_name.find_last_of('_');
	if(last_ == std::string::npos)
		return ec_name;

	std::string base = ec_name.substr(0, last_);
	std::string end = ec_name.substr(last_+1);
	size_t nidx = 0;

	int num = 0;
	try {
		num = std::stoi(end, &nidx, 10);
		if(nidx == end.length()) {
			return base + "[" + std::to_string(num) + "]";
		} else {
			return ec_name;
		}
	} catch(std::invalid_argument &e) { // Not numeric and stoi throws exception
		return ec_name;
	}

}

std::string make_dsp_ip(int x, int y, std::string net, std::string &primnet)
{
	// Don't generate excessive warnings about unknown cells
	static std::set<std::string> unsupported_cells;
	std::tuple<int, int, std::string> ecnet(x, y, net);
	std::tuple<std::string, int, int, int> key("", -1, -1, -1);
	bool found = false;
	for(auto ec : extra_cells) {
		for(auto entry : ec.second) {
			if(entry.second == ecnet) {
				key = ec.first;
				primnet = ecnetname_to_vlog(entry.first);
				found = true;
				break;
			}
		}
	}
	if(!found) {
		fprintf(stderr, "Error: net (%d, %d, '%s') does not correspond to any IP\n", x, y, net.c_str());
		exit(1);
	}
	int cx, cy, cz;
	std::string ectype;
	std::tie(ectype, cx, cy, cz) = key;

	auto cell = stringf("%s_%d_%d_%d", ectype.c_str(), cx, cy, cz);

	if (netlist_cell_types.count(cell))
		return cell;

	if(ectype == "MAC16") {
		// Given the few actual unique timing possibilites, only look at a subset
		// of the CBITs to pick the closest cell type from a timing point of view
		std::string dsptype = "";
		bool mode_8x8 = get_dsp_ip_cbit(extra_cells[key].at("MODE_8x8"));
		// It seems no different between any pipeline mode, so pick pipelining based
		// on one of the bits
		bool pipeline = get_dsp_ip_cbit(extra_cells[key].at("A_REG"));
		int botout = (get_dsp_ip_cbit(extra_cells[key].at("BOTOUTPUT_SELECT_1")) << 1) | get_dsp_ip_cbit(extra_cells[key].at("BOTOUTPUT_SELECT_0"));
		int botlwrin = (get_dsp_ip_cbit(extra_cells[key].at("BOTADDSUB_LOWERINPUT_1")) << 1) | get_dsp_ip_cbit(extra_cells[key].at("BOTADDSUB_LOWERINPUT_0"));
		bool botuprin = get_dsp_ip_cbit(extra_cells[key].at("BOTADDSUB_UPPERINPUT"));
		int topcarry = (get_dsp_ip_cbit(extra_cells[key].at("TOPADDSUB_CARRYSELECT_1")) << 1) | get_dsp_ip_cbit(extra_cells[key].at("TOPADDSUB_CARRYSELECT_0"));
		// Worst case default
		std::string basename = "SB_MAC16_MUL_U_16X16";
		// Note: signedness is ignored as it seems to have no effect
		if(mode_8x8 && !botuprin && (botlwrin == 0) && (botout == 2)) {
			basename = "SB_MAC16_MUL_U_8X8";
		} else if (!mode_8x8 && !botuprin && (botlwrin == 0) && (botout == 3)) {
			basename = "SB_MAC16_MUL_U_16X16";
		} else if (mode_8x8 && !botuprin && (botlwrin == 1) && (botout == 1)) {
			basename = "SB_MAC16_MAC_U_8X8";
		} else if (!mode_8x8 && !botuprin && (botlwrin == 2) && (botout == 1)) {
			basename = "SB_MAC16_MAC_U_16X16";
		} else if (mode_8x8 && !botuprin && (botlwrin == 0) && (botout == 1) && (topcarry == 0)) {
			basename = "SB_MAC16_ACC_U_16P16";
		} else if (mode_8x8 && !botuprin && (botlwrin == 0) && (botout == 1) && (topcarry == 2)) {
			basename = "SB_MAC16_ACC_U_32P32";
		} else if (mode_8x8 && botuprin && (botlwrin == 0) && (topcarry == 0)) {
			basename = "SB_MAC16_ADS_U_16P16";
		} else if (mode_8x8 && botuprin && (botlwrin == 0) && (topcarry == 2)) {
			basename = "SB_MAC16_ADS_U_32P32";
		} else if (mode_8x8 && botuprin && (botlwrin == 1)) {
			basename = "SB_MAC16_MAS_U_8X8";
		} else if (!mode_8x8 && botuprin && (botlwrin == 2)) {
			basename = "SB_MAC16_MAS_U_16X16";
		} else {
			fprintf(stderr, "Warning: detected unknown/unsupported DSP config, defaulting to 16x16 MUL.\n");
		}
		dsptype = basename + (pipeline ? "_ALL_PIPELINE" : "_BYPASS");
		netlist_cell_types[cell] = dsptype;

		for (int i = 0; i < 16; i++) {
			netlist_cell_ports[cell][stringf("C[%d]", i)] = "gnd";
			netlist_cell_ports[cell][stringf("A[%d]", i)] = "gnd";
			netlist_cell_ports[cell][stringf("B[%d]", i)] = "gnd";
			netlist_cell_ports[cell][stringf("D[%d]", i)] = "gnd";
		}

		netlist_cell_ports[cell]["CLK"] = "";
		netlist_cell_ports[cell]["CE"] = "";
		netlist_cell_ports[cell]["AHOLD"] = "gnd";
		netlist_cell_ports[cell]["BHOLD"] = "gnd";
		netlist_cell_ports[cell]["CHOLD"] = "gnd";
		netlist_cell_ports[cell]["DHOLD"] = "gnd";

		netlist_cell_ports[cell]["IRSTTOP"] = "";
		netlist_cell_ports[cell]["IRSTBOT"] = "";
		netlist_cell_ports[cell]["ORSTTOP"] = "";
		netlist_cell_ports[cell]["ORSTBOT"] = "";

		netlist_cell_ports[cell]["OLOADTOP"] = "gnd";
		netlist_cell_ports[cell]["OLOADBOT"] = "gnd";
		netlist_cell_ports[cell]["ADDSUBTOP"] = "gnd";
		netlist_cell_ports[cell]["ADDSUBBOT"] = "gnd";
		netlist_cell_ports[cell]["OHOLDTOP"] = "gnd";
		netlist_cell_ports[cell]["OHOLDBOT"] = "gnd";
		netlist_cell_ports[cell]["CI"] = "gnd";
		netlist_cell_ports[cell]["ACCUMCI"] = "";
		netlist_cell_ports[cell]["SIGNEXTIN"] = "";

		for (int i = 0; i < 32; i++) {
			netlist_cell_ports[cell][stringf("O[%d]", i)] = "";
		}

		netlist_cell_ports[cell]["ACCUMCO"] = "";
		netlist_cell_ports[cell]["SIGNEXTOUT"] = "";

		return cell;
	} else if(ectype == "SPRAM") {
		netlist_cell_types[cell] = "SB_SPRAM256KA";

		for (int i = 0; i < 14; i++) {
			netlist_cell_ports[cell][stringf("ADDRESS[%d]", i)] = "gnd";
		}

		for (int i = 0; i < 16; i++) {
			netlist_cell_ports[cell][stringf("DATAIN[%d]", i)] = "gnd";
			netlist_cell_ports[cell][stringf("DATAOUT[%d]", i)] = "";
		}

		netlist_cell_ports[cell]["MASKWREN[3]"] = "gnd";
		netlist_cell_ports[cell]["MASKWREN[2]"] = "gnd";
		netlist_cell_ports[cell]["MASKWREN[1]"] = "gnd";
		netlist_cell_ports[cell]["MASKWREN[0]"] = "gnd";

		netlist_cell_ports[cell]["WREN"] = "gnd";
		netlist_cell_ports[cell]["CHIPSELECT"] = "gnd";
		netlist_cell_ports[cell]["CLOCK"] = "";
		netlist_cell_ports[cell]["STANDBY"] = "gnd";
		netlist_cell_ports[cell]["SLEEP"] = "gnd";
		netlist_cell_ports[cell]["POWEROFF"] = "gnd";

		return cell;
	} else {
		if (unsupported_cells.find(ectype) == unsupported_cells.end()) {
			fprintf(stderr, "Warning: timing analysis not supported for cell type %s\n", ectype.c_str());
			unsupported_cells.insert(ectype);
		}
		return "";
	}
}

std::string make_ram(int x, int y)
{
	auto cell = stringf("ram_%d_%d", x, y);

	if (netlist_cell_types.count(cell))
		return cell;

	netlist_cell_types[cell] = "SB_RAM40_4K";

	for (int i = 0; i < 16; i++) {
		netlist_cell_ports[cell][stringf("MASK[%d]", i)] = "";
		netlist_cell_ports[cell][stringf("RDATA[%d]", i)] = "";
		netlist_cell_ports[cell][stringf("WDATA[%d]", i)] = "";
	}

	for (int i = 0; i < 11; i++) {
		netlist_cell_ports[cell][stringf("RADDR[%d]", i)] = "";
		netlist_cell_ports[cell][stringf("WADDR[%d]", i)] = "";
	}

	netlist_cell_ports[cell]["RE"] = "";
	netlist_cell_ports[cell]["RCLK"] = "";
	netlist_cell_ports[cell]["RCLKE"] = "";

	netlist_cell_ports[cell]["WE"] = "";
	netlist_cell_ports[cell]["WCLK"] = "";
	netlist_cell_ports[cell]["WCLKE"] = "";

	return cell;
}

bool dff_uses_clock(int x, int y, int z)
{
	auto bitpos = logic_tile_bits[stringf("LC_%d", z)][9];
	return get_config_bit(x, y, bitpos.first, bitpos.second);
}

void make_odrv(int x, int y, int src)
{
	for (int dst : net_buffers[src])
	{
		auto cell = stringf("odrv_%d_%d_%d_%d", x, y, src, dst);

		if (netlist_cell_types.count(cell))
			continue;

		bool is4 = false, is12 = false;

		for (auto &seg : net_to_segments[dst]) {
			if (seg.name.substr(0, 4) == "sp4_") is4 = true;
			if (seg.name.substr(0, 5) == "sp12_") is12 = true;
			if (seg.name.substr(0, 6) == "span4_") is4 = true;
			if (seg.name.substr(0, 7) == "span12_") is12 = true;
		}

		if (!is4 && !is12) {
			register_interconn_src(x, y, src);
			continue;
		}

		assert(is4 != is12);
		netlist_cell_types[cell] = is4 ? "Odrv4" : "Odrv12";
		netlist_cell_ports[cell]["I"] = net_name(src);
		netlist_cell_ports[cell]["O"] = net_name(dst);
		register_interconn_src(x, y, dst);
	}
}

void make_inmux(int x, int y, int dst, std::string muxtype = "")
{
	for (int src : net_rbuffers[dst])
	{
		std::tuple<int, int, int> key(x, y, src);
		std::string src_name = x_y_net_segment.at(key).name;
		int cascade_n = 0;

		if (src_name.size() > 6) {
			cascade_n = src_name[6] - '0';
			src_name[6] = 'X';
		}

		if (src_name == "lutff_X/lout") {
			auto cell = make_lc40(x, y, cascade_n);
			netlist_cell_ports[cell]["ltout"] = net_name(dst);
			continue;
		}

		auto cell = stringf("inmux_%d_%d_%d_%d", x, y, src, dst);

		if (netlist_cell_types.count(cell))
			continue;

		netlist_cell_types[cell] = muxtype.empty() ? (config_tile_type[x][y] == "io" ? "IoInMux" : "InMux") : muxtype;
		netlist_cell_ports[cell]["I"] = net_name(src);
		netlist_cell_ports[cell]["O"] = net_name(dst);

		register_interconn_dst(x, y, src);
		no_interconn_net.insert(dst);
	}
}

std::string cascademuxed(std::string n)
{
	std::string nc = n + "_cascademuxed";
	extra_wires.insert(nc);

	std::string tn = tname();
	netlist_cell_types[tn] = "CascadeMux";
	netlist_cell_ports[tn]["I"] = n;
	netlist_cell_ports[tn]["O"] = nc;

	return nc;
}

void make_seg_cell(int net, const net_segment_t &seg)
{
	int a = -1, b = -1;
	char c = 0;

	if (sscanf(seg.name.c_str(), "io_%d/D_IN_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.x, seg.y, a);
		netlist_cell_ports[cell][stringf("DIN%d", b)] = net_name(net);
		make_odrv(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "io_%d/D_OUT_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.x, seg.y, a);
		netlist_cell_ports[cell][stringf("DOUT%d", b)] = net_name(net);
		make_inmux(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "lutff_%d/in_%d", &a, &b) == 2) {
		//"logic" wires at the side of the device are actually IP or DSP
		if(device_type == "up5k" && ((seg.x == 0) || (seg.x == int(config_tile_type.size()) - 1))) {
			std::string primnet;
			auto cell = make_dsp_ip(seg.x, seg.y, seg.name, primnet);
			if(cell != "") {
				netlist_cell_ports[cell][primnet] = net_name(net);
				make_inmux(seg.x, seg.y, net);
			}
			return;
		} else {
			auto cell = make_lc40(seg.x, seg.y, a);
			if (b == 2) {
				// Lattice tools always put a CascadeMux on in2
				netlist_cell_ports[cell][stringf("in%d", b)] = cascademuxed(net_name(net));
			} else {
				netlist_cell_ports[cell][stringf("in%d", b)] = net_name(net);
			}
			make_inmux(seg.x, seg.y, net);
		}

		return;
	}

	if (sscanf(seg.name.c_str(), "lutff_%d/ou%c", &a, &c) == 2 && c == 't')
	{
		for (int dst_net : net_buffers.at(seg.net))
		for (auto &dst_seg : net_to_segments.at(dst_net)) {
			std::string n = dst_seg.name;
			if (n.size() > 6) n[6] = 'X';
			if (n != "lutff_X/in_2")
				goto use_lcout;
		}
		return;

	use_lcout:
		auto cell = make_lc40(seg.x, seg.y, a);
		netlist_cell_ports[cell]["lcout"] = net_name(net);
		make_odrv(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "slf_op_%d", &a) == 1)
	{
		std::string primnet;
		auto cell = make_dsp_ip(seg.x, seg.y, seg.name, primnet);
		if(cell != "") {
			netlist_cell_ports[cell][primnet] = net_name(net);
			make_odrv(seg.x, seg.y, net);
		}
		return;
	}

	if (sscanf(seg.name.c_str(), "mult/O_%d", &a) == 1)
	{
		std::string primnet;
		auto cell = make_dsp_ip(seg.x, seg.y, seg.name, primnet);
		if(cell != "") {
			netlist_cell_ports[cell][primnet] = net_name(net);
			make_odrv(seg.x, seg.y, net);
		}
		return;
	}

	if (sscanf(seg.name.c_str(), "lutff_%d/cou%c", &a, &c) == 2 && c == 't')
	{
		auto cell = make_lc40(seg.x, seg.y, a);
		netlist_cell_ports[cell]["carryout"] = net_name(net);
		return;
	}

	if (seg.name.substr(0, 4) == "ram/")
	{
		auto cell = make_ram(seg.x, 2*((seg.y-1) >> 1) + 1);

		if (sscanf(seg.name.c_str(), "ram/MASK_%d", &a) == 1) {
			netlist_cell_ports[cell][stringf("MASK[%d]", a)] = net_name(net);
			make_inmux(seg.x, seg.y, net);
		} else
		if (sscanf(seg.name.c_str(), "ram/RADDR_%d", &a) == 1) {
			netlist_cell_ports[cell][stringf("RADDR[%d]", a)] = cascademuxed(net_name(net));
			make_inmux(seg.x, seg.y, net);
		} else
		if (sscanf(seg.name.c_str(), "ram/RDATA_%d", &a) == 1) {
			netlist_cell_ports[cell][stringf("RDATA[%d]", a)] = net_name(net);
			make_odrv(seg.x, seg.y, net);
		} else
		if (sscanf(seg.name.c_str(), "ram/WADDR_%d", &a) == 1) {
			netlist_cell_ports[cell][stringf("WADDR[%d]", a)] = cascademuxed(net_name(net));
			make_inmux(seg.x, seg.y, net);
		} else
		if (sscanf(seg.name.c_str(), "ram/WDATA_%d", &a) == 1) {
			netlist_cell_ports[cell][stringf("WDATA[%d]", a)] = net_name(net);
			make_inmux(seg.x, seg.y, net);
		} else {
			netlist_cell_ports[cell][seg.name.substr(4)] = net_name(net);
			if (seg.name == "ram/RCLK" || seg.name == "ram/WCLK")
				make_inmux(seg.x, seg.y, net, "ClkMux");
			else if (seg.name == "ram/RCLKE" || seg.name == "ram/WCLKE")
				make_inmux(seg.x, seg.y, net, "CEMux");
			else
				make_inmux(seg.x, seg.y, net, "SRMux");
		}

		return;
	}

	if (seg.name == "lutff_global/clk" || seg.name == "lutff_global/cen" || seg.name == "lutff_global/s_r")
	{
		for (int i = 0; i < 8; i++)
		{
			if (!dff_uses_clock(seg.x, seg.y, i))
				continue;

			std::tuple<int, int, std::string> key(seg.x, seg.y, stringf("lutff_%d/out", i));
			if (x_y_name_net.count(key))
			{
				auto cell = make_lc40(seg.x, seg.y, i);

				if (seg.name == "lutff_global/clk") {
					make_inmux(seg.x, seg.y, net, "ClkMux");
					netlist_cell_ports[cell]["clk"] = net_name(seg.net);
				}
				if (seg.name == "lutff_global/cen") {
					make_inmux(seg.x, seg.y, net, "CEMux");
					netlist_cell_ports[cell]["ce"] = net_name(seg.net);
				}
				if (seg.name == "lutff_global/s_r") {
					make_inmux(seg.x, seg.y, net, "SRMux");
					netlist_cell_ports[cell]["sr"] = net_name(seg.net);
				}
			}
		}
		return;
	}

	if (seg.name == "io_global/inclk" || seg.name == "io_global/outclk" || seg.name == "io_global/cen")
	{
		for (int z = 0; z < 2; z++)
		{
			std::string pintype;
			std::pair<int, int> bitpos;

			for (int i = 0; i < 6; i++) {
				bitpos = io_tile_bits[stringf("IOB_%d.PINTYPE_%d", z, 5-i)][0];
				pintype.push_back(get_config_bit(seg.x, seg.y, bitpos.first, bitpos.second) ? '1' : '0');
			}

			bool use_inclk = false;
			bool use_outclk = false;

			if (pintype[5-0] == '0')
				use_inclk = true;

			if (pintype[5-5] == '1' && pintype[5-4] == '1')
				use_outclk = true;

			if (pintype[5-5] == '1' || pintype[5-4] == '1') {
				if (pintype[5-2] == '1' || pintype[5-3] == '0')
					use_outclk = true;
			}

			std::tuple<int, int, std::string> din0_key(seg.x, seg.y, stringf("io_%d/D_IN_%d", z, 0));
			std::tuple<int, int, std::string> din1_key(seg.x, seg.y, stringf("io_%d/D_IN_%d", z, 1));

			if (x_y_name_net.count(din0_key) == 0 && x_y_name_net.count(din1_key) == 0)
				use_inclk = false;

			std::tuple<int, int, std::string> dout0_key(seg.x, seg.y, stringf("io_%d/D_OUT_%d", z, 0));
			std::tuple<int, int, std::string> dout1_key(seg.x, seg.y, stringf("io_%d/D_OUT_%d", z, 1));

			if (x_y_name_net.count(dout0_key) == 0 && x_y_name_net.count(dout1_key) == 0)
				use_outclk = false;

			if (!use_inclk && !use_outclk)
				continue;

			auto cell = make_seg_pre_io(seg.x, seg.y, z);

			if (seg.name == "io_global/inclk" && use_inclk) {
				netlist_cell_ports[cell]["INPUTCLK"] = net_name(seg.net);
				make_inmux(seg.x, seg.y, seg.net, "ClkMux");
			}

			if (seg.name == "io_global/outclk" && use_outclk) {
				netlist_cell_ports[cell]["OUTPUTCLK"] = net_name(seg.net);
				make_inmux(seg.x, seg.y, seg.net, "ClkMux");
			}

			if (seg.name == "io_global/cen") {
				netlist_cell_ports[cell]["CLOCKENABLE"] = net_name(seg.net);
				make_inmux(seg.x, seg.y, seg.net, "CEMux");
			} else {
				if (netlist_cell_ports[cell]["CLOCKENABLE"] == "")
					netlist_cell_ports[cell]["CLOCKENABLE"] = "vcc";
			}
		}
	}
}

struct make_interconn_worker_t
{
	std::map<int, std::set<int>> net_tree;
	std::map<net_segment_t, std::set<net_segment_t>> seg_tree;
	std::map<net_segment_t, net_segment_t> seg_parents;
	std::map<net_segment_t, int> porch_segs;
	std::set<net_segment_t> target_segs, handled_segs;
	std::set<int> handled_global_nets;

	std::map<net_segment_t, std::pair<net_segment_t, std::string>> cell_log;

	void build_net_tree(int src)
	{
		auto &children = net_tree[src];

		for (auto &other : net_buffers[src])
			if (!net_tree.count(other) && !no_interconn_net.count(other)) {
				build_net_tree(other);
				children.insert(other);
			}

		for (auto &other : net_routing[src])
			if (!net_tree.count(other) && !no_interconn_net.count(other)) {
				build_net_tree(other);
				children.insert(other);
			}
	}

	void build_seg_tree(const net_segment_t &src)
	{
		std::set<net_segment_t> queue, targets;
		std::map<net_segment_t, int> distances;
		std::map<net_segment_t, net_segment_t> reverse_edges;
		queue.insert(src);

		std::map<net_segment_t, std::set<net_segment_t>> seg_connections;
		porch_segs[src] = 1;

		for (auto &it: net_tree)
		for (int child : it.second)
		{
			auto pos = connection_pos.at(std::pair<int, int>(it.first, child));
			std::tuple<int, int, int> key_parent(pos.first, pos.second, it.first);
			std::tuple<int, int, int> key_child(pos.first, pos.second, child);
			seg_connections[x_y_net_segment.at(key_parent)].insert(x_y_net_segment.at(key_child));


			const std::string &parent_name = x_y_net_segment.at(key_parent).name;
			const std::string &child_name = x_y_net_segment.at(key_child).name;
			if (parent_name.substr(0, 7) == "span12_" || parent_name.substr(0, 5) == "sp12_")
				if (child_name.substr(0, 6) == "span4_" || child_name.substr(0, 4) == "sp4_")
					porch_segs[x_y_net_segment.at(key_child)] = 1;
		}

		for (int distance_counter = 0; !queue.empty(); distance_counter++)
		{
			std::set<net_segment_t> next_queue;

			for (auto &seg : queue)
				distances[seg] = distance_counter;

			for (auto &seg : queue)
			{
				if (seg != src)
					assert(interconn_src.count(seg) == 0);

				if (interconn_dst.count(seg))
					targets.insert(seg);

				if (seg_connections.count(seg))
					for (auto &child : seg_connections.at(seg))
					{
						if (distances.count(child) != 0 || interconn_src.count(child) != 0)
							continue;

						reverse_edges[child] = seg;
						next_queue.insert(child);
					}

				for (int x = seg.x-1; x <= seg.x+1; x++)
				for (int y = seg.y-1; y <= seg.y+1; y++)
				{
					std::tuple<int, int, int> key(x, y, seg.net);

					if (x_y_net_segment.count(key) == 0)
						continue;

					auto &child = x_y_net_segment.at(key);

					if (distances.count(child) != 0)
						continue;

					if (porch_segs.count(seg))
						porch_segs[child] = porch_segs[seg]+1;

					reverse_edges[child] = seg;
					next_queue.insert(child);
				}
			}

			queue.swap(next_queue);
		}

		for (auto &trg : targets) {
			target_segs.insert(trg);
			seg_tree[trg];
		}

		while (!targets.empty()) {
			std::set<net_segment_t> next_targets;
			for (auto &trg : targets)
				if (reverse_edges.count(trg)) {
					seg_tree[reverse_edges.at(trg)].insert(trg);
					next_targets.insert(reverse_edges.at(trg));
				}
			targets.swap(next_targets);
		}

		for (auto &it : seg_tree)
		for (auto &child : it.second) {
			assert(seg_parents.count(child) == 0);
			seg_parents[child] = it.first;
		}
	}

	void create_cells(const net_segment_t &trg)
	{
		if (handled_segs.count(trg) || handled_global_nets.count(trg.net))
			return;

		handled_segs.insert(trg);

		if (seg_parents.count(trg) == 0) {
			net_assignments[seg_name(trg)] = net_name(trg.net);
			return;
		}

		const net_segment_t *cursor = &seg_parents.at(trg);
		std::string tn;

		// Local Mux

		if (trg.name.substr(0, 6) == "local_")
		{
			tn = tname();
			netlist_cell_types[tn] = "LocalMux";
			netlist_cell_ports[tn]["I"] = seg_name(*cursor);
			netlist_cell_ports[tn]["O"] = seg_name(trg);

			cell_log[trg] = std::make_pair(*cursor, "LocalMux");
			goto continue_at_cursor;
		}

		// Span4Mux

		if (trg.name.substr(0, 6) == "span4_" || trg.name.substr(0, 4) == "sp4_")
		{
			bool horiz = trg.name.substr(0, 6) == "sp4_h_";
			int count_length = 0;

			while (seg_parents.count(*cursor) && cursor->net == trg.net) {
				horiz = horiz || (cursor->name.substr(0, 6) == "sp4_h_");
				cursor = &seg_parents.at(*cursor);
				count_length++;
			}

			if (cursor->net == trg.net)
				goto skip_to_cursor;

			count_length = std::min(std::max(count_length, 0), 4);

			if (max_span_hack)
				count_length = 4;

			if (cursor->name.substr(0, 7) == "span12_" || cursor->name.substr(0, 5) == "sp12_") {
				tn = tname();
				netlist_cell_types[tn] = "Sp12to4";
				netlist_cell_ports[tn]["I"] = seg_name(*cursor);
				netlist_cell_ports[tn]["O"] = seg_name(trg);
				cell_log[trg] = std::make_pair(*cursor, "Sp12to4");
			} else
			if (cursor->name.substr(0, 6) == "span4_") {
				tn = tname();
				netlist_cell_types[tn] = "IoSpan4Mux";
				netlist_cell_ports[tn]["I"] = seg_name(*cursor);
				netlist_cell_ports[tn]["O"] = seg_name(trg);
				cell_log[trg] = std::make_pair(*cursor, "IoSpan4Mux");
			} else {
				tn = tname();
				netlist_cell_types[tn] = stringf("Span4Mux_%c%d", horiz ? 'h' : 'v', count_length);
				netlist_cell_ports[tn]["I"] = seg_name(*cursor);
				netlist_cell_ports[tn]["O"] = seg_name(trg);
				cell_log[trg] = std::make_pair(*cursor, stringf("Span4Mux_%c%d", horiz ? 'h' : 'v', count_length));
			}

			goto continue_at_cursor;
		}

		// Span12Mux

		if (trg.name.substr(0, 7) == "span12_" || trg.name.substr(0, 5) == "sp12_")
		{
			bool horiz = trg.name.substr(0, 7) == "sp12_h_";
			int count_length = 0;

			while (seg_parents.count(*cursor) && cursor->net == trg.net) {
				horiz = horiz || (cursor->name.substr(0, 7) == "sp12_h_");
				cursor = &seg_parents.at(*cursor);
				count_length++;
			}

			if (cursor->net == trg.net)
				goto skip_to_cursor;

			count_length = std::min(std::max(count_length, 0), 12);

			if (max_span_hack)
				count_length = 12;

			tn = tname();
			netlist_cell_types[tn] = stringf("Span12Mux_%c%d", horiz ? 'h' : 'v', count_length);
			netlist_cell_ports[tn]["I"] = seg_name(*cursor);
			netlist_cell_ports[tn]["O"] = seg_name(trg);
			cell_log[trg] = std::make_pair(*cursor, stringf("Span12Mux_%c%d", horiz ? 'h' : 'v', count_length));

			goto continue_at_cursor;
		}

		// Global nets

		if (trg.name.substr(0, 10) == "glb_netwk_")
		{
			while (seg_parents.count(*cursor) && (cursor->net == trg.net || cursor->name == "fabout"))
				cursor = &seg_parents.at(*cursor);

			if (cursor->net == trg.net)
				goto skip_to_cursor;

			tn = tname();
			netlist_cell_types[tn] = "GlobalMux";
			netlist_cell_ports[tn]["I"] = seg_name(*cursor, 3);
			netlist_cell_ports[tn]["O"] = seg_name(trg);

			tn = tname();
			netlist_cell_types[tn] = "gio2CtrlBuf";
			netlist_cell_ports[tn]["I"] = seg_name(*cursor, 2);
			netlist_cell_ports[tn]["O"] = seg_name(*cursor, 3);

			tn = tname();
			netlist_cell_types[tn] = "ICE_GB";
			netlist_cell_ports[tn]["USERSIGNALTOGLOBALBUFFER"] = seg_name(*cursor, 1);
			netlist_cell_ports[tn]["GLOBALBUFFEROUTPUT"] = seg_name(*cursor, 2);

			tn = tname();
			netlist_cell_types[tn] = "IoInMux";
			netlist_cell_ports[tn]["I"] = seg_name(*cursor);
			netlist_cell_ports[tn]["O"] = seg_name(*cursor, 1);

			cell_log[trg] = std::make_pair(*cursor, "GlobalMux -> ICE_GB -> IoInMux");

			handled_global_nets.insert(trg.net);
			goto continue_at_cursor;
		}

		// Default handler

		while (seg_parents.count(*cursor) && cursor->net == trg.net)
			cursor = &seg_parents.at(*cursor);

		if (cursor->net == trg.net)
			goto skip_to_cursor;

		tn = tname();
		netlist_cell_types[tn] = "INTERCONN";
		netlist_cell_ports[tn]["I"] = seg_name(*cursor);
		netlist_cell_ports[tn]["O"] = seg_name(trg);

		cell_log[trg] = std::make_pair(*cursor, "INTERCONN");
		goto continue_at_cursor;

	skip_to_cursor:
		net_assignments[seg_name(trg)] = seg_name(*cursor);
	continue_at_cursor:
		create_cells(*cursor);
	}

	static std::string graph_seg_name(const net_segment_t &seg)
	{
		std::string str = stringf("seg_%d_%d_%s", seg.x, seg.y, seg.name.c_str());
		for (auto &ch : str)
			if (ch == '/') ch = '_';
		return str;
	}

	static std::string graph_cell_name(const net_segment_t &seg)
	{
		std::string str = stringf("cell_%d_%d_%s", seg.x, seg.y, seg.name.c_str());
		for (auto &ch : str)
			if (ch == '/') ch = '_';
		return str;
	}

	void show_seg_tree_worker(FILE *f, const net_segment_t &src, std::vector<std::string> &global_lines)
	{
		std::string porch_str = porch_segs.count(src) ? stringf("\\n[P%d]", porch_segs.at(src)) : "";

		fprintf(f, "    %s [ shape=octagon, label=\"%d %d\\n%s%s\" ];\n",
				graph_seg_name(src).c_str(), src.x, src.y, src.name.c_str(), porch_str.c_str());

		std::vector<net_segment_t> other_net_children;

		for (auto &child : seg_tree.at(src)) {
			if (child.net != src.net) {
				other_net_children.push_back(child);
			} else
				show_seg_tree_worker(f, child, global_lines);
			global_lines.push_back(stringf("  %s -> %s;\n",
					graph_seg_name(src).c_str(), graph_seg_name(child).c_str()));
		}

		if (!other_net_children.empty()) {
			for (auto &child : other_net_children) {
				fprintf(f, "  }\n");
				fprintf(f, "  subgraph cluster_net_%d {\n", child.net);
				fprintf(f, "    label = \"net %d\";\n", child.net);
				show_seg_tree_worker(f, child, global_lines);
			}
		}

		if (cell_log.count(src)) {
			auto &cell = cell_log.at(src);
			global_lines.push_back(stringf("  %s [ label=\"%s\" ];\n",
					graph_cell_name(src).c_str(), cell.second.c_str()));
			global_lines.push_back(stringf("  %s -> %s;\n",
					graph_seg_name(cell.first).c_str(), graph_cell_name(src).c_str()));
			global_lines.push_back(stringf("  %s -> %s;\n",
					graph_cell_name(src).c_str(), graph_seg_name(src).c_str()));
		}
	}

	void show_seg_tree(const net_segment_t &src, FILE *f)
	{
		fprintf(f, "  subgraph cluster_net_%d {\n", src.net);
		fprintf(f, "    label = \"net %d\";\n", src.net);

		std::vector<std::string> global_lines;
		show_seg_tree_worker(f, src, global_lines);
		fprintf(f, "    }\n");

		for (auto &line : global_lines) {
			fprintf(f, "%s", line.c_str());
		}
	}
};

void make_interconn(const net_segment_t &src, FILE *graph_f)
{
	make_interconn_worker_t worker;
	worker.build_net_tree(src.net);
	worker.build_seg_tree(src);

	if (verbose)
	{
		printf("// INTERCONN %d %d %s %d\n", src.x, src.y, src.name.c_str(), src.net);
		std::function<void(int,int)> print_net_tree = [&] (int net, int indent) {
			printf("// %*sNET_TREE %d\n", indent, "", net);
			for (int child : worker.net_tree.at(net))
				print_net_tree(child, indent+2);
		};
		std::function<void(const net_segment_t&,int,bool)> print_seg_tree = [&] (const net_segment_t &seg, int indent, bool chain) {
			printf("// %*sSEG_TREE %d %d %s %d\n", indent, chain ? "`" : "", seg.x, seg.y, seg.name.c_str(), seg.net);
			if (worker.seg_tree.count(seg)) {
				auto &children = worker.seg_tree.at(seg);
				bool child_chain = children.size() == 1;
				for (auto &child : children)
					print_seg_tree(child, child_chain ? (chain ? indent : indent+1) : indent+2, child_chain);
			} else {
				printf("// %*s  DEAD_END (!)\n", indent, "");
			}
		};
		print_net_tree(src.net, 2);
		print_seg_tree(src, 2, false);
	}

	for (auto &seg : worker.target_segs) {
		net_assignments[net_name(seg.net)] = seg_name(seg);
		worker.create_cells(seg);
	}

	for (int n : graph_nets)
		if (worker.net_tree.count(n)) {
			worker.show_seg_tree(src, graph_f);
			break;
		}
}

void help(const char *cmd)
{
	printf("\n");
	printf("Usage: %s [options] input.asc\n", cmd);
	printf("\n");
	printf("    -p <pcf_file>\n");
	printf("    -P <chip_package>\n");
	printf("        provide this two options for correct IO pin names\n");
	printf("\n");
	printf("    -g <net_index>\n");
	printf("        write a graphviz description of the interconnect tree\n");
	printf("        that includes the given net to 'icetime_graph.dot'.\n");
	printf("\n");
	printf("    -o <output_file>\n");
	printf("        write verilog netlist to the file. use '-' for stdout\n");
	printf("\n");
	printf("    -r <output_file>\n");
	printf("        write timing report to the file (instead of stdout)\n");
	printf("\n");
	printf("    -j <output_file>\n");
	printf("        write timing report in json format to the file\n");
	printf("\n");
	printf("    -d lp384|lp1k|hx1k|lp8k|hx8k|up5k\n");
	printf("        select the device type (default = lp variant)\n");
	printf("\n");
	printf("    -C <chipdb-file>\n");
	printf("        read chip description from the specified file\n");
	printf("\n");
	printf("    -m\n");
	printf("        enable max_span_hack for conservative timing estimates\n");
	printf("\n");
	printf("    -i\n");
	printf("        only consider interior timing paths (not to/from IOs)\n");
	printf("\n");
	printf("    -t\n");
	printf("        print a timing report (based on topological timing\n");
	printf("        analysis)\n");
	printf("\n");
	printf("    -T <net_name>\n");
	printf("        print a timing report for the specified net\n");
	printf("\n");
	printf("    -N\n");
	printf("        list valid net names for -T <net_name>\n");
	printf("\n");
	printf("    -c <Mhz>\n");
	printf("        check timing estimate against clock constraint\n");
	printf("\n");
	printf("    -v\n");
	printf("        verbose mode (print all interconnect trees)\n");
	printf("\n");
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

	bool listnets = false;
	bool print_timing = false;
	bool interior_timing = false;
	double clock_constr = 0;
	std::vector<std::string> print_timing_nets;

	int opt;
	while ((opt = getopt(argc, argv, "p:P:g:o:r:j:d:mitT:Nvc:C:")) != -1)
	{
		switch (opt)
		{
		case 'p':
			printf("// Reading input .pcf file..\n");
			fflush(stdout);
			read_pcf(optarg);
			break;
		case 'P':
			selected_package = optarg;
			break;
		case 'g':
			graph_nets.insert(atoi(optarg));
			break;
		case 'o':
			if (!strcmp(optarg, "-")) {
				fout = stdout;
			} else {
				fout = fopen(optarg, "w");
				if (fout == nullptr) {
					perror("Can't open output file");
					exit(1);
				}
			}
			break;
		case 'r':
			frpt = fopen(optarg, "w");
			if (frpt == nullptr) {
				perror("Can't open report file");
				exit(1);
			}
			break;
		case 'j':
			fjson = fopen(optarg, "w");
			if (fjson == nullptr) {
				perror("Can't open json file");
				exit(1);
			}
			break;
		case 'd':
			device_type = optarg;
			break;
		case 'm':
			max_span_hack = true;
			break;
		case 'i':
			interior_timing = true;
			break;
		case 't':
			print_timing = true;
			break;
		case 'T':
			print_timing_nets.push_back(optarg);
			break;
		case 'N':
			listnets = true;
			break;
		case 'c':
			clock_constr = strtod(optarg, NULL);
			break;
		case 'C':
			chipdbfile = optarg;
			break;
		case 'v':
			verbose = true;
			break;
		default:
			help(argv[0]);
		}
	}

	if (optind+1 == argc) {
		fin = fopen(argv[optind], "r");
		if (fin == nullptr) {
			perror("Can't open input file");
			exit(1);
		}
	} else
		help(argv[0]);

	printf("// Reading input .asc file..\n");
	fflush(stdout);
	read_config();

	std::transform(config_device.begin(), config_device.end(), config_device.begin(), ::tolower);

	if (device_type.empty()) {
		if(config_device == "5k")
			device_type = "up" + config_device;
		else
			device_type = "lp" + config_device;
		printf("// Warning: Missing -d parameter. Assuming '%s' device.\n", device_type.c_str());
	}

	std::transform(device_type.begin(), device_type.end(), device_type.begin(), ::tolower);

	if (device_type == "lp384") {
		if (config_device != "384")
			goto device_chip_mismatch;
	} else
	if (device_type == "lp1k" || device_type == "hx1k") {
		if (config_device != "1k")
			goto device_chip_mismatch;
	} else
	if (device_type == "lp8k" || device_type == "hx8k") {
		if (config_device != "8k")
			goto device_chip_mismatch;
	} else
	if (device_type == "up5k") {
		if (config_device != "5k")
			goto device_chip_mismatch;
	} else {
		fprintf(stderr, "Error: Invalid device type '%s'.\n", device_type.c_str());
		exit(1);
	}

	if (0) {
device_chip_mismatch:
		printf("// Warning: Device type '%s' and chip '%s' do not match.\n", device_type.c_str(), config_device.c_str());
		fflush(stdout);
	}

	printf("// Reading %s chipdb file..\n", config_device.c_str());
	fflush(stdout);
	read_chipdb();

	printf("// Creating timing netlist..\n");
	fflush(stdout);

	for (int net : used_nets)
	for (auto &seg : net_to_segments[net])
		make_seg_cell(net, seg);

	for (int x = 0; x < int(config_tile_type.size()); x++)
	for (int y = 0; y < int(config_tile_type[x].size()); y++)
	{
		auto const &tile_type = config_tile_type[x][y];

		if (tile_type == "ramb")
		{
			bool cascade_cbits[4] = {false, false, false, false};
			bool &cascade_cbit_4 = cascade_cbits[0];
			// bool &cascade_cbit_5 = cascade_cbits[1];
			bool &cascade_cbit_6 = cascade_cbits[2];
			// bool &cascade_cbit_7 = cascade_cbits[3];
			std::pair<int, int> bitpos;

			for (int i = 0; i < 4; i++) {
				std::string cbit_name = stringf("RamCascade.CBIT_%d", i+4);
				if (ramb_tile_bits.count(cbit_name)) {
					bitpos = ramb_tile_bits.at(cbit_name)[0];
					cascade_cbits[i] = get_config_bit(x, y, bitpos.first, bitpos.second);
				}
				if (ramt_tile_bits.count(cbit_name)) {
					bitpos = ramt_tile_bits.at(cbit_name)[0];
					cascade_cbits[i] = get_config_bit(x, y+1, bitpos.first, bitpos.second);
				}
			}

			if (cascade_cbit_4)
			{
				std::string src_cell = stringf("ram_%d_%d", x, y+2);
				std::string dst_cell = stringf("ram_%d_%d", x, y);

				for (int i = 0; i < 11; i++)
				{
					std::string port = stringf("WADDR[%d]", i);

					if (netlist_cell_ports[src_cell][port] == "")
						continue;

					std::string srcnet = netlist_cell_ports[src_cell][port];
					std::string tmpnet = tname();
					extra_wires.insert(tmpnet);

					std::string tn = tname();
					netlist_cell_types[tn] = "CascadeBuf";
					netlist_cell_ports[tn]["I"] = srcnet;
					netlist_cell_ports[tn]["O"] = tmpnet;

					netlist_cell_ports[dst_cell][port] = cascademuxed(tmpnet);
				}
			}

			if (cascade_cbit_6)
			{
				std::string src_cell = stringf("ram_%d_%d", x, y+2);
				std::string dst_cell = stringf("ram_%d_%d", x, y);

				for (int i = 0; i < 11; i++)
				{
					std::string port = stringf("RADDR[%d]", i);

					if (netlist_cell_ports[src_cell][port] == "")
						continue;

					std::string srcnet = netlist_cell_ports[src_cell][port];
					std::string tmpnet = tname();
					extra_wires.insert(tmpnet);

					std::string tn = tname();
					netlist_cell_types[tn] = "CascadeBuf";
					netlist_cell_ports[tn]["I"] = srcnet;
					netlist_cell_ports[tn]["O"] = tmpnet;

					netlist_cell_ports[dst_cell][port] = cascademuxed(tmpnet);
				}
			}
		}
	}

	FILE *graph_f = nullptr;

	if (!graph_nets.empty())
	{
		graph_f = fopen("icetime_graph.dot", "w");
		if (graph_f == nullptr) {
			perror("Can't open 'icetime_graph.dot' for writing");
			exit(1);
		}

		fprintf(graph_f, "digraph \"icetime net-segment graph \" {\n");
		fprintf(graph_f, "  rankdir = \"LR\";\n");
	}

	for (auto &seg : interconn_src)
		make_interconn(seg, graph_f);

	if (graph_f) {
		fprintf(graph_f, "}\n");
		fclose(graph_f);
	}

	for (auto it : netlist_cell_types)
	for (auto &port : netlist_cell_ports[it.first])
		if (port.second == "") {
			size_t open_bracket_pos = port.first.find('[');
			if (open_bracket_pos == std::string::npos)
				continue;
			port.second = stringf("dangling_wire_%d", dangling_cnt++);
			extra_wires.insert(port.second);
		}

	if (fout != NULL)
	{
		fprintf(fout, "module chip (");
		const char *io_sep = "";
		for (auto io : io_names) {
			fprintf(fout, "%s%s", io_sep, io.c_str());
			io_sep = ", ";
		}
		fprintf(fout, ");\n");

		for (int net : declared_nets)
			fprintf(fout, "  wire net_%d;\n", net);

		for (auto net : extra_wires)
			fprintf(fout, "  wire %s;\n", net.c_str());

		for (auto &it : net_assignments)
			fprintf(fout, "  assign %s = %s;\n", it.first.c_str(), it.second.c_str());

		fprintf(fout, "  wire gnd, vcc;\n");
		fprintf(fout, "  GND gnd_cell (.Y(gnd));\n");
		fprintf(fout, "  VCC vcc_cell (.Y(vcc));\n");

		for (auto &str : extra_vlog)
			fprintf(fout, "%s", str.c_str());

		for (auto it : netlist_cell_types)
		{
			const char *sep = "";
			fprintf(fout, "  %s ", it.second.c_str());
			if (netlist_cell_params.count(it.first)) {
				fprintf(fout, "#(");
				for (auto port : netlist_cell_params[it.first]) {
					fprintf(fout, "%s\n    .%s(%s)", sep, port.first.c_str(), port.second.c_str());
					sep = ",";
				}
				fprintf(fout, "\n  ) ");
				sep = "";
			}

			fprintf(fout, "%s (", it.first.c_str());
			std::map<std::string, std::vector<std::string>> multibit_ports;

			for (auto port : netlist_cell_ports[it.first])
			{
				size_t open_bracket_pos = port.first.find('[');
				if (open_bracket_pos != std::string::npos) {
					std::string base_name = port.first.substr(0, open_bracket_pos);
					int bit_index = atoi(port.first.substr(open_bracket_pos+1).c_str());
					if (int(multibit_ports[base_name].size()) <= bit_index)
						multibit_ports[base_name].resize(bit_index+1);
					multibit_ports[base_name][bit_index] = port.second;
					continue;
				}

				fprintf(fout, "%s\n    .%s(%s)", sep, port.first.c_str(), port.second.c_str());
				sep = ",";
			}

			for (auto it : multibit_ports)
			{
				fprintf(fout, "%s\n    .%s({", sep, it.first.c_str());
				sep = ",";

				const char *sepsep = "";
				for (int i = int(it.second.size())-1; i >= 0; i--) {
					std::string wire_name = it.second[i];
					fprintf(fout, "%s%s", sepsep, wire_name.c_str());
					sepsep = ", ";
				}
				fprintf(fout, "})");
			}

			fprintf(fout, "\n  );\n");
		}

		fprintf(fout, "endmodule\n");
	}

	double max_path_delay = 0;

	if (fjson)
		fprintf(fjson, "[\n");

	if (print_timing || listnets || !print_timing_nets.empty())
	{
		TimingAnalysis ta(interior_timing);

		if (frpt == nullptr)
			frpt = stdout;
		else
			printf("// Timing estimate: %.2f ns (%.2f MHz)\n", ta.global_max_path_delay, 1000.0 / ta.global_max_path_delay);

		fprintf(frpt, "\n");
		fprintf(frpt, "icetime topological timing analysis report\n");
		fprintf(frpt, "==========================================\n");
		fprintf(frpt, "\n");

		if (max_span_hack) {
			fprintf(frpt, "Info: max_span_hack is enabled: estimate is conservative.\n");
			fprintf(frpt, "\n");
		}

		for (auto &n : print_timing_nets)
			max_path_delay = std::max(max_path_delay, ta.report(n));

		if (print_timing)
			max_path_delay = ta.report();

		if (listnets)
			for (auto &it : ta.net_max_path_delay)
				fprintf(frpt, "%s\n", it.first.c_str());
	}
	else
	{
		TimingAnalysis ta(interior_timing);
		printf("// Timing estimate: %.2f ns (%.2f MHz)\n", ta.global_max_path_delay, 1000.0 / ta.global_max_path_delay);
		max_path_delay = ta.report();
	}

	if (clock_constr > 0) {
		printf("// Checking %.2f ns (%.2f MHz) clock constraint: ", 1000.0 / clock_constr, clock_constr);
		if (max_path_delay <= 1000.0 / clock_constr) {
			printf("PASSED.\n");
		} else {
			printf("FAILED.\n");
			return 1;
		}
	}

	if (fjson) {
		if (!json_firstentry)
			fprintf(fjson, "  ]\n");
		fprintf(fjson, "]\n");
	}

	return 0;
}
