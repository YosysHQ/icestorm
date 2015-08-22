#!/usr/bin/env python3
#
#  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import iceboxdb
import re, sys

class iceconfig:
    def __init__(self):
        self.clear()

    def clear(self):
        self.max_x = 0
        self.max_y = 0
        self.device = ""
        self.logic_tiles = dict()
        self.io_tiles = dict()
        self.ramb_tiles = dict()
        self.ramt_tiles = dict()
        self.ram_data = dict()
        self.extra_bits = set()
        self.symbols = dict()

    def setup_empty_1k(self):
        self.clear()
        self.device = "1k"
        self.max_x = 13
        self.max_y = 17

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (3, 10):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def setup_empty_8k(self):
        self.clear()
        self.device = "8k"
        self.max_x = 33
        self.max_y = 33

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (8, 25):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def lookup_extra_bit(self, bit):
        assert self.device in extra_bits_db
        if bit in extra_bits_db[self.device]:
            return extra_bits_db[self.device][bit]
        return ("UNKNOWN_FUNCTION",)

    def tile(self, x, y):
        if (x, y) in self.io_tiles: return self.io_tiles[(x, y)]
        if (x, y) in self.logic_tiles: return self.logic_tiles[(x, y)]
        if (x, y) in self.ramb_tiles: return self.ramb_tiles[(x, y)]
        if (x, y) in self.ramt_tiles: return self.ramt_tiles[(x, y)]
        return None

    def pinloc_db(self):
        if self.device == "1k": return pinloc_db["1k-tq144"]
        if self.device == "8k": return pinloc_db["8k-ct256"]
        assert False

    def gbufin_db(self):
        return gbufin_db[self.device]

    def iolatch_db(self):
        return iolatch_db[self.device]

    def padin_pio_db(self):
        return padin_pio_db[self.device]

    def extra_bits_db(self):
        return extra_bits_db[self.device]

    def ieren_db(self):
        return ieren_db[self.device]

    def pll_list(self):
        if self.device == "1k":
            return ["1k"]
        if self.device == "8k":
            return ["8k_0", "8k_1"]
        assert False

    def colbuf_db(self):
        if self.device == "1k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  4: src_y =  4
                    if  5 <= y <=  8: src_y =  5
                    if  9 <= y <= 12: src_y = 12
                    if 13 <= y <= 17: src_y = 13
                    if x in [3, 10] and src_y ==  4: src_y =  3
                    if x in [3, 10] and src_y == 12: src_y = 11
                    entries.append((x, src_y, x, y))
            return entries

        if self.device == "8k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  8: src_y =  8
                    if  9 <= y <= 16: src_y =  9
                    if 17 <= y <= 24: src_y = 24
                    if 25 <= y <= 33: src_y = 25
                    entries.append((x, src_y, x, y))
            return entries

        assert False

    def tile_db(self, x, y):
        if x == 0: return iotile_l_db
        if y == 0: return iotile_b_db
        if x == self.max_x: return iotile_r_db
        if y == self.max_y: return iotile_t_db
        if self.device == "1k":
            if (x, y) in self.logic_tiles: return logictile_db
            if (x, y) in self.ramb_tiles: return rambtile_db
            if (x, y) in self.ramt_tiles: return ramttile_db
        if self.device == "8k":
            if (x, y) in self.logic_tiles: return logictile_8k_db
            if (x, y) in self.ramb_tiles: return rambtile_8k_db
            if (x, y) in self.ramt_tiles: return ramttile_8k_db
        assert False

    def tile_type(self, x, y):
        if x == 0: return "IO"
        if y == 0: return "IO"
        if x == self.max_x: return "IO"
        if y == self.max_y: return "IO"
        if (x, y) in self.ramb_tiles: return "RAMB"
        if (x, y) in self.ramt_tiles: return "RAMT"
        if (x, y) in self.logic_tiles: return "LOGIC"
        assert False

    def tile_pos(self, x, y):
        if x == 0 and 0 < y < self.max_y: return "l"
        if y == 0 and 0 < x < self.max_x: return "b"
        if x == self.max_x and 0 < y < self.max_y: return "r"
        if y == self.max_y and 0 < x < self.max_x: return "t"
        if 0 < x < self.max_x and 0 < y < self.max_y: return "x"
        return None

    def tile_has_entry(self, x, y, entry):
        if entry[1] in ("routing", "buffer"):
            return self.tile_has_net(x, y, entry[2]) and self.tile_has_net(x, y, entry[3])
        return True

    def tile_has_net(self, x, y, netname):
        if netname.startswith("logic_op_"):
            if netname.startswith("logic_op_bot_"):
                if y == self.max_y and 0 < x < self.max_x: return True
            if netname.startswith("logic_op_bnl_"):
                if x == self.max_x and 1 < y < self.max_y: return True
                if y == self.max_y and 1 < x < self.max_x: return True
            if netname.startswith("logic_op_bnr_"):
                if x == 0 and 1 < y < self.max_y: return True
                if y == self.max_y and 0 < x < self.max_x-1: return True

            if netname.startswith("logic_op_top_"):
                if y == 0 and 0 < x < self.max_x: return True
            if netname.startswith("logic_op_tnl_"):
                if x == self.max_x and 0 < y < self.max_y-1: return True
                if y == 0 and 1 < x < self.max_x: return True
            if netname.startswith("logic_op_tnr_"):
                if x == 0 and 0 < y < self.max_y-1: return True
                if y == 0 and 0 < x < self.max_x-1: return True

            if netname.startswith("logic_op_lft_"):
                if x == self.max_x: return True
            if netname.startswith("logic_op_rgt_"):
                if x == 0: return True

            return False
            
        if not 0 <= x <= self.max_x: return False
        if not 0 <= y <= self.max_y: return False
        return pos_has_net(self.tile_pos(x, y), netname)

    def tile_follow_net(self, x, y, direction, netname):
        if x == 1 and y not in (0, self.max_y) and direction == 'l': return pos_follow_net("x", "L", netname)
        if y == 1 and x not in (0, self.max_x) and direction == 'b': return pos_follow_net("x", "B", netname)
        if x == self.max_x-1 and y not in (0, self.max_y) and direction == 'r': return pos_follow_net("x", "R", netname)
        if y == self.max_y-1 and x not in (0, self.max_x) and direction == 't': return pos_follow_net("x", "T", netname)
        return pos_follow_net(self.tile_pos(x, y), direction, netname)

    def follow_funcnet(self, x, y, func):
        neighbours = set()
        def do_direction(name, nx, ny):
            if 0 < nx < self.max_x and 0 < ny < self.max_y:
                neighbours.add((nx, ny, "neigh_op_%s_%d" % (name, func)))
            if nx in (0, self.max_x) and 0 < ny < self.max_y and nx != x:
                neighbours.add((nx, ny, "logic_op_%s_%d" % (name, func)))
            if ny in (0, self.max_y) and 0 < nx < self.max_x and ny != y:
                neighbours.add((nx, ny, "logic_op_%s_%d" % (name, func)))
        do_direction("bot", x,   y+1)
        do_direction("bnl", x+1, y+1)
        do_direction("bnr", x-1, y+1)
        do_direction("top", x,   y-1)
        do_direction("tnl", x+1, y-1)
        do_direction("tnr", x-1, y-1)
        do_direction("lft", x+1, y  )
        do_direction("rgt", x-1, y  )
        return neighbours

    def lookup_funcnet(self, nx, ny, x, y, func):
        npos = self.tile_pos(nx, ny)
        pos = self.tile_pos(x, y)

        if npos is not None and pos is not None:
            if npos == "x":
                if (nx, ny) in self.logic_tiles:
                    return (nx, ny, "lutff_%d/out" % func)
                if (nx, ny) in self.ramb_tiles:
                    if self.device == "1k":
                        return (nx, ny, "ram/RDATA_%d" % func)
                    elif self.device == "8k":
                        return (nx, ny, "ram/RDATA_%d" % (15-func))
                    else:
                        assert False
                if (nx, ny) in self.ramt_tiles:
                    if self.device == "1k":
                        return (nx, ny, "ram/RDATA_%d" % (8+func))
                    elif self.device == "8k":
                        return (nx, ny, "ram/RDATA_%d" % (7-func))
                    else:
                        assert False

            elif pos == "x" and npos in ("l", "r", "t", "b"):
                if func in (0, 4): return (nx, ny, "io_0/D_IN_0")
                if func in (1, 5): return (nx, ny, "io_0/D_IN_1")
                if func in (2, 6): return (nx, ny, "io_1/D_IN_0")
                if func in (3, 7): return (nx, ny, "io_1/D_IN_1")

        return None

    def rlookup_funcnet(self, x, y, netname):
        funcnets = set()

        if netname == "io_0/D_IN_0":
            for net in self.follow_funcnet(x, y, 0) | self.follow_funcnet(x, y, 4):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_0/D_IN_1":
            for net in self.follow_funcnet(x, y, 1) | self.follow_funcnet(x, y, 5):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_1/D_IN_0":
            for net in self.follow_funcnet(x, y, 2) | self.follow_funcnet(x, y, 6):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_1/D_IN_1":
            for net in self.follow_funcnet(x, y, 3) | self.follow_funcnet(x, y, 7):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        match = re.match(r"lutff_(\d+)/out", netname)
        if match:
            funcnets |= self.follow_funcnet(x, y, int(match.group(1)))

        match = re.match(r"ram/RDATA_(\d+)", netname)
        if match:
            if self.device == "1k":
                funcnets |= self.follow_funcnet(x, y, int(match.group(1)) % 8)
            elif self.device == "8k":
                funcnets |= self.follow_funcnet(x, y, 7 - int(match.group(1)) % 8)
            else:
                assert False

        return funcnets

    def follow_net(self, netspec):
        x, y, netname = netspec
        neighbours = self.rlookup_funcnet(x, y, netname)

        if netname == "carry_in" and y > 1:
            neighbours.add((x, y-1, "lutff_7/cout"))

        if netname == "lutff_7/cout" and y+1 < self.max_y:
            neighbours.add((x, y+1, "carry_in"))

        if netname.startswith("glb_netwk_"):
            for nx in range(self.max_x+1):
                for ny in range(self.max_y+1):
                    if self.tile_pos(nx, ny) is not None:
                        neighbours.add((nx, ny, netname))

        match = re.match(r"sp4_r_v_b_(\d+)", netname)
        if match and 0 < x < self.max_x-1:
            neighbours.add((x+1, y, sp4v_normalize("sp4_v_b_" + match.group(1))))

        match = re.match(r"sp4_v_[bt]_(\d+)", netname)
        if match and 1 < x < self.max_x:
            n = sp4v_normalize(netname, "b")
            if n is not None:
                n = n.replace("sp4_", "sp4_r_")
                neighbours.add((x-1, y, n))

        match = re.match(r"(logic|neigh)_op_(...)_(\d+)", netname)
        if match:
            if match.group(2) == "bot": nx, ny = (x,   y-1)
            if match.group(2) == "bnl": nx, ny = (x-1, y-1)
            if match.group(2) == "bnr": nx, ny = (x+1, y-1)
            if match.group(2) == "top": nx, ny = (x,   y+1)
            if match.group(2) == "tnl": nx, ny = (x-1, y+1)
            if match.group(2) == "tnr": nx, ny = (x+1, y+1)
            if match.group(2) == "lft": nx, ny = (x-1, y  )
            if match.group(2) == "rgt": nx, ny = (x+1, y  )
            n = self.lookup_funcnet(nx, ny, x, y, int(match.group(3)))
            if n is not None:
                neighbours.add(n)

        for direction in ["l", "r", "t", "b"]:
            n = self.tile_follow_net(x, y, direction, netname)
            if n is not None:
                if direction == "l": s = (x-1, y, n)
                if direction == "r": s = (x+1, y, n)
                if direction == "t": s = (x, y+1, n)
                if direction == "b": s = (x, y-1, n)

                if s[0] in (0, self.max_x) and s[1] in (0, self.max_y):
                    if re.match("span4_(vert|horz)_[lrtb]_\d+$", n):
                        vert_net = n.replace("_l_", "_t_").replace("_r_", "_b_").replace("_horz_", "_vert_")
                        horz_net = n.replace("_t_", "_l_").replace("_b_", "_r_").replace("_vert_", "_horz_")

                        if s[0] == 0 and s[1] == 0:
                            if direction == "l": s = (0, 1, vert_net)
                            if direction == "b": s = (1, 0, horz_net)

                        if s[0] == self.max_x and s[1] == self.max_y:
                            if direction == "r": s = (self.max_x, self.max_y-1, vert_net)
                            if direction == "t": s = (self.max_x-1, self.max_y, horz_net)

                        vert_net = netname.replace("_l_", "_t_").replace("_r_", "_b_").replace("_horz_", "_vert_")
                        horz_net = netname.replace("_t_", "_l_").replace("_b_", "_r_").replace("_vert_", "_horz_")

                        if s[0] == 0 and s[1] == self.max_y:
                            if direction == "l": s = (0, self.max_y-1, vert_net)
                            if direction == "t": s = (1, self.max_y, horz_net)

                        if s[0] == self.max_x and s[1] == 0:
                            if direction == "r": s = (self.max_x, 1, vert_net)
                            if direction == "b": s = (self.max_x-1, 0, horz_net)

                if self.tile_has_net(s[0], s[1], s[2]):
                    neighbours.add((s[0], s[1], s[2]))
        return neighbours

    def group_segments(self, all_from_tiles=set(), extra_connections=list(), extra_segments=list(), connect_gb=True):
        seed_segments = set()
        seen_segments = set()
        connected_segments = dict()
        grouped_segments = set()

        for seg in extra_segments:
            seed_segments.add(seg)

        for conn in extra_connections:
            s1, s2 = conn
            connected_segments.setdefault(s1, set()).add(s2)
            connected_segments.setdefault(s2, set()).add(s1)
            seed_segments.add(s1)
            seed_segments.add(s2)

        for idx, tile in self.io_tiles.items():
            tc = tileconfig(tile)
            pintypes = [ list("000000"), list("000000") ]
            for entry in self.tile_db(idx[0], idx[1]):
                if entry[1].startswith("IOB_") and entry[2].startswith("PINTYPE_") and tc.match(entry[0]):
                    pintypes[int(entry[1][-1])][int(entry[2][-1])] = "1"
            if "".join(pintypes[0][2:6]) != "0000":
                seed_segments.add((idx[0], idx[1], "io_0/D_OUT_0"))
            if "".join(pintypes[1][2:6]) != "0000":
                seed_segments.add((idx[0], idx[1], "io_1/D_OUT_0"))

        def add_seed_segments(idx, tile, db):
            tc = tileconfig(tile)
            for entry in db:
                if entry[1] in ("routing", "buffer"):
                    config_match = tc.match(entry[0])
                    if idx in all_from_tiles or config_match:
                        if not self.tile_has_net(idx[0], idx[1], entry[2]): continue
                        if not self.tile_has_net(idx[0], idx[1], entry[3]): continue
                        s1 = (idx[0], idx[1], entry[2])
                        s2 = (idx[0], idx[1], entry[3])
                        if config_match:
                            connected_segments.setdefault(s1, set()).add(s2)
                            connected_segments.setdefault(s2, set()).add(s1)
                        seed_segments.add(s1)
                        seed_segments.add(s2)

        for idx, tile in self.io_tiles.items():
            add_seed_segments(idx, tile, self.tile_db(idx[0], idx[1]))

        for idx, tile in self.logic_tiles.items():
            if idx in all_from_tiles:
                seed_segments.add((idx[0], idx[1], "lutff_7/cout"))
            if self.device == "1k":
                add_seed_segments(idx, tile, logictile_db)
            elif self.device == "8k":
                add_seed_segments(idx, tile, logictile_8k_db)
            else:
                assert False

        for idx, tile in self.ramb_tiles.items():
            if self.device == "1k":
                add_seed_segments(idx, tile, rambtile_db)
            elif self.device == "8k":
                add_seed_segments(idx, tile, rambtile_8k_db)
            else:
                assert False

        for idx, tile in self.ramt_tiles.items():
            if self.device == "1k":
                add_seed_segments(idx, tile, ramttile_db)
            elif self.device == "8k":
                add_seed_segments(idx, tile, ramttile_8k_db)
            else:
                assert False

        for padin, pio in enumerate(self.padin_pio_db()):
            s1 = (pio[0], pio[1], "padin_%d" % pio[2])
            s2 = (pio[0], pio[1], "glb_netwk_%d" % padin)
            if s1 in seed_segments or (pio[0], pio[1]) in all_from_tiles:
                connected_segments.setdefault(s1, set()).add(s2)
                connected_segments.setdefault(s2, set()).add(s1)
                seed_segments.add(s1)
                seed_segments.add(s2)

        for entry in self.iolatch_db():
            if entry[0] == 0 or entry[0] == self.max_x:
                iocells = [(entry[0], i) for i in range(1, self.max_y)]
            if entry[1] == 0 or entry[1] == self.max_y:
                iocells = [(i, entry[1]) for i in range(1, self.max_x)]
            for cell in iocells:
                s1 = (entry[0], entry[1], "fabout")
                s2 = (cell[0], cell[1], "io_global/latch")
                if s1 in seed_segments or s2 in seed_segments or \
                        (entry[0], entry[1]) in all_from_tiles or (cell[0], cell[1]) in all_from_tiles:
                    connected_segments.setdefault(s1, set()).add(s2)
                    connected_segments.setdefault(s2, set()).add(s1)
                    seed_segments.add(s1)
                    seed_segments.add(s2)

        if connect_gb:
            for entry in self.gbufin_db():
                s1 = (entry[0], entry[1], "fabout")
                s2 = (entry[0], entry[1], "glb_netwk_%d" % entry[2])
                if s1 in seed_segments or (pio[0], pio[1]) in all_from_tiles:
                    connected_segments.setdefault(s1, set()).add(s2)
                    connected_segments.setdefault(s2, set()).add(s1)
                    seed_segments.add(s1)
                    seed_segments.add(s2)

        while seed_segments:
            queue = set()
            segments = set()
            queue.add(seed_segments.pop())
            while queue:
                for s in self.expand_net(queue.pop()):
                    if s not in segments:
                        segments.add(s)
                        assert s not in seen_segments
                        seen_segments.add(s)
                        seed_segments.discard(s)
                        if s in connected_segments:
                            for cs in connected_segments[s]:
                                if not cs in segments:
                                    queue.add(cs)
            for s in segments:
                assert s not in seed_segments
            grouped_segments.add(tuple(sorted(segments)))

        return grouped_segments

    def expand_net(self, netspec):
        queue = set()
        segments = set()
        queue.add(netspec)
        while queue:
            n = queue.pop()
            segments.add(n)
            for k in self.follow_net(n):
                if k not in segments:
                    queue.add(k)
        return segments

    def read_file(self, filename):
        self.clear()
        current_data = None
        expected_data_lines = 0
        with open(filename, "r") as f:
            for linenum, linetext in enumerate(f):
                # print("DEBUG: input line %d: %s" % (linenum, linetext.strip()))
                line = linetext.strip().split()
                if len(line) == 0:
                    assert expected_data_lines == 0
                    continue
                if line[0][0] != ".":
                    if expected_data_lines == -1:
                        continue
                    if line[0][0] not in "0123456789abcdef":
                        print("Warning: ignoring data block in line %d: %s" % (linenum, linetext.strip()))
                        expected_data_lines = 0
                        continue
                    assert expected_data_lines != 0
                    current_data.append(line[0])
                    expected_data_lines -= 1
                    continue
                assert expected_data_lines <= 0
                if line[0] in (".io_tile", ".logic_tile", ".ramb_tile", ".ramt_tile", ".ram_data"):
                    current_data = list()
                    expected_data_lines = 16
                    self.max_x = max(self.max_x, int(line[1]))
                    self.max_y = max(self.max_y, int(line[2]))
                if line[0] == ".io_tile":
                    self.io_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".logic_tile":
                    self.logic_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ramb_tile":
                    self.ramb_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ramt_tile":
                    self.ramt_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ram_data":
                    self.ram_data[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".extra_bit":
                    self.extra_bits.add((int(line[1]), int(line[2]), int(line[3])))
                    continue
                if line[0] == ".device":
                    assert line[1] in ["1k", "8k"]
                    self.device = line[1]
                    continue
                if line[0] == ".sym":
                    self.symbols.setdefault(int(line[1]), set()).add(line[2])
                    continue
                if line[0] == ".comment":
                    expected_data_lines = -1
                    continue
                print("Warning: ignoring line %d: %s" % (linenum, linetext.strip()))
                expected_data_lines = -1

    def write_file(self, filename):
        with open(filename, "w") as f:
            print(".device %s" % self.device, file=f)
            for y in range(self.max_y+1):
                for x in range(self.max_x+1):
                    if self.tile_pos(x, y) is not None:
                        print(".%s_tile %d %d" % (self.tile_type(x, y).lower(), x, y), file=f)
                        for line in self.tile(x, y):
                            print(line, file=f)
            for x, y in sorted(self.ram_data):
                print(".ram_data %d %d" % (x, y), file=f)
                for line in self.ram_data[(x, y)]:
                    print(line, file=f)

class tileconfig:
    def __init__(self, tile):
        self.bits = set()
        for k, line in enumerate(tile):
            for i in range(len(line)):
                if line[i] == "1":
                    self.bits.add("B%d[%d]" % (k, i))
                else:
                    self.bits.add("!B%d[%d]" % (k, i))
    def match(self, pattern):
        for bit in pattern:
            if not bit in self.bits:
                return False
        return True

if False:
    ## Lattice span net name normalization

    valid_sp4_h_l = set([1, 2, 4, 5, 7, 9, 10, 11, 15, 16, 17, 21, 24, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47])
    valid_sp4_h_r = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 19, 21, 24, 25, 27, 30, 31, 33, 34, 35, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46])

    valid_sp4_v_t = set([1, 3, 5, 9, 12, 14, 16, 17, 18, 21, 22, 23, 26, 28, 29, 30, 32, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47])
    valid_sp4_v_b = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 18, 19, 21, 22, 23, 24, 26, 30, 33, 36, 37, 38, 42, 46, 47])

    valid_sp12_h_l = set([3, 4, 5, 12, 14, 16, 17, 18, 21, 22, 23])
    valid_sp12_h_r = set([0, 1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 16, 20, 23])

    valid_sp12_v_t = set([0, 1, 2, 3, 6, 9, 10, 12, 14, 21, 22, 23])
    valid_sp12_v_b = set([0, 1, 6, 7, 8, 11, 12, 14, 16, 18, 19, 20, 21, 23])

