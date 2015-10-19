#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <string.h> 
#include <string>
#include <vector>
#include <map>
#include <set>

FILE *fin, *fout;

std::string config_device;
std::vector<std::vector<std::string>> config_tile_type;
std::vector<std::vector<std::vector<std::vector<bool>>>> config_bits;

struct net_segment_name
{
	int tile_x, tile_y;
	std::string segment_name;

	net_segment_name(int x, int y, std::string n) :
		tile_x(x), tile_y(y), segment_name(n) { }
	
	bool operator<(const net_segment_name &other) const {
		if (tile_x != other.tile_x)
			return tile_x < other.tile_x;
		if (tile_y != other.tile_y)
			return tile_y < other.tile_y;
		return segment_name < other.segment_name;
	}
};

std::map<net_segment_name, int> segment_to_net;
std::map<int, std::set<net_segment_name>> net_to_segments;
std::map<int, std::set<int>> net_buffers, net_rbuffers, net_routing;
std::map<std::pair<int, int>, std::pair<int, int>> connection_pos;
std::set<int> used_nets;

// netlist_cells[cell_name][port_name] = port_expr
std::map<std::string, std::map<std::string, std::string>> netlist_cells;
std::map<std::string, std::string> netlist_cell_types;

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

		if (mode == ".net") {
			int tile_x = atoi(tok);
			int tile_y = atoi(strtok(nullptr, " \t\r\n"));
			std::string segment_name = strtok(nullptr, " \t\r\n");
			net_segment_name seg(tile_x, tile_y, segment_name);
			segment_to_net[seg] = current_net;
			net_to_segments[current_net].insert(seg);
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
	}

	fclose(fdb);

	// purge unused nets from memory
	int max_net = net_to_segments.rbegin()->first;
	for (int net = 0; net <= max_net; net++)
	{
		if (used_nets.count(net))
			continue;

		for (auto seg : net_to_segments[net])
			segment_to_net.erase(seg);
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

#if 1
	for (int net : used_nets)
	{
		printf("// NET %d:\n", net);
		for (auto seg : net_to_segments[net])
			printf("//  SEG %d %d %s\n", seg.tile_x, seg.tile_y, seg.segment_name.c_str());
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

	fprintf(fout, "  wire io_pad_%d_%d_%d_din;\n", x, y, z);
	fprintf(fout, "  wire io_pad_%d_%d_%d_dout;\n", x, y, z);
	fprintf(fout, "  wire io_pad_%d_%d_%d_oe;\n", x, y, z);
	fprintf(fout, "  (* keep *) wire io_pad_%d_%d_%d_pin;\n", x, y, z);
	fprintf(fout, "  IO_PAD io_pad_%d_%d_%d (\n", x, y, z);
	fprintf(fout, "    .DIN(io_pad_%d_%d_%d_din),\n", x, y, z);
	fprintf(fout, "    .DOUT(io_pad_%d_%d_%d_dout),\n", x, y, z);
	fprintf(fout, "    .OE(io_pad_%d_%d_%d_oe),\n", x, y, z);
	fprintf(fout, "    .PACKAGEPIN(io_pad_%d_%d_%d_pin)\n", x, y, z);
	fprintf(fout, "  );\n");

	return cell;
}

void make_seg_cell(int net, const net_segment_name &seg)
{
	int a, b;

	if (sscanf(seg.segment_name.c_str(), "io_%d/D_IN_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.tile_x, seg.tile_y, a);
		netlist_cells[cell][stringf("DIN%d", b)] = stringf("net_%d", net);
		return;
	}

	if (sscanf(seg.segment_name.c_str(), "io_%d/D_OUT_%d", &a, &b) == 2) {
		auto cell = make_seg_pre_io(seg.tile_x, seg.tile_y, a);
		netlist_cells[cell][stringf("DOUT%d", b)] = stringf("net_%d", net);
		return;
	}
}

void help(const char *cmd)
{
	printf("\n");
	printf("Usage: %s [options] input.txt [output.v]\n", cmd);
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	int opt;
	while ((opt = getopt(argc, argv, "")) != -1)
	{
		switch (opt)
		{
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

	printf("// Reading input .txt file..\n");
	read_config();

	printf("// Reading chipdb file..\n");
	read_chipdb();

	fprintf(fout, "module chip;\n");

	for (int net : used_nets)
		fprintf(fout, "  wire net_%d;\n", net);

	for (int net : used_nets)
	for (auto seg : net_to_segments[net])
		make_seg_cell(net, seg);

	for (auto it : netlist_cell_types) {
		const char *sep = "";
		fprintf(fout, "  %s %s (", it.second.c_str(), it.first.c_str());
		for (auto port : netlist_cells[it.first]) {
			fprintf(fout, "%s\n    .%s(%s)", sep, port.first.c_str(), port.second.c_str());
			sep = ",";
		}
		fprintf(fout, "\n  );\n");
	}

	fprintf(fout, "endmodule\n");

	return 0;
}
