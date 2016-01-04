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

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <string.h>
#include <stdarg.h>

#include <functional>
#include <string>
#include <vector>
#include <tuple>
#include <map>
#include <set>

#define MAX_SPAN_HACK 1

FILE *fin, *fout;

std::string config_device, selected_package;
std::vector<std::vector<std::string>> config_tile_type;
std::vector<std::vector<std::vector<std::vector<bool>>>> config_bits;
std::map<std::tuple<int, int, int>, std::string> pin_pos;
std::map<std::string, std::string> pin_names;
std::set<std::tuple<int, int, int>> extra_bits;
std::set<std::string> io_names;

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

// netlist_cells[cell_name][port_name] = port_expr
std::map<std::string, std::map<std::string, std::string>> netlist_cells;
std::map<std::string, std::map<std::string, std::string>> netlist_cell_params;
std::map<std::string, std::string> netlist_cell_types;

std::set<std::string> extra_wires;
std::vector<std::string> extra_vlog;
std::set<int> declared_nets;

std::map<std::string, std::vector<std::pair<int, int>>> logic_tile_bits,
		io_tile_bits, ramb_tile_bits, ramt_tile_bits;

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
		if (buffer[0] == '#')
			continue;

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
	char buffer[128];
	int tile_x, tile_y, line_nr = -1;

	while (fgets(buffer, 128, fin))
	{
		if (buffer[0] == '.')
		{
			line_nr = -1;
			const char *tok = strtok(buffer, " \t\r\n");

			if (!strcmp(tok, ".device"))
			{
				config_device = strtok(nullptr, " \t\r\n");
			} else
			if (!strcmp(tok, ".io_tile") || !strcmp(tok, ".logic_tile") ||
					!strcmp(tok, ".ramb_tile") || !strcmp(tok, ".ramt_tile"))
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
			} else
			if (!strcmp(tok, ".extra_bit")) {
				int b = atoi(strtok(nullptr, " \t\r\n"));
				int x = atoi(strtok(nullptr, " \t\r\n"));
				int y = atoi(strtok(nullptr, " \t\r\n"));
				std::tuple<int, int, int> key(b, x, y);
				extra_bits.insert(key);
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
	snprintf(buffer, 1024, "/usr/local/share/icebox/chipdb-%s.txt", config_device.c_str());

	FILE *fdb = fopen(buffer, "r");
	if (fdb == nullptr) {
		perror("Can't open chipdb file");
		exit(1);
	}


	std::string mode;
	int current_net = -1;
	int tile_x = -1, tile_y = -1;
	std::string thiscfg;

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
					thiscfg.push_back(config_bits[tile_x][tile_y][bit_row][bit_col] ? '1' : '0');
				}
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

		if (mode == ".logic_tile_bits" || mode == ".io_tile_bits" || mode == ".ramb_tile_bits" || mode == ".ramt_tile_bits") {
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
		}

		if (mode == ".extra_bits") {
			int b = atoi(strtok(nullptr, " \t\r\n"));
			int x = atoi(strtok(nullptr, " \t\r\n"));
			int y = atoi(strtok(nullptr, " \t\r\n"));
			std::tuple<int, int, int> key(b, x, y);
			if (extra_bits.count(key))
				extrabitfunc.insert(tok);
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


#if 1
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
#endif
}

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
	netlist_cells[cell]["PADIN"] = stringf("io_pad_%d_%d_%d_dout", x, y, z);
	netlist_cells[cell]["PADOUT"] = stringf("io_pad_%d_%d_%d_din", x, y, z);
	netlist_cells[cell]["PADOEN"] = stringf("io_pad_%d_%d_%d_oe", x, y, z);
	netlist_cells[cell]["LATCHINPUTVALUE"] = "";
	netlist_cells[cell]["CLOCKENABLE"] = "";
	netlist_cells[cell]["INPUTCLK"] = "";
	netlist_cells[cell]["OUTPUTCLK"] = "";
	netlist_cells[cell]["OUTPUTENABLE"] = "";
	netlist_cells[cell]["DOUT1"] = "";
	netlist_cells[cell]["DOUT0"] = "";
	netlist_cells[cell]["DIN1"] = "";
	netlist_cells[cell]["DIN0"] = "";

	std::string pintype;
	std::pair<int, int> bitpos;

	for (int i = 0; i < 6; i++) {
		bitpos = io_tile_bits[stringf("IOB_%d.PINTYPE_%d", z, 5-i)][0];
		pintype.push_back(config_bits[x][y][bitpos.first][bitpos.second] ? '1' : '0');
	}

	bitpos = io_tile_bits["NegClk"][0];
	char negclk = config_bits[x][y][bitpos.first][bitpos.second] ? '1' : '0';

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
	auto cell = stringf("lc40_%d_%d_%d", x, y, z);

	if (netlist_cell_types.count(cell))
		return cell;

	netlist_cell_types[cell] = "LogicCell40";
	netlist_cells[cell]["carryin"] = "gnd";
	netlist_cells[cell]["ce"] = "";
	netlist_cells[cell]["clk"] = "gnd";
	netlist_cells[cell]["in0"] = "gnd";
	netlist_cells[cell]["in1"] = "gnd";
	netlist_cells[cell]["in2"] = "gnd";
	netlist_cells[cell]["in3"] = "gnd";
	netlist_cells[cell]["sr"] = "gnd";
	netlist_cells[cell]["carryout"] = "";
	netlist_cells[cell]["lcout"] = "";
	netlist_cells[cell]["ltout"] = "";

	char lcbits[20];
	auto &lcbits_pos = logic_tile_bits[stringf("LC_%d", z)];

	for (int i = 0; i < 20; i++)
		lcbits[i] = config_bits[x][y][lcbits_pos[i].first][lcbits_pos[i].second] ? '1' : '0';

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
			auto co_cell = make_lc40(x, y-1, 7);
			std::string n1, n2;

			char cinit_1 = config_bits[x][y][1][49] ? '1' : '0';
			char cinit_0 = config_bits[x][y][1][50] ? '1' : '0';

			if (cinit_1 == '1') {
				std::tuple<int, int, std::string> key(x, y-1, "lutff_7/cout");
				if (x_y_name_net.count(key)) {
					n1 = net_name(x_y_name_net.at(key));
				} else {
					n1 = tname();
					netlist_cells[co_cell]["carryout"] = n1;
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

			extra_vlog.push_back(stringf("  ICE_CARRY_IN_MUX #(.C_INIT(2'b%c%c)) %s (.carryinitin(%s), "
					".carryinitout(%s));\n", cinit_1, cinit_0, tname().c_str(), n1.c_str(), n2.c_str()));
			netlist_cells[cell]["carryin"] = n2;
		}
		else
		{
			auto co_cell = make_lc40(x, y, z-1);
			std::tuple<int, int, std::string> key(x, y, stringf("lutff_%d/cout", z-1));
			auto n = x_y_name_net.count(key) ? net_name(x_y_name_net.at(key)) : tname();

			netlist_cells[co_cell]["carryout"] = n;
			netlist_cells[cell]["carryin"] = n;
			extra_wires.insert(n);
		}

		std::tuple<int, int, std::string> key(x, y, stringf("lutff_%d/cout", z-1));
	}

	return cell;
}