else:
    ## IceStorm span net name normalization

    valid_sp4_h_l = set(range(36, 48))
    valid_sp4_h_r = set(range(48))

    valid_sp4_v_t = set(range(36, 48))
    valid_sp4_v_b = set(range(48))

    valid_sp12_h_l = set(range(22, 24))
    valid_sp12_h_r = set(range(24))

    valid_sp12_v_t = set(range(22, 24))
    valid_sp12_v_b = set(range(24))

def sp4h_normalize(netname, edge=""):
    m = re.match("sp4_h_([lr])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "r" and (edge == "l" or (edge == "" and cur_index not in valid_sp4_h_r)):
        if cur_index < 12:
            return None
        return "sp4_h_l_%d" % ((cur_index-12)^1)

    if cur_edge == "l" and (edge == "r" or (edge == "" and cur_index not in valid_sp4_h_l)):
        if cur_index >= 36:
            return None
        return "sp4_h_r_%d" % ((cur_index+12)^1)

    return netname

def sp4v_normalize(netname, edge=""):
    m = re.match("sp4_v_([bt])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "b" and (edge == "t" or (edge == "" and cur_index not in valid_sp4_v_b)):
        if cur_index < 12:
            return None
        return "sp4_v_t_%d" % ((cur_index-12)^1)

    if cur_edge == "t" and (edge == "b" or (edge == "" and cur_index not in valid_sp4_v_t)):
        if cur_index >= 36:
            return None
        return "sp4_v_b_%d" % ((cur_index+12)^1)

    return netname

def sp12h_normalize(netname, edge=""):
    m = re.match("sp12_h_([lr])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "r" and (edge == "l" or (edge == "" and cur_index not in valid_sp12_h_r)):
        if cur_index < 2:
            return None
        return "sp12_h_l_%d" % ((cur_index-2)^1)

    if cur_edge == "l" and (edge == "r" or (edge == "" and cur_index not in valid_sp12_h_l)):
        if cur_index >= 22:
            return None
        return "sp12_h_r_%d" % ((cur_index+2)^1)

    return netname

def sp12v_normalize(netname, edge=""):
    m = re.match("sp12_v_([bt])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "b" and (edge == "t" or (edge == "" and cur_index not in valid_sp12_v_b)):
        if cur_index < 2:
            return None
        return "sp12_v_t_%d" % ((cur_index-2)^1)

    if cur_edge == "t" and (edge == "b" or (edge == "" and cur_index not in valid_sp12_v_t)):
        if cur_index >= 22:
            return None
        return "sp12_v_b_%d" % ((cur_index+2)^1)

    return netname

def netname_normalize(netname, edge="", ramb=False, ramt=False, ramb_8k=False, ramt_8k=False):
    if netname.startswith("sp4_v_"): return sp4v_normalize(netname, edge)
    if netname.startswith("sp4_h_"): return sp4h_normalize(netname, edge)
    if netname.startswith("sp12_v_"): return sp12v_normalize(netname, edge)
    if netname.startswith("sp12_h_"): return sp12h_normalize(netname, edge)
    if netname.startswith("input_2_"): netname = netname.replace("input_2_", "wire_logic_cluster/lc_") + "/in_2"
    netname = netname.replace("lc_trk_", "local_")
    netname = netname.replace("lc_", "lutff_")
    netname = netname.replace("wire_logic_cluster/", "")
    netname = netname.replace("wire_io_cluster/", "")
    netname = netname.replace("wire_bram/", "")
    if (ramb or ramt or ramb_8k or ramt_8k) and netname.startswith("input"):
        match = re.match(r"input(\d)_(\d)", netname)
        idx1, idx2 = (int(match.group(1)), int(match.group(2)))
        if ramb: netname="ram/WADDR_%d" % (idx1*4 + idx2)
        if ramt: netname="ram/RADDR_%d" % (idx1*4 + idx2)
        if ramb_8k: netname="ram/RADDR_%d" % ([7, 6, 5, 4, 3, 2, 1, 0, -1, -1, -1, -1, -1, 10, 9, 8][idx1*4 + idx2])
        if ramt_8k: netname="ram/WADDR_%d" % ([7, 6, 5, 4, 3, 2, 1, 0, -1, -1, -1, -1, -1, 10, 9, 8][idx1*4 + idx2])
    match = re.match(r"(...)_op_(.*)", netname)
    if match:
        netname = "neigh_op_%s_%s" % (match.group(1), match.group(2))
    if re.match(r"lutff_7/(cen|clk|s_r)", netname):
        netname = netname.replace("lutff_7/", "lutff_global/")
    if re.match(r"io_1/(cen|inclk|outclk)", netname):
        netname = netname.replace("io_1/", "io_global/")
    if netname == "carry_in_mux/cout":
        return "carry_in_mux"
    return netname

def pos_has_net(pos, netname):
    if pos in ("l", "r"):
        if re.search(r"_vert_\d+$", netname): return False
        if re.search(r"_horz_[rl]_\d+$", netname): return False
    if pos in ("t", "b"):
        if re.search(r"_horz_\d+$", netname): return False
        if re.search(r"_vert_[bt]_\d+$", netname): return False
    return True

def pos_follow_net(pos, direction, netname):
    if pos == "x":
            m = re.match("sp4_h_[lr]_(\d+)$", netname)
            if m and direction in ("l", "L"):
                n = sp4h_normalize(netname, "l")
                if n is not None:
                    if direction == "l":
                        n = re.sub("_l_", "_r_", n)
                        n = sp4h_normalize(n)
                    else:
                        n = re.sub("_l_", "_", n)
                        n = re.sub("sp4_h_", "span4_horz_", n)
                    return n
            if m and direction in ("r", "R"):
                n = sp4h_normalize(netname, "r")
                if n is not None:
                    if direction == "r":
                        n = re.sub("_r_", "_l_", n)
                        n = sp4h_normalize(n)
                    else:
                        n = re.sub("_r_", "_", n)
                        n = re.sub("sp4_h_", "span4_horz_", n)
                    return n

            m = re.match("sp4_v_[tb]_(\d+)$", netname)
            if m and direction in ("t", "T"):
                n = sp4v_normalize(netname, "t")
                if n is not None:
                    if direction == "t":
                        n = re.sub("_t_", "_b_", n)
                        n = sp4v_normalize(n)
                    else:
                        n = re.sub("_t_", "_", n)
                        n = re.sub("sp4_v_", "span4_vert_", n)
                    return n
            if m and direction in ("b", "B"):
                n = sp4v_normalize(netname, "b")
                if n is not None:
                    if direction == "b":
                        n = re.sub("_b_", "_t_", n)
                        n = sp4v_normalize(n)
                    else:
                        n = re.sub("_b_", "_", n)
                        n = re.sub("sp4_v_", "span4_vert_", n)
                    return n

            m = re.match("sp12_h_[lr]_(\d+)$", netname)
            if m and direction in ("l", "L"):
                n = sp12h_normalize(netname, "l")
                if n is not None:
                    if direction == "l":
                        n = re.sub("_l_", "_r_", n)
                        n = sp12h_normalize(n)
                    else:
                        n = re.sub("_l_", "_", n)
                        n = re.sub("sp12_h_", "span12_horz_", n)
                    return n
            if m and direction in ("r", "R"):
                n = sp12h_normalize(netname, "r")
                if n is not None:
                    if direction == "r":
                        n = re.sub("_r_", "_l_", n)
                        n = sp12h_normalize(n)
                    else:
                        n = re.sub("_r_", "_", n)
                        n = re.sub("sp12_h_", "span12_horz_", n)
                    return n

            m = re.match("sp12_v_[tb]_(\d+)$", netname)
            if m and direction in ("t", "T"):
                n = sp12v_normalize(netname, "t")
                if n is not None:
                    if direction == "t":
                        n = re.sub("_t_", "_b_", n)
                        n = sp12v_normalize(n)
                    else:
                        n = re.sub("_t_", "_", n)
                        n = re.sub("sp12_v_", "span12_vert_", n)
                    return n
            if m and direction in ("b", "B"):
                n = sp12v_normalize(netname, "b")
                if n is not None:
                    if direction == "b":
                        n = re.sub("_b_", "_t_", n)
                        n = sp12v_normalize(n)
                    else:
                        n = re.sub("_b_", "_", n)
                        n = re.sub("sp12_v_", "span12_vert_", n)
                    return n

    if pos in ("l", "r" ):
        m = re.match("span4_vert_([bt])_(\d+)$", netname)
        if m:
            case, idx = direction + m.group(1), int(m.group(2))
            if case == "tt":
                return "span4_vert_b_%d" % idx
            if case == "tb" and idx >= 4:
                return "span4_vert_b_%d" % (idx-4)
            if case == "bb" and idx < 12:
                return "span4_vert_b_%d" % (idx+4)
            if case == "bb" and idx >= 12:
                return "span4_vert_t_%d" % idx

    if pos in ("t", "b" ):
        m = re.match("span4_horz_([rl])_(\d+)$", netname)
        if m:
            case, idx = direction + m.group(1), int(m.group(2))
            if case == "ll":
                return "span4_horz_r_%d" % idx
            if case == "lr" and idx >= 4:
                return "span4_horz_r_%d" % (idx-4)
            if case == "rr" and idx < 12:
                return "span4_horz_r_%d" % (idx+4)
            if case == "rr" and idx >= 12:
                return "span4_horz_l_%d" % idx

    if pos == "l" and direction == "r":
            m = re.match("span4_horz_(\d+)$", netname)
            if m: return sp4h_normalize("sp4_h_l_%s" % m.group(1))
            m = re.match("span12_horz_(\d+)$", netname)
            if m: return sp12h_normalize("sp12_h_l_%s" % m.group(1))

    if pos == "r" and direction == "l":
            m = re.match("span4_horz_(\d+)$", netname)
            if m: return sp4h_normalize("sp4_h_r_%s" % m.group(1))
            m = re.match("span12_horz_(\d+)$", netname)
            if m: return sp12h_normalize("sp12_h_r_%s" % m.group(1))

    if pos == "t" and direction == "b":
            m = re.match("span4_vert_(\d+)$", netname)
            if m: return sp4v_normalize("sp4_v_t_%s" % m.group(1))
            m = re.match("span12_vert_(\d+)$", netname)
            if m: return sp12v_normalize("sp12_v_t_%s" % m.group(1))

    if pos == "b" and direction == "t":
            m = re.match("span4_vert_(\d+)$", netname)
            if m: return sp4v_normalize("sp4_v_b_%s" % m.group(1))
            m = re.match("span12_vert_(\d+)$", netname)
            if m: return sp12v_normalize("sp12_v_b_%s" % m.group(1))

    return None

def get_lutff_bits(tile, index):
    bits = list("--------------------")
    for k, line in enumerate(tile):
        for i in range(36, 46):
            lutff_idx = k // 2
            lutff_bitnum = (i-36) + 10*(k%2)
            if lutff_idx == index:
                bits[lutff_bitnum] = line[i];
    return bits

def get_lutff_lut_bits(tile, index):
    lutff_bits = get_lutff_bits(tile, index)
    return [lutff_bits[i] for i in [4, 14, 15, 5, 6, 16, 17, 7, 3, 13, 12, 2, 1, 11, 10, 0]]

def get_lutff_seq_bits(tile, index):
    lutff_bits = get_lutff_bits(tile, index)
    return [lutff_bits[i] for i in [8, 9, 18, 19]]

def get_carry_cascade_bit(tile):
    return tile[1][49]

def get_carry_bit(tile):
    return tile[1][50]

def get_negclk_bit(tile):
    return tile[0][0]

def cmp_netnames(a, b):
    a = re.sub(r"\d+", lambda m: "%09d" % int(m.group(0)), a)
    b = re.sub(r"\d+", lambda m: "%09d" % int(m.group(0)), b)
    return cmp(a, b)

def run_checks_neigh():
    print("Running consistency checks on neighbour finder..")
    ic = iceconfig()
    ic.setup_empty_1k()
    # ic.setup_empty_8k()

    all_segments = set()

    def add_segments(idx, db):
        for entry in db:
            if entry[1] in ("routing", "buffer"):
                if not ic.tile_has_net(idx[0], idx[1], entry[2]): continue
                if not ic.tile_has_net(idx[0], idx[1], entry[3]): continue
                all_segments.add((idx[0], idx[1], entry[2]))
                all_segments.add((idx[0], idx[1], entry[3]))

    for x in range(ic.max_x+1):
        for y in range(ic.max_x+1):
            if x in (0, ic.max_x) and y in (0, ic.max_y):
                continue
            add_segments((x, y), ic.tile_db(x, y))
            if (x, y) in ic.logic_tiles:
                all_segments.add((x, y, "lutff_7/cout"))

    for s1 in all_segments:
        # if s1[1] > 4: continue
        for s2 in ic.follow_net(s1):
            if s1 not in ic.follow_net(s2):
                print("ERROR: %s -> %s, but not vice versa!" % (s1, s2))
                print("Neighbours of %s:" % (s1,))
                for s in ic.follow_net(s1):
                    print("  ", s)
                print("Neighbours of %s:" % (s2,))
                for s in ic.follow_net(s2):
                    print("  ", s)
                print()

def run_checks():
    run_checks_neigh()

def parse_db(text, grep_8k=False):
    db = list()
    for line in text.split("\n"):
        line_1k = line.replace("1k_glb_netwk_", "glb_netwk_")
        line_8k = line.replace("8k_glb_netwk_", "glb_netwk_")
        if line_1k != line:
            if grep_8k:
                continue
            line = line_1k
        elif line_8k != line:
            if not grep_8k:
                continue
            line = line_8k
        line = line.split("\t")
        if len(line) == 0 or line[0] == "":
            continue
        line[0] = line[0].split(",")
        db.append(line)
    return db

extra_bits_db = {
    "1k": {
        (0, 330, 142): ("padin_glb_netwk", "0"),
        (0, 331, 142): ("padin_glb_netwk", "1"),
        (1, 330, 143): ("padin_glb_netwk", "2"),
        (1, 331, 143): ("padin_glb_netwk", "3"),
        (1, 330, 142): ("padin_glb_netwk", "4"),
        (1, 331, 142): ("padin_glb_netwk", "5"),
        (0, 330, 143): ("padin_glb_netwk", "6"),
        (0, 331, 143): ("padin_glb_netwk", "7"),
    },
    "8k": {
        (0, 870, 270): ("padin_glb_netwk", "0"),
        (0, 871, 270): ("padin_glb_netwk", "1"),
        (1, 870, 271): ("padin_glb_netwk", "2"),
        (1, 871, 271): ("padin_glb_netwk", "3"),
        (1, 870, 270): ("padin_glb_netwk", "4"),
        (1, 871, 270): ("padin_glb_netwk", "5"),
        (0, 870, 271): ("padin_glb_netwk", "6"),
        (0, 871, 271): ("padin_glb_netwk", "7"),
    }
}

gbufin_db = {
    "1k": [
        (13,  8,  7),
        ( 0,  8,  6),
        ( 7, 17,  1),
        ( 7,  0,  0),
        ( 0,  9,  3),
        (13,  9,  2),
        ( 6,  0,  5),
        ( 6, 17,  4),
    ],
    "8k": [
        (33, 16,  7),
        ( 0, 16,  6),
        (17, 33,  1),
        (17,  0,  0),
        ( 0, 17,  3),
        (33, 17,  2),
        (16,  0,  5),
        (16, 33,  4),
    ]
}

iolatch_db = {
    "1k": [
        ( 0,  7),
        (13, 10),
        ( 5,  0),
        ( 8, 17),
    ],
    "8k": [
        ( 0, 15),
        (33, 18),
        (18,  0),
        (15, 33),
    ],
}

warmbootinfo_db = {
    "1k": {
        "BOOT": ( 12, 0, "fabout" ),
        "S0":   ( 13, 1, "fabout" ),
        "S1":   ( 13, 2, "fabout" ),
    },
    "8k": {
        "BOOT": ( 31, 0, "fabout" ),
        "S0":   ( 33, 1, "fabout" ),
        "S1":   ( 33, 2, "fabout" ),
    }
}

pllinfo_db = {
    "1k": {
        "LOC" : (6, 0),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 0,  3, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 0,  5, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 0,  5, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 0,  5, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 0,  2, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 0,  3, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 0,  4, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 0,  4, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 0,  3, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 0,  3, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 0,  3, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 0,  3, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 0,  3, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 0,  3, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 0,  4, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 0,  4, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 0,  4, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 0,  4, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 0,  4, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 0,  4, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 0,  4, "PLLCONFIG_8"),
        "DIVR_0":               ( 0,  1, "PLLCONFIG_1"),
        "DIVR_1":               ( 0,  1, "PLLCONFIG_2"),
        "DIVR_2":               ( 0,  1, "PLLCONFIG_3"),
        "DIVR_3":               ( 0,  1, "PLLCONFIG_4"),
        "DIVF_0":               ( 0,  1, "PLLCONFIG_5"),
        "DIVF_1":               ( 0,  1, "PLLCONFIG_6"),
        "DIVF_2":               ( 0,  1, "PLLCONFIG_7"),
        "DIVF_3":               ( 0,  1, "PLLCONFIG_8"),
        "DIVF_4":               ( 0,  1, "PLLCONFIG_9"),
        "DIVF_5":               ( 0,  2, "PLLCONFIG_1"),
        "DIVF_6":               ( 0,  2, "PLLCONFIG_2"),
        "DIVQ_0":               ( 0,  2, "PLLCONFIG_3"),
        "DIVQ_1":               ( 0,  2, "PLLCONFIG_4"),
        "DIVQ_2":               ( 0,  2, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 0,  2, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 0,  2, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 0,  2, "PLLCONFIG_8"),
        "TEST_MODE":            ( 0,  3, "PLLCONFIG_8"),

        # PLL Ports
        "PLLOUT_A":             ( 6,  0, 1),
        "PLLOUT_B":             ( 7,  0, 0),
        "REFERENCECLK":         ( 0,  1, "fabout"),
        "EXTFEEDBACK":          ( 0,  2, "fabout"),
        "DYNAMICDELAY_0":       ( 0,  4, "fabout"),
        "DYNAMICDELAY_1":       ( 0,  5, "fabout"),
        "DYNAMICDELAY_2":       ( 0,  6, "fabout"),
        "DYNAMICDELAY_3":       ( 0, 10, "fabout"),
        "DYNAMICDELAY_4":       ( 0, 11, "fabout"),
        "DYNAMICDELAY_5":       ( 0, 12, "fabout"),
        "DYNAMICDELAY_6":       ( 0, 13, "fabout"),
        "DYNAMICDELAY_7":       ( 0, 14, "fabout"),
        "LOCK":                 ( 1,  1, "neigh_op_bnl_1"),
        "BYPASS":               ( 1,  0, "fabout"),
        "RESETB":               ( 2,  0, "fabout"),
        "LATCHINPUTVALUE":      ( 5,  0, "fabout"),
        "SDO":                  (12,  1, "neigh_op_bnr_3"),
        "SDI":                  ( 4,  0, "fabout"),
        "SCLK":                 ( 3,  0, "fabout"),
    },
    "8k_0": {
        "LOC" : (16, 0),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 16, 0, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 18, 0, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 18, 0, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 18, 0, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 15, 0, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 16, 0, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 17, 0, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 17, 0, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 16, 0, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 16, 0, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 16, 0, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 16, 0, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 16, 0, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 16, 0, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 17, 0, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 17, 0, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 17, 0, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 17, 0, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 17, 0, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 17, 0, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 17, 0, "PLLCONFIG_8"),
        "DIVR_0":               ( 14, 0, "PLLCONFIG_1"),
        "DIVR_1":               ( 14, 0, "PLLCONFIG_2"),
        "DIVR_2":               ( 14, 0, "PLLCONFIG_3"),
        "DIVR_3":               ( 14, 0, "PLLCONFIG_4"),
        "DIVF_0":               ( 14, 0, "PLLCONFIG_5"),
        "DIVF_1":               ( 14, 0, "PLLCONFIG_6"),
        "DIVF_2":               ( 14, 0, "PLLCONFIG_7"),
        "DIVF_3":               ( 14, 0, "PLLCONFIG_8"),
        "DIVF_4":               ( 14, 0, "PLLCONFIG_9"),
        "DIVF_5":               ( 15, 0, "PLLCONFIG_1"),
        "DIVF_6":               ( 15, 0, "PLLCONFIG_2"),
        "DIVQ_0":               ( 15, 0, "PLLCONFIG_3"),
        "DIVQ_1":               ( 15, 0, "PLLCONFIG_4"),
        "DIVQ_2":               ( 15, 0, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 15, 0, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 15, 0, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 15, 0, "PLLCONFIG_8"),
        "TEST_MODE":            ( 16, 0, "PLLCONFIG_8"),

        # PLL Ports
        "PLLOUT_A":             ( 16, 0, 1),
        "PLLOUT_B":             ( 17, 0, 0),
        "REFERENCECLK":         ( 13, 0, "fabout"),
        "EXTFEEDBACK":          ( 14, 0, "fabout"),
        "DYNAMICDELAY_0":       (  5, 0, "fabout"),
        "DYNAMICDELAY_1":       (  6, 0, "fabout"),
        "DYNAMICDELAY_2":       (  7, 0, "fabout"),
        "DYNAMICDELAY_3":       (  8, 0, "fabout"),
        "DYNAMICDELAY_4":       (  9, 0, "fabout"),
        "DYNAMICDELAY_5":       ( 10, 0, "fabout"),
        "DYNAMICDELAY_6":       ( 11, 0, "fabout"),
        "DYNAMICDELAY_7":       ( 12, 0, "fabout"),
        "LOCK":                 (  1, 1, "neigh_op_bnl_1"),
        "BYPASS":               ( 19, 0, "fabout"),
        "RESETB":               ( 20, 0, "fabout"),
        "LATCHINPUTVALUE":      ( 15, 0, "fabout"),
        "SDO":                  ( 32, 1, "neigh_op_bnr_3"),
        "SDI":                  ( 22, 0, "fabout"),
        "SCLK":                 ( 21, 0, "fabout"),
    },
    "8k_1": {
        "LOC" : (16, 33),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 16, 33, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 18, 33, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 18, 33, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 18, 33, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 15, 33, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 16, 33, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 17, 33, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 17, 33, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 16, 33, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 16, 33, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 16, 33, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 16, 33, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 16, 33, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 16, 33, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 17, 33, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 17, 33, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 17, 33, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 17, 33, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 17, 33, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 17, 33, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 17, 33, "PLLCONFIG_8"),
        "DIVR_0":               ( 14, 33, "PLLCONFIG_1"),
        "DIVR_1":               ( 14, 33, "PLLCONFIG_2"),
        "DIVR_2":               ( 14, 33, "PLLCONFIG_3"),
        "DIVR_3":               ( 14, 33, "PLLCONFIG_4"),
        "DIVF_0":               ( 14, 33, "PLLCONFIG_5"),
        "DIVF_1":               ( 14, 33, "PLLCONFIG_6"),
        "DIVF_2":               ( 14, 33, "PLLCONFIG_7"),
        "DIVF_3":               ( 14, 33, "PLLCONFIG_8"),
        "DIVF_4":               ( 14, 33, "PLLCONFIG_9"),
        "DIVF_5":               ( 15, 33, "PLLCONFIG_1"),
        "DIVF_6":               ( 15, 33, "PLLCONFIG_2"),
        "DIVQ_0":               ( 15, 33, "PLLCONFIG_3"),
        "DIVQ_1":               ( 15, 33, "PLLCONFIG_4"),
        "DIVQ_2":               ( 15, 33, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 15, 33, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 15, 33, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 15, 33, "PLLCONFIG_8"),
        "TEST_MODE":            ( 16, 33, "PLLCONFIG_8"),

        # PLL Ports
        "PLLOUT_A":             ( 16, 33, 1),
        "PLLOUT_B":             ( 17, 33, 0),
        "REFERENCECLK":         ( 13, 33, "fabout"),
        "EXTFEEDBACK":          ( 14, 33, "fabout"),
        "DYNAMICDELAY_0":       (  5, 33, "fabout"),
        "DYNAMICDELAY_1":       (  6, 33, "fabout"),
        "DYNAMICDELAY_2":       (  7, 33, "fabout"),
        "DYNAMICDELAY_3":       (  8, 33, "fabout"),
        "DYNAMICDELAY_4":       (  9, 33, "fabout"),
        "DYNAMICDELAY_5":       ( 10, 33, "fabout"),
        "DYNAMICDELAY_6":       ( 11, 33, "fabout"),
        "DYNAMICDELAY_7":       ( 12, 33, "fabout"),
        "LOCK":                 (  1, 32, "neigh_op_tnl_1"),
        "BYPASS":               ( 19, 33, "fabout"),
        "RESETB":               ( 20, 33, "fabout"),
        "LATCHINPUTVALUE":      ( 15, 33, "fabout"),
        "SDO":                  ( 32, 32, "neigh_op_tnr_1"),
        "SDI":                  ( 22, 33, "fabout"),
        "SCLK":                 ( 21, 33, "fabout"),
    },
}

padin_pio_db = {
    "1k": [
        (13,  8, 1),  # glb_netwk_0
        ( 0,  8, 1),  # glb_netwk_1
        ( 7, 17, 0),  # glb_netwk_2
        ( 7,  0, 0),  # glb_netwk_3
        ( 0,  9, 0),  # glb_netwk_4
        (13,  9, 0),  # glb_netwk_5
        ( 6,  0, 1),  # glb_netwk_6
        ( 6, 17, 1),  # glb_netwk_7
    ],
    "8k": [
        (33, 16, 1),
        ( 0, 16, 1),
        (17, 33, 0),
        (17,  0, 0),
        ( 0, 17, 0),
        (33, 17, 0),
        (16,  0, 1),
        (16, 33, 1),
    ]
}

ieren_db = {
    "1k": [
        # IO-block (X, Y, Z) <-> IeRen-block (X, Y, Z)
        ( 0,  2, 0,  0,  2, 1),
        ( 0,  2, 1,  0,  2, 0),
        ( 0,  3, 0,  0,  3, 1),
        ( 0,  3, 1,  0,  3, 0),
        ( 0,  4, 0,  0,  4, 1),
        ( 0,  4, 1,  0,  4, 0),
        ( 0,  5, 0,  0,  5, 1),
        ( 0,  5, 1,  0,  5, 0),
        ( 0,  6, 0,  0,  6, 1),
        ( 0,  6, 1,  0,  6, 0),
        ( 0,  8, 0,  0,  8, 1),
        ( 0,  8, 1,  0,  8, 0),
        ( 0,  9, 0,  0,  9, 1),
        ( 0,  9, 1,  0,  9, 0),
        ( 0, 10, 0,  0, 10, 1),
        ( 0, 10, 1,  0, 10, 0),
        ( 0, 11, 0,  0, 11, 1),
        ( 0, 11, 1,  0, 11, 0),
        ( 0, 12, 0,  0, 12, 1),
        ( 0, 12, 1,  0, 12, 0),
        ( 0, 13, 0,  0, 13, 1),
        ( 0, 13, 1,  0, 13, 0),
        ( 0, 14, 0,  0, 14, 1),
        ( 0, 14, 1,  0, 14, 0),
        ( 1,  0, 0,  1,  0, 0),
        ( 1,  0, 1,  1,  0, 1),
        ( 1, 17, 0,  1, 17, 0),
        ( 1, 17, 1,  1, 17, 1),
        ( 2,  0, 0,  2,  0, 0),
        ( 2,  0, 1,  2,  0, 1),
        ( 2, 17, 0,  2, 17, 0),
        ( 2, 17, 1,  2, 17, 1),
        ( 3,  0, 0,  3,  0, 0),
        ( 3,  0, 1,  3,  0, 1),
        ( 3, 17, 0,  3, 17, 0),
        ( 3, 17, 1,  3, 17, 1),
        ( 4,  0, 0,  4,  0, 0),
        ( 4,  0, 1,  4,  0, 1),
        ( 4, 17, 0,  4, 17, 0),
        ( 4, 17, 1,  4, 17, 1),
        ( 5,  0, 0,  5,  0, 0),
        ( 5,  0, 1,  5,  0, 1),
        ( 5, 17, 0,  5, 17, 0),
        ( 5, 17, 1,  5, 17, 1),
        ( 6,  0, 0,  7,  0, 0),
        ( 6,  0, 1,  6,  0, 0),
        ( 6, 17, 1,  6, 17, 1),
        ( 7,  0, 0,  6,  0, 1),
        ( 7,  0, 1,  7,  0, 1),
        ( 7, 17, 0,  7, 17, 0),
        ( 7, 17, 1,  7, 17, 1),
        ( 8,  0, 0,  8,  0, 0),
        ( 8,  0, 1,  8,  0, 1),
        ( 8, 17, 0,  8, 17, 0),
        ( 8, 17, 1,  8, 17, 1),
        ( 9,  0, 0,  9,  0, 0),
        ( 9,  0, 1,  9,  0, 1),
        ( 9, 17, 0, 10, 17, 0),
        ( 9, 17, 1, 10, 17, 1),
        (10,  0, 0, 10,  0, 0),
        (10,  0, 1, 10,  0, 1),
        (10, 17, 0,  9, 17, 0),
        (10, 17, 1,  9, 17, 1),
        (11,  0, 0, 11,  0, 0),
        (11,  0, 1, 11,  0, 1),
        (11, 17, 0, 11, 17, 0),
        (11, 17, 1, 11, 17, 1),
        (12,  0, 0, 12,  0, 0),
        (12,  0, 1, 12,  0, 1),
        (12, 17, 0, 12, 17, 0),
        (12, 17, 1, 12, 17, 1),
        (13,  1, 0, 13,  1, 0),
        (13,  1, 1, 13,  1, 1),
        (13,  2, 0, 13,  2, 0),
        (13,  2, 1, 13,  2, 1),
        (13,  3, 1, 13,  3, 1),
        (13,  4, 0, 13,  4, 0),
        (13,  4, 1, 13,  4, 1),
        (13,  6, 0, 13,  6, 0),
        (13,  6, 1, 13,  6, 1),
        (13,  7, 0, 13,  7, 0),
        (13,  7, 1, 13,  7, 1),
        (13,  8, 0, 13,  8, 0),
        (13,  8, 1, 13,  8, 1),
        (13,  9, 0, 13,  9, 0),
        (13,  9, 1, 13,  9, 1),
        (13, 11, 0, 13, 10, 0),
        (13, 11, 1, 13, 10, 1),
        (13, 12, 0, 13, 11, 0),
        (13, 12, 1, 13, 11, 1),
        (13, 13, 0, 13, 13, 0),
        (13, 13, 1, 13, 13, 1),
        (13, 14, 0, 13, 14, 0),
        (13, 14, 1, 13, 14, 1),
        (13, 15, 0, 13, 15, 0),
        (13, 15, 1, 13, 15, 1),
    ],
    "8k": [
        ( 0,  3, 0,  0,  3, 0),
        ( 0,  3, 1,  0,  3, 1),
        ( 0,  4, 0,  0,  4, 0),
        ( 0,  4, 1,  0,  4, 1),
        ( 0,  5, 0,  0,  5, 0),
        ( 0,  5, 1,  0,  5, 1),
        ( 0,  6, 0,  0,  6, 0),
        ( 0,  6, 1,  0,  6, 1),
        ( 0,  7, 0,  0,  7, 0),
        ( 0,  7, 1,  0,  7, 1),
        ( 0,  8, 0,  0,  8, 0),
        ( 0,  8, 1,  0,  8, 1),
        ( 0,  9, 0,  0,  9, 0),
        ( 0,  9, 1,  0,  9, 1),
        ( 0, 10, 0,  0, 10, 0),
        ( 0, 10, 1,  0, 10, 1),
        ( 0, 11, 0,  0, 11, 0),
        ( 0, 11, 1,  0, 11, 1),
        ( 0, 12, 0,  0, 12, 0),
        ( 0, 12, 1,  0, 12, 1),
        ( 0, 13, 0,  0, 13, 0),
        ( 0, 13, 1,  0, 13, 1),
        ( 0, 14, 0,  0, 14, 0),
        ( 0, 14, 1,  0, 14, 1),
        ( 0, 16, 0,  0, 16, 0),
        ( 0, 16, 1,  0, 16, 1),
        ( 0, 17, 0,  0, 17, 0),
        ( 0, 17, 1,  0, 17, 1),
        ( 0, 18, 0,  0, 18, 0),
        ( 0, 18, 1,  0, 18, 1),
        ( 0, 19, 0,  0, 19, 0),
        ( 0, 19, 1,  0, 19, 1),
        ( 0, 20, 0,  0, 20, 0),
        ( 0, 20, 1,  0, 20, 1),
        ( 0, 21, 0,  0, 21, 0),
        ( 0, 21, 1,  0, 21, 1),
        ( 0, 22, 0,  0, 22, 0),
        ( 0, 22, 1,  0, 22, 1),
        ( 0, 23, 0,  0, 23, 0),
        ( 0, 23, 1,  0, 23, 1),
        ( 0, 24, 0,  0, 24, 0),
        ( 0, 24, 1,  0, 24, 1),
        ( 0, 25, 0,  0, 25, 0),
        ( 0, 25, 1,  0, 25, 1),
        ( 0, 27, 0,  0, 27, 0),
        ( 0, 27, 1,  0, 27, 1),
        ( 0, 28, 0,  0, 28, 0),
        ( 0, 28, 1,  0, 28, 1),
        ( 0, 30, 0,  0, 30, 0),
        ( 0, 30, 1,  0, 30, 1),
        ( 0, 31, 0,  0, 31, 0),
        ( 0, 31, 1,  0, 31, 1),
        ( 1, 33, 0,  1, 33, 0),
        ( 1, 33, 1,  1, 33, 1),
        ( 2,  0, 0,  2,  0, 0),
        ( 2,  0, 1,  2,  0, 1),
        ( 2, 33, 0,  2, 33, 0),
        ( 2, 33, 1,  2, 33, 1),
        ( 3,  0, 0,  3,  0, 0),
        ( 3,  0, 1,  3,  0, 1),
        ( 3, 33, 0,  3, 33, 0),
        ( 3, 33, 1,  3, 33, 1),
        ( 4,  0, 0,  4,  0, 0),
        ( 4,  0, 1,  4,  0, 1),
        ( 4, 33, 0,  4, 33, 0),
        ( 4, 33, 1,  4, 33, 1),
        ( 5,  0, 0,  5,  0, 0),
        ( 5,  0, 1,  5,  0, 1),
        ( 5, 33, 0,  5, 33, 0),
        ( 5, 33, 1,  5, 33, 1),
        ( 6,  0, 0,  6,  0, 0),
        ( 6,  0, 1,  6,  0, 1),
        ( 6, 33, 1,  6, 33, 1),
        ( 7,  0, 1,  7,  0, 1),
        ( 7, 33, 0,  7, 33, 0),
        ( 7, 33, 1,  7, 33, 1),
        ( 8,  0, 0,  8,  0, 0),
        ( 8, 33, 0,  8, 33, 0),
        ( 8, 33, 1,  8, 33, 1),
        ( 9,  0, 0,  9,  0, 0),
        ( 9,  0, 1,  9,  0, 1),
        ( 9, 33, 0,  9, 33, 0),
        ( 9, 33, 1,  9, 33, 1),
        (10,  0, 0, 10,  0, 0),
        (10,  0, 1, 10,  0, 1),
        (10, 33, 0, 10, 33, 0),
        (10, 33, 1, 10, 33, 1),
        (11,  0, 1, 11,  0, 1),
        (11, 33, 0, 11, 33, 0),
        (11, 33, 1, 11, 33, 1),
        (12,  0, 0, 12,  0, 0),
        (12,  0, 1, 12,  0, 1),
        (12, 33, 0, 12, 33, 0),
        (13,  0, 0, 13,  0, 0),
        (13,  0, 1, 13,  0, 1),
        (13, 33, 0, 13, 33, 0),
        (14,  0, 0, 14,  0, 0),
        (14,  0, 1, 14,  0, 1),
        (14, 33, 1, 14, 33, 1),
        (15,  0, 0, 15,  0, 0),
        (15,  0, 1, 15,  0, 1),
        (16,  0, 0, 16,  0, 0),
        (16,  0, 1, 16,  0, 1),
        (16, 33, 0, 16, 33, 0),
        (16, 33, 1, 16, 33, 1),
        (17,  0, 0, 17,  0, 0),
        (17,  0, 1, 17,  0, 1),
        (17, 33, 0, 17, 33, 0),
        (17, 33, 1, 17, 33, 1),
        (18, 33, 1, 18, 33, 1),
        (19,  0, 0, 19,  0, 0),
        (19,  0, 1, 19,  0, 1),
        (19, 33, 0, 19, 33, 0),
        (19, 33, 1, 19, 33, 1),
        (20,  0, 0, 20,  0, 0),
        (20,  0, 1, 20,  0, 1),
        (20, 33, 0, 20, 33, 0),
        (20, 33, 1, 20, 33, 1),
        (21,  0, 0, 21,  0, 0),
        (21,  0, 1, 21,  0, 1),
        (22,  0, 1, 22,  0, 1),
        (22, 33, 0, 22, 33, 0),
        (22, 33, 1, 22, 33, 1),
        (23,  0, 0, 23,  0, 0),
        (23,  0, 1, 23,  0, 1),
        (23, 33, 0, 23, 33, 0),
        (23, 33, 1, 23, 33, 1),
        (24,  0, 0, 24,  0, 0),
        (24, 33, 0, 24, 33, 0),
        (24, 33, 1, 24, 33, 1),
        (25, 33, 0, 25, 33, 0),
        (25, 33, 1, 25, 33, 1),
        (26,  0, 0, 26,  0, 0),
        (26,  0, 1, 26,  0, 1),
        (26, 33, 0, 26, 33, 0),
        (26, 33, 1, 26, 33, 1),
        (27,  0, 0, 27,  0, 0),
        (27,  0, 1, 27,  0, 1),
        (27, 33, 0, 27, 33, 0),
        (27, 33, 1, 27, 33, 1),
        (28,  0, 0, 28,  0, 0),
        (28, 33, 1, 28, 33, 1),
        (29,  0, 0, 29,  0, 0),
        (29,  0, 1, 29,  0, 1),
        (29, 33, 0, 29, 33, 0),
        (29, 33, 1, 29, 33, 1),
        (30,  0, 0, 30,  0, 0),
        (30,  0, 1, 30,  0, 1),
        (30, 33, 0, 30, 33, 0),
        (30, 33, 1, 30, 33, 1),
        (31,  0, 0, 31,  0, 0),
        (31,  0, 1, 31,  0, 1),
        (31, 33, 0, 31, 33, 0),
        (31, 33, 1, 31, 33, 1),
        (33,  1, 0, 33,  1, 0),
        (33,  1, 1, 33,  1, 1),
        (33,  2, 0, 33,  2, 0),
        (33,  2, 1, 33,  2, 1),
        (33,  3, 0, 33,  3, 0),
        (33,  3, 1, 33,  3, 1),
        (33,  4, 0, 33,  4, 0),
        (33,  4, 1, 33,  4, 1),
        (33,  5, 0, 33,  5, 0),
        (33,  5, 1, 33,  5, 1),
        (33,  6, 0, 33,  6, 0),
        (33,  6, 1, 33,  6, 1),
        (33,  7, 0, 33,  7, 0),
        (33,  7, 1, 33,  7, 1),
        (33,  8, 0, 33,  8, 0),
        (33,  9, 1, 33,  9, 1),
        (33, 10, 0, 33, 10, 0),
        (33, 10, 1, 33, 10, 1),
        (33, 11, 0, 33, 11, 0),
        (33, 11, 1, 33, 11, 1),
        (33, 12, 0, 33, 12, 0),
        (33, 13, 0, 33, 13, 0),
        (33, 13, 1, 33, 13, 1),
        (33, 14, 1, 33, 14, 1),
        (33, 15, 0, 33, 15, 0),
        (33, 15, 1, 33, 15, 1),
        (33, 16, 0, 33, 16, 0),
        (33, 16, 1, 33, 16, 1),
        (33, 17, 0, 33, 17, 0),
        (33, 17, 1, 33, 17, 1),
        (33, 19, 0, 33, 19, 0),
        (33, 19, 1, 33, 19, 1),
        (33, 20, 0, 33, 20, 0),
        (33, 20, 1, 33, 20, 1),
        (33, 21, 0, 33, 21, 0),
        (33, 21, 1, 33, 21, 1),
        (33, 22, 0, 33, 22, 0),
        (33, 22, 1, 33, 22, 1),
        (33, 23, 0, 33, 23, 0),
        (33, 23, 1, 33, 23, 1),
        (33, 24, 0, 33, 24, 0),
        (33, 24, 1, 33, 24, 1),
        (33, 25, 0, 33, 25, 0),
        (33, 25, 1, 33, 25, 1),
        (33, 26, 0, 33, 26, 0),
        (33, 26, 1, 33, 26, 1),
        (33, 27, 1, 33, 27, 1),
        (33, 28, 0, 33, 28, 0),
        (33, 28, 1, 33, 28, 1),
        (33, 30, 0, 33, 30, 0),
        (33, 30, 1, 33, 30, 1),
        (33, 31, 0, 33, 31, 0),
    ]
}

pinloc_db = {
    "1k-tq144": [
        (  "1",  0, 14, 1),
        ( "10",  0, 11, 0),
        ("101", 13, 13, 0),
        ("102", 13, 13, 1),
        ("104", 13, 14, 0),
        ("105", 13, 14, 1),
        ("106", 13, 15, 0),
        ("107", 13, 15, 1),
        ( "11",  0, 10, 1),
        ("112", 12, 17, 1),
        ("113", 12, 17, 0),
        ("114", 11, 17, 1),
        ("115", 11, 17, 0),
        ("116", 10, 17, 1),
        ("117", 10, 17, 0),
        ("118",  9, 17, 1),
        ("119",  9, 17, 0),
        ( "12",  0, 10, 0),
        ("120",  8, 17, 1),
        ("121",  8, 17, 0),
        ("122",  7, 17, 1),
        ("128",  7, 17, 0),
        ("129",  6, 17, 1),
        ("134",  5, 17, 1),
        ("135",  5, 17, 0),
        ("136",  4, 17, 1),
        ("137",  4, 17, 0),
        ("138",  3, 17, 1),
        ("139",  3, 17, 0),
        ("141",  2, 17, 1),
        ("142",  2, 17, 0),
        ("143",  1, 17, 1),
        ("144",  1, 17, 0),
        ( "19",  0,  9, 1),
        (  "2",  0, 14, 0),
        ( "20",  0,  9, 0),
        ( "21",  0,  8, 1),
        ( "22",  0,  8, 0),
        ( "23",  0,  6, 1),
        ( "24",  0,  6, 0),
        ( "25",  0,  5, 1),
        ( "26",  0,  5, 0),
        ( "28",  0,  4, 1),
        ( "29",  0,  4, 0),
        (  "3",  0, 13, 1),
        ( "31",  0,  3, 1),
        ( "32",  0,  3, 0),
        ( "33",  0,  2, 1),
        ( "34",  0,  2, 0),
        ( "37",  1,  0, 0),
        ( "38",  1,  0, 1),
        ( "39",  2,  0, 0),
        (  "4",  0, 13, 0),
        ( "41",  2,  0, 1),
        ( "42",  3,  0, 0),
        ( "43",  3,  0, 1),
        ( "44",  4,  0, 0),
        ( "45",  4,  0, 1),
        ( "47",  5,  0, 0),
        ( "48",  5,  0, 1),
        ( "49",  6,  0, 1),
        ( "50",  7,  0, 0),
        ( "52",  6,  0, 0),
        ( "56",  7,  0, 1),
        ( "58",  8,  0, 0),
        ( "60",  8,  0, 1),
        ( "61",  9,  0, 0),
        ( "62",  9,  0, 1),
        ( "63", 10,  0, 0),
        ( "64", 10,  0, 1),
        ( "67", 11,  0, 0),
        ( "68", 11,  0, 1),
        (  "7",  0, 12, 1),
        ( "70", 12,  0, 0),
        ( "71", 12,  0, 1),
        ( "73", 13,  1, 0),
        ( "74", 13,  1, 1),
        ( "75", 13,  2, 0),
        ( "76", 13,  2, 1),
        ( "78", 13,  3, 1),
        ( "79", 13,  4, 0),
        (  "8",  0, 12, 0),
        ( "80", 13,  4, 1),
        ( "81", 13,  6, 0),
        ( "87", 13,  6, 1),
        ( "88", 13,  7, 0),
        (  "9",  0, 11, 1),
        ( "90", 13,  7, 1),
        ( "91", 13,  8, 0),
        ( "93", 13,  8, 1),
        ( "94", 13,  9, 0),
        ( "95", 13,  9, 1),
        ( "96", 13, 11, 0),
        ( "97", 13, 11, 1),
        ( "98", 13, 12, 0),
        ( "99", 13, 12, 1),
    ],
    "8k-ct256": [
        ( "A1",  4, 33, 1),
        ("A10", 22, 33, 1),
        ("A11", 22, 33, 0),
        ("A15", 27, 33, 0),
        ("A16", 27, 33, 1),
        ( "A2",  5, 33, 1),
        ( "A5",  8, 33, 0),
        ( "A6",  9, 33, 0),
        ( "A7", 12, 33, 0),
        ( "A9", 18, 33, 1),
        ( "B1",  0, 30, 0),
        ("B10", 24, 33, 0),
        ("B11", 23, 33, 1),
        ("B12", 24, 33, 1),
        ("B13", 26, 33, 1),
        ("B14", 30, 33, 0),
        ("B15", 31, 33, 0),
        ("B16", 33, 30, 0),
        ( "B2",  0, 31, 0),
        ( "B3",  3, 33, 0),
        ( "B4",  6, 33, 1),
        ( "B5",  7, 33, 1),
        ( "B6", 10, 33, 1),
        ( "B7", 11, 33, 0),
        ( "B8", 13, 33, 0),
        ( "B9", 16, 33, 0),
        ( "C1",  0, 28, 1),
        ("C10", 23, 33, 0),
        ("C11", 25, 33, 1),
        ("C12", 29, 33, 1),
        ("C13", 28, 33, 1),
        ("C14", 31, 33, 1),
        ("C16", 33, 28, 0),
        ( "C2",  0, 28, 0),
        ( "C3",  1, 33, 0),
        ( "C4",  3, 33, 1),
        ( "C5",  4, 33, 0),
        ( "C6", 10, 33, 0),
        ( "C7", 11, 33, 1),
        ( "C8", 17, 33, 0),
        ( "C9", 20, 33, 0),
        ( "D1",  0, 25, 0),
        ("D10", 20, 33, 1),
        ("D11", 25, 33, 0),
        ("D13", 30, 33, 1),
        ("D14", 33, 31, 0),
        ("D15", 33, 26, 0),
        ("D16", 33, 24, 0),
        ( "D2",  0, 27, 0),
        ( "D3",  1, 33, 1),
        ( "D4",  2, 33, 1),
        ( "D5",  5, 33, 0),
        ( "D6",  8, 33, 1),
        ( "D7",  9, 33, 1),
        ( "D8", 14, 33, 1),
        ( "D9", 19, 33, 0),
        ("E10", 26, 33, 0),
        ("E11", 29, 33, 0),
        ("E13", 33, 30, 1),
        ("E14", 33, 27, 1),
        ("E16", 33, 23, 0),
        ( "E2",  0, 23, 0),
        ( "E3",  0, 24, 0),
        ( "E4",  0, 31, 1),
        ( "E5",  2, 33, 0),
        ( "E6",  7, 33, 0),
        ( "E9", 19, 33, 1),
        ( "F1",  0, 20, 0),
        ("F11", 33, 26, 1),
        ("F12", 33, 25, 1),
        ("F13", 33, 28, 1),
        ("F14", 33, 25, 0),
        ("F15", 33, 22, 0),
        ("F16", 33, 21, 0),
        ( "F2",  0, 21, 0),
        ( "F3",  0, 22, 0),
        ( "F4",  0, 27, 1),
        ( "F5",  0, 30, 1),
        ( "F7", 16, 33, 1),
        ( "F9", 17, 33, 1),
        ( "G1",  0, 17, 0),
        ("G10", 33, 20, 1),
        ("G11", 33, 21, 1),
        ("G12", 33, 24, 1),
        ("G13", 33, 23, 1),
        ("G14", 33, 22, 1),
        ("G15", 33, 20, 0),
        ("G16", 33, 19, 0),
        ( "G2",  0, 19, 0),
        ( "G3",  0, 22, 1),
        ( "G4",  0, 24, 1),
        ( "G5",  0, 25, 1),
        ( "H1",  0, 16, 0),
        ("H11", 33, 16, 1),
        ("H12", 33, 19, 1),
        ("H13", 33, 16, 0),
        ("H14", 33, 17, 1),
        ("H16", 33, 17, 0),
        ( "H2",  0, 18, 0),
        ( "H3",  0, 21, 1),
        ( "H4",  0, 19, 1),
        ( "H5",  0, 23, 1),
        ( "H6",  0, 20, 1),
        ( "J1",  0, 14, 0),
        ("J10", 33,  7, 1),
        ("J11", 33,  9, 1),
        ("J12", 33, 14, 1),
        ("J13", 33, 15, 0),
        ("J14", 33, 13, 1),
        ("J15", 33, 11, 1),
        ("J16", 33, 15, 1),
        ( "J2",  0, 14, 1),
        ( "J3",  0, 16, 1),
        ( "J4",  0, 18, 1),
        ( "J5",  0, 17, 1),
        ( "K1",  0, 13, 1),
        ("K11", 29,  0, 0),
        ("K12", 33,  6, 1),
        ("K13", 33, 10, 1),
        ("K14", 33, 11, 0),
        ("K15", 33, 12, 0),
        ("K16", 33, 13, 0),
        ( "K3",  0, 13, 0),
        ( "K4",  0, 11, 1),
        ( "K5",  0,  9, 1),
        ( "K9", 17,  0, 0),
        ( "L1",  0, 12, 0),
        ("L10", 19,  0, 1),
        ("L11", 26,  0, 1),
        ("L12", 33,  4, 1),
        ("L13", 33,  5, 1),
        ("L14", 33,  6, 0),
        ("L16", 33, 10, 0),
        ( "L3",  0, 10, 0),
        ( "L4",  0, 12, 1),
        ( "L5",  0,  6, 1),
        ( "L6",  0, 10, 1),
        ( "L7",  0,  8, 1),
        ( "L9", 13,  0, 0),
        ( "M1",  0, 11, 0),
        ("M11", 23,  0, 1),
        ("M12", 27,  0, 1),
        ("M13", 33,  3, 1),
        ("M14", 33,  4, 0),
        ("M15", 33,  8, 0),
        ("M16", 33,  7, 0),
        ( "M2",  0,  9, 0),
        ( "M3",  0,  7, 0),
        ( "M4",  0,  5, 0),
        ( "M5",  0,  4, 0),
        ( "M6",  0,  7, 1),
        ( "M7",  8,  0, 0),
        ( "M8", 10,  0, 0),
        ( "M9", 16,  0, 0),
        ("N10", 20,  0, 1),
        ("N12", 26,  0, 0),
        ("N16", 33,  5, 0),
        ( "N2",  0,  8, 0),
        ( "N3",  0,  6, 0),
        ( "N4",  0,  3, 0),
        ( "N5",  4,  0, 0),
        ( "N6",  2,  0, 0),
        ( "N7",  9,  0, 0),
        ( "N9", 15,  0, 0),
        ( "P1",  0,  5, 1),
        ("P10", 20,  0, 0),
        ("P11", 30,  0, 1),
        ("P12", 30,  0, 0),
        ("P13", 29,  0, 1),
        ("P14", 33,  2, 0),
        ("P15", 33,  2, 1),
        ("P16", 33,  3, 0),
        ( "P2",  0,  4, 1),
        ( "P4",  3,  0, 0),
        ( "P5",  5,  0, 0),
        ( "P6",  9,  0, 1),
        ( "P7", 14,  0, 1),
        ( "P8", 12,  0, 0),
        ( "P9", 17,  0, 1),
        ( "R1",  0,  3, 1),
        ("R10", 19,  0, 0),
        ("R11", 31,  0, 0),
        ("R12", 31,  0, 1),
        ("R14", 33,  1, 0),
        ("R15", 33,  1, 1),
        ("R16", 28,  0, 0),
        ( "R2",  3,  0, 1),
        ( "R3",  5,  0, 1),
        ( "R4",  7,  0, 1),
        ( "R5",  6,  0, 0),
        ( "R6", 11,  0, 1),
        ( "R9", 16,  0, 1),
        ( "T1",  2,  0, 1),
        ("T10", 21,  0, 0),
        ("T11", 21,  0, 1),
        ("T13", 24,  0, 0),
        ("T14", 23,  0, 0),
        ("T15", 22,  0, 1),
        ("T16", 27,  0, 0),
        ( "T2",  4,  0, 1),
        ( "T3",  6,  0, 1),
        ( "T5", 10,  0, 1),
        ( "T6", 12,  0, 1),
        ( "T7", 13,  0, 1),
        ( "T8", 14,  0, 0),
        ( "T9", 15,  0, 1),
    ]
}

iotile_full_db = parse_db(iceboxdb.database_io_txt)
logictile_db = parse_db(iceboxdb.database_logic_txt)
logictile_8k_db = parse_db(iceboxdb.database_logic_txt, True)
rambtile_db = parse_db(iceboxdb.database_ramb_txt)
ramttile_db = parse_db(iceboxdb.database_ramt_txt)
rambtile_8k_db = parse_db(iceboxdb.database_ramb_8k_txt, True)
ramttile_8k_db = parse_db(iceboxdb.database_ramt_8k_txt, True)

iotile_l_db = list()
iotile_r_db = list()
iotile_t_db = list()
iotile_b_db = list()

for entry in iotile_full_db:
    if entry[1] == "buffer" and entry[2].startswith("IO_L."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_l_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_R."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_r_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_T."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_t_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_B."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_b_db.append(new_entry)
    else:
        iotile_l_db.append(entry)
        iotile_r_db.append(entry)
        iotile_t_db.append(entry)
        iotile_b_db.append(entry)

logictile_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_db.append([["B1[50]"], "CarryInSet"])

logictile_8k_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_8k_db.append([["B1[50]"], "CarryInSet"])

for db in [iotile_l_db, iotile_r_db, iotile_t_db, iotile_b_db, logictile_db, logictile_8k_db, rambtile_db, ramttile_db, rambtile_8k_db, ramttile_8k_db]:
    for entry in db:
        if entry[1] in ("buffer", "routing"):
            entry[2] = netname_normalize(entry[2], ramb=(db == rambtile_db), ramt=(db == ramttile_db), ramb_8k=(db == rambtile_8k_db), ramt_8k=(db == ramttile_8k_db))
            entry[3] = netname_normalize(entry[3], ramb=(db == rambtile_db), ramt=(db == ramttile_db), ramb_8k=(db == rambtile_8k_db), ramt_8k=(db == ramttile_8k_db))
    unique_entries = dict()
    while db:
        entry = db.pop()
        key = " ".join(entry[1:]) + str(entry)
        unique_entries[key] = entry
    for key in sorted(unique_entries):
        db.append(unique_entries[key])

if __name__ == "__main__":
    run_checks()

