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
from icebox import re_match_cached
import getopt, sys, re

verbose = False

def usage():
    print("""
Usage: icebox_stat [options] [bitmap.asc]

    -v
        verbose output

""")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "v")
except:
    usage()

for o, a in opts:
    if o == "-v":
        verbose = True
    else:
        usage()

if len(args) == 0:
    args.append("/dev/stdin")

if len(args) != 1:
    usage()

if verbose:
    print("Reading input file.")

ic = icebox.iceconfig()
ic.read_file(args[0])

dff_locations = set()
lut_locations = set()
carry_locations = set()
bram_locations = set()
io_locations = set()
pll_locations = set()
global_nets = set()

if verbose:
    print("Analyzing connectivity.")

connections = sorted(ic.group_segments())

if verbose:
    print("Counting resources.")

for segs in connections:
    for seg in segs:
        if ic.tile_type(seg[0], seg[1]) == "IO" and seg[2].startswith("io_"):
            match = re_match_cached("io_(\d+)/D_(IN|OUT)_(\d+)", seg[2])
            if match:
                loc = (seg[0], seg[1], int(match.group(1)))
                io_locations.add(loc)

        if ic.tile_type(seg[0], seg[1]) == "LOGIC" and seg[2].startswith("lutff_"):
            match = re_match_cached("lutff_(\d)/in_\d", seg[2])
            if match:
                loc = (seg[0], seg[1], int(match.group(1)))
                lut_locations.add(loc)

            match = re_match_cached("lutff_(\d)/cout", seg[2])
            if match:
                loc = (seg[0], seg[1], int(match.group(1)))
                carry_locations.add(loc)

            match = re_match_cached("lutff_(\d)/out", seg[2])
            if match:
                loc = (seg[0], seg[1], int(match.group(1)))
                seq_bits = icebox.get_lutff_seq_bits(ic.tile(loc[0], loc[1]), loc[2])
                if seq_bits[1] == "1":
                    dff_locations.add(loc)

        if ic.tile_type(seg[0], seg[1]) in ("RAMB", "RAMT") and seg[2].startswith("ram/"):
            loc = (seg[0], seg[1] - (seg[1] % 2))
            bram_locations.add(loc)

        if seg[2].startswith("glb_netwk_"):
            match = re_match_cached("glb_netwk_(\d)", seg[2])
            if match:
                global_nets.add(int(match.group(1)))

pll_config_bitidx = dict()

for entry in icebox.iotile_l_db:
    if entry[1] == "PLL":
        match = re_match_cached(r"B(\d+)\[(\d+)\]", entry[0][0]);
        assert match
        pll_config_bitidx[entry[2]] = (int(match.group(1)), int(match.group(2)))

def get_pll_bit(pllinfo, name):
    bit = pllinfo[name]
    assert bit[2] in pll_config_bitidx
    return ic.tile(bit[0], bit[1])[pll_config_bitidx[bit[2]][0]][pll_config_bitidx[bit[2]][1]]

def get_pll_bits(pllinfo, name, n):
    return "".join([get_pll_bit(pllinfo, "%s_%d" % (name, i)) for i in range(n-1, -1, -1)])

for pllid in ic.pll_list():
    pllinfo = icebox.pllinfo_db[pllid]
    plltype = get_pll_bits(pllinfo, "PLLTYPE", 3)
    if plltype != "000":
        pll_locations.add(pllid)

if verbose:
    print()

print("DFFs:   %4d" % len(dff_locations))
print("LUTs:   %4d" % len(lut_locations))
print("CARRYs: %4d" % len(carry_locations))
print("BRAMs:  %4d" % len(bram_locations))
print("IOBs:   %4d" % len(io_locations))
print("PLLs:   %4d" % len(pll_locations))
print("GLBs:   %4d" % len(global_nets))