bool dff_uses_clock(int x, int y, int z)
{
	auto bitpos = logic_tile_bits[stringf("LC_%d", z)][9];
	return config_bits[x][y][bitpos.first][bitpos.second];
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
		netlist_cells[cell]["I"] = net_name(src);
		netlist_cells[cell]["O"] = net_name(dst);
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

		if (src_name == "lutff_X/out") {
			auto cell = make_lc40(x, y, cascade_n);
			netlist_cells[cell]["ltout"] = net_name(dst);
			continue;
		}

		auto cell = stringf("inmux_%d_%d_%d_%d", x, y, src, dst);

		if (netlist_cell_types.count(cell))
			continue;

		netlist_cell_types[cell] = muxtype.empty() ? (config_tile_type[x][y] == "io" ? "IoInMux" : "InMux") : muxtype;
		netlist_cells[cell]["I"] = net_name(src);
		netlist_cells[cell]["O"] = net_name(dst);

		register_interconn_dst(x, y, src);
		no_interconn_net.insert(dst);
	}
}

void make_seg_cell(int net, const net_segment_t &seg)
{
	int a = -1, b = -1;
	char c = 0;

	if (sscanf(seg.name.c_str(), "io_%d/D_IN_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.x, seg.y, a);
		netlist_cells[cell][stringf("DIN%d", b)] = net_name(net);
		make_odrv(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "io_%d/D_OUT_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.x, seg.y, a);
		netlist_cells[cell][stringf("DOUT%d", b)] = net_name(net);
		make_inmux(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "lutff_%d/in_%d", &a, &b) == 2) {
		auto cell = make_lc40(seg.x, seg.y, a);
		if (b == 2) {
			// Lattice tools always put a CascadeMux on in2
			extra_wires.insert(net_name(net) + "_cascademuxed");
			extra_vlog.push_back(stringf("  CascadeMux %s (.I(%s), .O(%s));\n",
					tname().c_str(), net_name(net).c_str(), (net_name(net) + "_cascademuxed").c_str()));
			netlist_cells[cell][stringf("in%d", b)] = net_name(net) + "_cascademuxed";
		} else {
			netlist_cells[cell][stringf("in%d", b)] = net_name(net);
		}
		make_inmux(seg.x, seg.y, net);
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
		netlist_cells[cell]["lcout"] = net_name(net);
		make_odrv(seg.x, seg.y, net);
		return;
	}

	if (sscanf(seg.name.c_str(), "lutff_%d/cou%c", &a, &c) == 2 && c == 't')
	{
		auto cell = make_lc40(seg.x, seg.y, a);
		netlist_cells[cell]["carryout"] = net_name(net);
		return;
	}

	if (seg.name == "lutff_global/clk")
	{
		for (int i = 0; i < 8; i++)
		{
			if (!dff_uses_clock(seg.x, seg.y, i))
				continue;

			std::tuple<int, int, std::string> key(seg.x, seg.y, stringf("lutff_%d/out", i));
			if (x_y_name_net.count(key)) {
				auto cell = make_lc40(seg.x, seg.y, i);
				make_inmux(seg.x, seg.y, net, "ClkMux");
				netlist_cells[cell]["clk"] = net_name(seg.net);
			}
		}
		return;
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
			extra_vlog.push_back(stringf("  assign %s = %s;\n", seg_name(trg).c_str(), net_name(trg.net).c_str()));
			return;
		}

		const net_segment_t *cursor = &seg_parents.at(trg);

		// Local Mux

		if (trg.name.substr(0, 6) == "local_")
		{
			extra_vlog.push_back(stringf("  LocalMux %s (.I(%s), .O(%s));\n",
					tname().c_str(), seg_name(*cursor).c_str(), seg_name(trg).c_str()));
			cell_log[trg] = std::make_pair(*cursor, "LocalMux");
			goto continue_at_cursor;
		}

		// Span4Mux

		if (trg.name.substr(0, 6) == "span4_" || trg.name.substr(0, 4) == "sp4_")
		{
			bool horiz = trg.name.substr(0, 6) == "sp4_h_";
			int count_length = -1;

			while (seg_parents.count(*cursor) && cursor->net == trg.net) {
				horiz = horiz || (cursor->name.substr(0, 6) == "sp4_h_");
				cursor = &seg_parents.at(*cursor);
				count_length++;
			}

			if (cursor->net == trg.net)
				goto skip_to_cursor;

			count_length = std::max(count_length, 0);

			if (cursor->name.substr(0, 7) == "span12_" || cursor->name.substr(0, 5) == "sp12_") {
				extra_vlog.push_back(stringf("  Sp12to4 %s (.I(%s), .O(%s));\n",
						tname().c_str(), seg_name(*cursor).c_str(), seg_name(trg).c_str()));
				cell_log[trg] = std::make_pair(*cursor, "Sp12to4");
			} else
			if (cursor->name.substr(0, 6) == "span4_") {
				extra_vlog.push_back(stringf("  IoSpan4Mux %s (.I(%s), .O(%s));\n",
						tname().c_str(), seg_name(*cursor).c_str(), seg_name(trg).c_str()));
				cell_log[trg] = std::make_pair(*cursor, "IoSpan4Mux");
			} else {
				extra_vlog.push_back(stringf("  Span4Mux_%c%d %s (.I(%s), .O(%s));\n",
						horiz ? 'h' : 'v', MAX_SPAN_HACK ? 4 : count_length, tname().c_str(),
						seg_name(*cursor).c_str(), seg_name(trg).c_str()));
				cell_log[trg] = std::make_pair(*cursor, stringf("Span4Mux_%c%d", horiz ? 'h' : 'v', count_length));
			}

			goto continue_at_cursor;
		}

		// Span12Mux

		if (trg.name.substr(0, 7) == "span12_" || trg.name.substr(0, 5) == "sp12_")
		{
			bool horiz = trg.name.substr(0, 7) == "sp12_h_";
			int count_length = -1;

			while (seg_parents.count(*cursor) && cursor->net == trg.net) {
				horiz = horiz || (cursor->name.substr(0, 7) == "sp12_h_");
				cursor = &seg_parents.at(*cursor);
				count_length++;
			}

			if (cursor->net == trg.net)
				goto skip_to_cursor;

			count_length = std::max(count_length, 0);

			extra_vlog.push_back(stringf("  Span12Mux_%c%d %s (.I(%s), .O(%s));\n",
					horiz ? 'h' : 'v', MAX_SPAN_HACK ? 12 : count_length, tname().c_str(),
					seg_name(*cursor).c_str(), seg_name(trg).c_str()));
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

			extra_vlog.push_back(stringf("  GlobalMux %s (.I(%s), .O(%s));\n",
					tname().c_str(), seg_name(*cursor, 3).c_str(), seg_name(trg).c_str()));

			extra_vlog.push_back(stringf("  gio2CtrlBuf %s (.I(%s), .O(%s));\n",
					tname().c_str(), seg_name(*cursor, 2).c_str(), seg_name(*cursor, 3).c_str()));

			extra_vlog.push_back(stringf("  ICE_GB %s (.USERSIGNALTOGLOBALBUFFER(%s), .GLOBALBUFFEROUTPUT(%s));\n",
					tname().c_str(), seg_name(*cursor, 1).c_str(), seg_name(*cursor, 2).c_str()));

			extra_vlog.push_back(stringf("  IoInMux %s (.I(%s), .O(%s));\n",
					tname().c_str(), seg_name(*cursor).c_str(), seg_name(*cursor, 1).c_str()));

			cell_log[trg] = std::make_pair(*cursor, "GlobalMux -> ICE_GB -> IoInMux");

			handled_global_nets.insert(trg.net);
			goto continue_at_cursor;
		}

		// Default handler

		while (seg_parents.count(*cursor) && cursor->net == trg.net)
			cursor = &seg_parents.at(*cursor);

		if (cursor->net == trg.net)
			goto skip_to_cursor;

		extra_vlog.push_back(stringf("  INTERCONN %s (.I(%s), .O(%s));\n",
				tname().c_str(), seg_name(*cursor).c_str(), seg_name(trg).c_str()));
		cell_log[trg] = std::make_pair(*cursor, "INTERCONN");
		goto continue_at_cursor;

	skip_to_cursor:
		extra_vlog.push_back(stringf("  assign %s = %s;\n", seg_name(trg).c_str(), seg_name(*cursor).c_str()));
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

#if 1
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
#endif

	for (auto &seg : worker.target_segs) {
		extra_vlog.push_back(stringf("  assign %s = %s;\n", net_name(seg.net).c_str(), seg_name(seg).c_str()));
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
	printf("Usage: %s [options] input.asc [output.v]\n", cmd);
	printf("\n");
	printf("    -p <pcf_file>\n");
	printf("    -P <chip_package>\n");
	printf("        provide this two options for correct IO pin names\n");
	printf("\n");
	printf("    -g <net_index>\n");
	printf("        write a graphviz description of the interconnect tree\n");
	printf("        that includes the given net to 'icetime_graph.dot'.\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	int opt;
	while ((opt = getopt(argc, argv, "p:P:g:")) != -1)
	{
		switch (opt)
		{
		case 'p':
			printf("// Reading input .pcf file..\n");
			read_pcf(optarg);
			break;
		case 'P':
			selected_package = optarg;
			break;
		case 'g':
			graph_nets.insert(atoi(optarg));
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
		fout = stdout;
	} else
	if (optind+2 == argc) {
		fin = fopen(argv[optind], "r");
		if (fin == nullptr) {
			perror("Can't open input file");
			exit(1);
		}
		fout = fopen(argv[optind+1], "w");
		if (fout == nullptr) {
			perror("Can't open output file");
			exit(1);
		}
	} else
		help(argv[0]);

	printf("// Reading input .asc file..\n");
	read_config();

	printf("// Reading chipdb file..\n");
	read_chipdb();

	for (int net : used_nets)
	for (auto &seg : net_to_segments[net])
		make_seg_cell(net, seg);

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

	fprintf(fout, "  wire gnd, vcc;\n");
	fprintf(fout, "  GND gnd_cell (.Y(gnd));\n");
	fprintf(fout, "  VCC vcc_cell (.Y(vcc));\n");

	for (auto &str : extra_vlog)
		fprintf(fout, "%s", str.c_str());

	for (auto it : netlist_cell_types) {
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
		for (auto port : netlist_cells[it.first]) {
			fprintf(fout, "%s\n    .%s(%s)", sep, port.first.c_str(), port.second.c_str());
			sep = ",";
		}
		fprintf(fout, "\n  );\n");
	}

	fprintf(fout, "endmodule\n");

	return 0;
}
