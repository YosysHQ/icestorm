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

check_mode = False
fixup_mode = False

def usage():
    print("""
Usage: icebox_colbuf [options] [input.txt [output.txt]]

    -c
        check colbuf bits

    -f
        fix colbuf bits
""")
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:], "cf")
except:
    usage()

for o, a in opts:
    if o == "-c":
        check_mode = True
    elif o == "-f":
        fixup_mode = True
    else:
        usage()

if len(args) == 0:
    args.append("/dev/stdin")

if len(args) not in [1, 2]:
    usage()

if check_mode == fixup_mode:
    print("Error: Use either -c or -f!")
    sys.exit(1)

print("Reading file '%s'.." % args[0])
ic = icebox.iceconfig()
ic.read_file(args[0])

def make_cache(stmt, raw_db):
    cache = list()
    for entry in raw_db:
        if entry[1] == stmt and entry[2].startswith("glb_netwk_"):
            cache_entry = [int(entry[2][-1]), []]
            for bit in entry[0]:
                value = "1"
                if bit.startswith("!"):
                    value = "0"
                    bit = bit[1:]
                match = re.match("B([0-9]+)\[([0-9]+)\]", bit)
                cache_entry[1].append((int(match.group(1)), int(match.group(2)), value))
            cache.append(cache_entry)
    return cache

def match_cache_entry(cache_entry, tile_dat):
    for entry in cache_entry[1]:
        if tile_dat[entry[0]][entry[1]] != entry[2]:
            return False
    return True

def analyze_tile(ic, cache, tile_pos):
    glbs = set()
    tile_dat = ic.tile(tile_pos[0], tile_pos[1])
    for cache_entry in cache:
        if match_cache_entry(cache_entry, tile_dat):
            glbs.add(cache_entry[0])
    return glbs

colbuf_map = dict()
used_glbs_map = dict()
driven_glbs_map = dict()

for entry in ic.colbuf_db():
    colbuf_map[(entry[2], entry[3])] = (entry[0], entry[1])

for tiles in [ic.io_tiles, ic.logic_tiles, ic.ramb_tiles, ic.ramt_tiles]:
    cache = None
    for tile in tiles:
        if cache is None:
            cache = make_cache("buffer", ic.tile_db(tile[0], tile[1]))
        glbs = analyze_tile(ic, cache, tile)
        if len(glbs):
            assert tile in colbuf_map
            s = used_glbs_map.setdefault(colbuf_map[tile], set())
            used_glbs_map[colbuf_map[tile]] = s.union(glbs)

    cache = None
    for tile in tiles:
        if cache is None:
            cache = make_cache("ColBufCtrl", ic.tile_db(tile[0], tile[1]))
        glbs = analyze_tile(ic, cache, tile)
        if len(glbs):
            driven_glbs_map[tile] = glbs

def set_colbuf(ic, tile, bit, value):
    tile_dat = ic.tile(tile[0], tile[1])
    tile_db = ic.tile_db(tile[0], tile[1])
    for entry in tile_db:
        if entry[1] == "ColBufCtrl" and entry[2] == "glb_netwk_%d" % bit:
            match = re.match("B([0-9]+)\[([0-9]+)\]", entry[0][0])
            l = tile_dat[int(match.group(1))]
            n = int(match.group(2))
            l = l[:n] + value + l[n+1:]
            tile_dat[int(match.group(1))] = l
            return
    assert False

error_count = 0
correct_count = 0
for tile, bits in sorted(used_glbs_map.items()):
    for bit in bits:
        if tile not in driven_glbs_map or bit not in driven_glbs_map[tile]:
            print("Missing driver for glb_netwk_%d in tile %s" % (bit, tile))
            set_colbuf(ic, tile, bit, "1")
            error_count += 1
for tile, bits in sorted(driven_glbs_map.items()):
    for bit in bits:
        if tile not in used_glbs_map or bit not in used_glbs_map[tile]:
            print("Unused driver for glb_netwk_%d in tile %s" % (bit, tile))
            set_colbuf(ic, tile, bit, "0")
            error_count += 1
        else:
            # print("Correct driver for glb_netwk_%d in tile %s" % (bit, tile))
            correct_count += 1
print("Found %d correct driver bits." % correct_count)
if error_count != 0:
    if not fixup_mode:
        print("Found %d errors!" % error_count)
        sys.exit(1)
    ic.write_file(args[0] if len(args) == 1 else args[1])
    print("Corrected %d errors." % error_count)
else:
    print("No errors found.")

