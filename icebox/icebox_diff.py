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
import sys

print("Reading file '%s'.." % sys.argv[1])
ic1 = icebox.iceconfig()
ic1.read_file(sys.argv[1])

print("Reading file '%s'.." % sys.argv[2])
ic2 = icebox.iceconfig()
ic2.read_file(sys.argv[2])

def diff_tiles(stmt, tiles1, tiles2):
    for i in sorted(set(tiles1.keys() + tiles2.keys())):
        if not i in tiles1:
            print("+ %s %d %d" % (stmt, i[0], i[1]))
            for line in tiles2[i]:
                print("+ %s" % line)
            continue
        if not i in tiles2:
            print("- %s %d %d" % (stmt, i[0], i[1]))
            for line in tiles1[i]:
                print("- %s" % line)
            continue
        if tiles1[i] == tiles2[i]:
            continue
        print("  %s %d %d" % (stmt, i[0], i[1]))
        for c in range(len(tiles1[i])):
            if tiles1[i][c] == tiles2[i][c]:
                print("  %s" % tiles1[i][c])
            else:
                print("- %s" % tiles1[i][c])
                print("+ %s" % tiles2[i][c])

diff_tiles(".io_tile", ic1.io_tiles, ic2.io_tiles)
diff_tiles(".logic_tile", ic1.logic_tiles, ic2.logic_tiles)
diff_tiles(".ramb_tile", ic1.ramb_tiles, ic2.ramb_tiles)
diff_tiles(".ramt_tile", ic1.ramt_tiles, ic2.ramt_tiles)

