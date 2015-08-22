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

import icebox
import getopt, sys, re

mode = None

def usage():
    print("Usage:")
    print("  icebox_maps -m bitmaps")
    print("  icebox_maps -m io_tile_nets_l")
    print("  icebox_maps -m io_tile_nets_r")
    print("  icebox_maps -m io_tile_nets_t")
    print("  icebox_maps -m io_tile_nets_b")
    print("  icebox_maps -m logic_tile_nets")
    print("  icebox_maps -m ramb_tile_nets")
    print("  icebox_maps -m ramt_tile_nets")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "m:")
except:
    usage()

for o, a in opts:
    if o == "-m":
        mode = a.strip()
    else:
        usage()

if len(args) != 0:
    usage()

def get_bit_group(x, y, db):
    bit = "B%d[%d]" % (y, x)
    nbit = "!B%d[%d]" % (y, x)
    funcs = set()
    for entry in db:
        if bit in entry[0] or nbit in entry[0]:
            if entry[1] in ("IOB_0", "IOB_1", "IoCtrl"):
                funcs.add("i")
            elif entry[1] == "routing":
                funcs.add("r")
            elif entry[1] == "buffer":
                funcs.add("b")
            elif re.match("LC_", entry[1]):
                funcs.add("l")
            elif entry[1] == "NegClk":
                funcs.add("N")
            elif entry[1] == "ColBufCtrl":
                funcs.add("o")
            elif entry[1] == "CarryInSet":
                funcs.add("C")
            elif entry[1] == "Cascade":
                funcs.add("a")
            else:
                funcs.add("?")
    if len(funcs) == 1:
        return funcs.pop()
    if len(funcs) > 1:
        return "X"
    return "-"

def print_tilemap(stmt, db, n):
    print()
    print(stmt)
    for y in range(16):
        for x in range(n):
            print(get_bit_group(x, y, db), end="")
        print()

def print_db_nets(stmt, db, pos):
    print()
    print(stmt, end="")
    netnames = set()
    for entry in db:
        if entry[1] in ("routing", "buffer"):
            if icebox.pos_has_net(pos[0], entry[2]): netnames.add(entry[2])
            if icebox.pos_has_net(pos[0], entry[3]): netnames.add(entry[3])
    last_prefix = ""
    for net in sorted(netnames, icebox.cmp_netnames):
        match = re.match(r"(.*?)(\d+)$", net)
        if match:
            if last_prefix == match.group(1):
                print(",%s" % match.group(2), end="")
            else:
                print()
                print(net, end="")
                last_prefix = match.group(1)
        else:
            print()
            print(net, end="")
            last_prefix = "*"
    print()

if mode == "bitmaps":
    print_tilemap(".io_tile_bitmap_l", icebox.iotile_l_db, 18)
    print_tilemap(".io_tile_bitmap_r", icebox.iotile_r_db, 18)
    print_tilemap(".io_tile_bitmap_t", icebox.iotile_t_db, 18)
    print_tilemap(".io_tile_bitmap_b", icebox.iotile_b_db, 18)
    print_tilemap(".logic_tile_bitmap", icebox.logictile_db, 54)
    print_tilemap(".ramb_tile_bitmap", icebox.rambtile_db, 42)
    print_tilemap(".ramt_tile_bitmap", icebox.ramttile_db, 42)
    print()
    print(".bitmap_legend")
    print("- ... unknown bit")
    print("? ... unknown bit type")
    print("X ... database conflict")
    print("i ... IOB_0 IOB_1 IoCtrl")
    print("a ... Carry_In_Mux Cascade")
    print("r ... routing")
    print("b ... buffer")
    print("l ... logic bits")
    print("o ... ColBufCtrl")
    print("C ... CarryInSet")
    print("N ... NegClk")
    print()

elif mode == "io_tile_nets_l":
    print_db_nets(".io_tile_nets_l", icebox.iotile_l_db, "l")

elif mode == "io_tile_nets_r":
    print_db_nets(".io_tile_nets_r", icebox.iotile_r_db, "r")

elif mode == "io_tile_nets_t":
    print_db_nets(".io_tile_nets_t", icebox.iotile_t_db, "t")

elif mode == "io_tile_nets_b":
    print_db_nets(".io_tile_nets_b", icebox.iotile_b_db, "b")

elif mode == "logic_tile_nets":
    print_db_nets(".logic_tile_nets", icebox.logictile_db, "c")

elif mode == "ramb_tile_nets":
    print_db_nets(".ramb_tile_nets", icebox.ramtile_db, "c")

elif mode == "ramt_tile_nets":
    print_db_nets(".ramt_tile_nets", icebox.ramtile_db, "c")

else:
    usage()

