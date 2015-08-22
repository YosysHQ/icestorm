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
import sys
import re

print("Reading file '%s'.." % sys.argv[1])
ic1 = icebox.iceconfig()
ic1.read_file(sys.argv[1])

print("Reading file '%s'.." % sys.argv[2])
ic2 = icebox.iceconfig()
ic2.read_file(sys.argv[2])

def format_bits(line_nr, this_line, other_line):
    text = ""
    for i in range(len(this_line)):
        if this_line[i] != other_line[i]:
            if this_line[i] == "1":
                text += "%8s" % ("B%d[%d]" % (line_nr, i))
            else:
                text += "%8s" % ""
    return text

def explained_bits(db, tile):
    bits = set()
    mapped_bits = set()
    for k, line in enumerate(tile):
        for i in range(len(line)):
            if line[i] == "1":
                bits.add("B%d[%d]" % (k, i))
            else:
                bits.add("!B%d[%d]" % (k, i))
    text = set()
    for entry in db:
        if re.match(r"LC_", entry[1]):
            continue
        if entry[1] in ("routing", "buffer"):
            continue
        match = True
        for bit in entry[0]:
            if not bit in bits:
                match = False
        if match:
            text.add("<%s> %s" % (",".join(entry[0]), " ".join(entry[1:])))
    return text

def diff_tiles(stmt, tiles1, tiles2):
    for i in sorted(set(list(tiles1.keys()) + list(tiles2.keys()))):
        if not i in tiles1:
            print("+ %s %d %d" % (stmt, i[0], i[1]))
            for line in tiles2[i]:
                print("+ %s" % line)
            print()
            continue
        if not i in tiles2:
            print("- %s %d %d" % (stmt, i[0], i[1]))
            for line in tiles1[i]:
                print("- %s" % line)
            print()
            continue
        if tiles1[i] == tiles2[i]:
            continue
        print("  %s %d %d" % (stmt, i[0], i[1]))
        for c in range(len(tiles1[i])):
            if tiles1[i][c] == tiles2[i][c]:
                print("  %s" % tiles1[i][c])
            else:
                print("- %s%s" % (tiles1[i][c], format_bits(c, tiles1[i][c], tiles2[i][c])))
                print("+ %s%s" % (tiles2[i][c], format_bits(c, tiles2[i][c], tiles1[i][c])))
        bits1 = explained_bits(ic1.tile_db(i[0], i[1]), tiles1[i])
        bits2 = explained_bits(ic2.tile_db(i[0], i[1]), tiles2[i])
        for bit in sorted(bits1):
            if bit not in bits2:
                print("- %s" % bit)
        for bit in sorted(bits2):
            if bit not in bits1:
                print("+ %s" % bit)
        print()

diff_tiles(".io_tile", ic1.io_tiles, ic2.io_tiles)
diff_tiles(".logic_tile", ic1.logic_tiles, ic2.logic_tiles)
diff_tiles(".ramb_tile", ic1.ramb_tiles, ic2.ramb_tiles)
diff_tiles(".ramt_tile", ic1.ramt_tiles, ic2.ramt_tiles)

