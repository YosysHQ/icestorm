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
std::vector<std::set<net_segment_name>> net_to_segments;
std::map<int, std::set<int>> net_buffers, net_rbuffers, net_routing;
std::set<int> used_nets;

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
				if (current_net >= int(net_to_segments.size()))
					net_to_segments.resize(current_net+1);
			}

			if (mode == ".buffer" || mode == ".routing")
			{
				int tile_x = atoi(strtok(nullptr, " \t\r\n"));
				int tile_y = atoi(strtok(nullptr, " \t\r\n"));
				current_net = atoi(strtok(nullptr, " \t\r\n"));

				thiscfg = "";
				while ((tok = strtok(nullptr, " \t\r\n")) != nullptr) {
					int bit_row, bit_col, rc;
					rc = sscanf(tok, "B%d[%d]", &bit_row, &bit_col);
					assert(rc == 2);
					thiscfg.push_back(config_bits[tile_x][tile_y][bit_row][bit_col] ? '1' : '0');
				}
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
			used_nets.insert(current_net);
			used_nets.insert(other_net);
		}

		if (mode == ".routing" && !strcmp(tok, thiscfg.c_str())) {
			int other_net = atoi(strtok(nullptr, " \t\r\n"));
			net_routing[current_net].insert(other_net);
			net_routing[other_net].insert(current_net);
			used_nets.insert(current_net);
			used_nets.insert(other_net);
		}
	}

	fclose(fdb);
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

	return 0;
}
