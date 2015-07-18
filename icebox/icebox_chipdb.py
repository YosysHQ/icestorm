#!/usr/bin/python
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

from __future__ import division
from __future__ import print_function

import icebox
import getopt, sys, re

ic = icebox.iceconfig()
ic.setup_empty_1k()

all_tiles = set()
for x in range(ic.max_x+1):
    for y in range(ic.max_y+1):
        if ic.tile(x, y) is not None:
            all_tiles.add((x, y))

seg_to_net = dict()
net_to_segs = list()

print("""#
# IceBox Database Dump for iCE40 HX1K / LP1K
#
#
# Quick File Format Reference:
# ----------------------------
#
#
# .io_tile X Y
# .logic_tile X Y
# .ram_tile X Y
#
#    declares the existence of a IO/LOGIC/RAM tile with the given coordinates
#
#
# .net NET_INDEX
# X1 Y1 name1
# X2 Y2 name2
# ...
#
#    declares a net on the chip and lists its various names in different tiles
#
#
# .buffer X Y DST_NET_INDEX CONFIG_BITS_NAMES
# CONFIG_BITS_VALUES_1 SRC_NET_INDEX_1
# CONFIG_BITS_VALUES_2 SRC_NET_INDEX_2
# ...
#
#    declares a buffer in the specified tile
#
#
# .routing X Y DST_NET_INDEX CONFIG_BITS_NAMES
# CONFIG_BITS_VALUES_1 SRC_NET_INDEX_1
# CONFIG_BITS_VALUES_2 SRC_NET_INDEX_2
# ...
#
#    declares a routing switch in the specified tile
#
""")

for idx in sorted(ic.io_tiles):
    print(".io_tile %d %d" % idx)
print()

for idx in sorted(ic.logic_tiles):
    print(".logic_tile %d %d" % idx)
print()

for idx in sorted(ic.ram_tiles):
    print(".ram_tile %d %d" % idx)
print()

for group in sorted(ic.group_segments(all_tiles)):
    netidx = len(net_to_segs)
    net_to_segs.append(group)
    print(".net %d" % netidx)
    for seg in group:
        print("%d %d %s" % seg)
        assert seg not in seg_to_net
        seg_to_net[seg] = netidx
    print()

for idx in sorted(all_tiles):
    db = ic.tile_db(idx[0], idx[1])
    db_by_bits = dict()
    for entry in db:
        if entry[1] in ("buffer", "routing") and ic.tile_has_net(idx[0], idx[1], entry[2]) and ic.tile_has_net(idx[0], idx[1], entry[3]):
            bits = tuple([entry[1]] + sorted([bit.replace("!", "") for bit in entry[0]]))
            db_by_bits.setdefault(bits, list()).append(entry)
    for bits in sorted(db_by_bits):
        dst_net = None
        for entry in sorted(db_by_bits[bits]):
            assert (idx[0], idx[1], entry[3]) in seg_to_net
            if dst_net is None:
                dst_net = seg_to_net[(idx[0], idx[1], entry[3])]
            else:
                assert dst_net == seg_to_net[(idx[0], idx[1], entry[3])]
        print(".%s %d %d %d %s" % (bits[0], idx[0], idx[1], dst_net, " ".join(bits[1:])))
        for entry in sorted(db_by_bits[bits]):
            pattern = ""
            for bit in bits[1:]:
                pattern += "1" if bit in entry[0] else "0"
            assert (idx[0], idx[1], entry[2]) in seg_to_net
            print("%s %d" % (pattern, seg_to_net[(idx[0], idx[1], entry[2])]))
        print()

