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

print_bits = False
print_map = False
single_tile = None
print_all = False

def usage():
    print("""
Usage: icebox_explain [options] [bitmap.txt]

    -b
        print config bit names for each config statement

    -m
        print tile config bitmaps

    -A
        don't skip uninteresting tiles

    -t '<x-coordinate> <y-coordinate>'
        print only the specified tile
""")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "bmAt:")
except:
    usage()

for o, a in opts:
    if o == "-b":
        print_bits = True
    elif o == "-m":
        print_map = True
    elif o == "-A":
        print_all = True
    elif o == "-t":
        single_tile = tuple([int(s) for s in a.split()])
    else:
        usage()

if len(args) == 0:
    args.append("/dev/stdin")

if len(args) != 1:
    usage()

print("Reading file '%s'.." % args[0])
ic = icebox.iceconfig()
ic.read_file(args[0])
print("Fabric size (without IO tiles): %d x %d" % (ic.max_x-1, ic.max_y-1))

def print_tile(stmt, ic, x, y, tile, db):
    if single_tile is not None and single_tile != (x, y):
        return

    bits = set()
    mapped_bits = set()
    for k, line in enumerate(tile):
        for i in range(len(line)):
            if line[i] == "1":
                bits.add("B%d[%d]" % (k, i))
            else:
                bits.add("!B%d[%d]" % (k, i))

    if re.search(r"logic_tile", stmt):
        active_luts = set([i for i in range(8) if "1" in icebox.get_lutff_bits(tile, i)])

    text = set()
    used_lc = set()
    text_default_mask = 0
    for entry in db:
        if re.match(r"LC_", entry[1]):
            continue
        if entry[1] in ("routing", "buffer"):
            if not ic.tile_has_net(x, y, entry[2]): continue
            if not ic.tile_has_net(x, y, entry[3]): continue
        match = True
        for bit in entry[0]:
            if not bit in bits:
                match = False
        if match:
            for bit in entry[0]:
                mapped_bits.add(bit)
            if entry[1] == "IoCtrl" and entry[2] == "IE_0":
                text_default_mask |= 1
            if entry[1] == "IoCtrl" and entry[2] == "IE_1":
                text_default_mask |= 2
            if entry[1] == "RamConfig" and entry[2] == "PowerUp":
                text_default_mask |= 4
            if print_bits:
                text.add("<%s> %s" % (" ".join(entry[0]), " ".join(entry[1:])))
            else:
                text.add(" ".join(entry[1:]))
    bitinfo = list()
    print_bitinfo = False
    for k, line in enumerate(tile):
        bitinfo.append("")
        extra_text = ""
        for i in range(len(line)):
            if 36 <= i <= 45 and re.search(r"logic_tile", stmt):
                lutff_idx = k // 2
                lutff_bitnum = (i-36) + 10*(k%2)
                if line[i] == "1":
                    used_lc.add(lutff_idx)
                    bitinfo[-1] += "*"
                else:
                    bitinfo[-1] += "-"
            elif line[i] == "1" and "B%d[%d]" % (k, i) not in mapped_bits:
                print_bitinfo = True
                extra_text += " B%d[%d]" % (k, i)
                bitinfo[-1] += "?"
            else:
                bitinfo[-1] += "+" if line[i] == "1" else "-"
        bitinfo[-1] += extra_text
    for lcidx in sorted(used_lc):
        lutff_options = "".join(icebox.get_lutff_seq_bits(tile, lcidx))
        if lutff_options[0] == "1": lutff_options += " CarryEnable"
        if lutff_options[1] == "1": lutff_options += " DffEnable"
        if lutff_options[2] == "1": lutff_options += " Set_NoReset"
        if lutff_options[3] == "1": lutff_options += " AsyncSetReset"
        text.add("LC_%d %s %s" % (lcidx, "".join(icebox.get_lutff_lut_bits(tile, lcidx)), lutff_options))
    if not print_bitinfo and not print_all:
        if text_default_mask == 3 and len(text) == 2:
            return
        if text_default_mask == 4 and len(text) == 1:
            return
    if len(text) or print_bitinfo or print_all:
        print("\n%s" % stmt)
        if print_bitinfo:
            print("Warning: No DB entries for some bits:")
        if print_bitinfo or print_map:
            for k, line in enumerate(bitinfo):
                print("%4s %s" % ("B%d" % k, line))
        for line in sorted(text):
            print(line)

for idx in ic.io_tiles:
    print_tile(".io_tile %d %d" % idx, ic, idx[0], idx[1], ic.io_tiles[idx], ic.tile_db(idx[0], idx[1]))

for idx in ic.logic_tiles:
    print_tile(".logic_tile %d %d" % idx, ic, idx[0], idx[1], ic.logic_tiles[idx], ic.tile_db(idx[0], idx[1]))

for idx in ic.ramb_tiles:
    print_tile(".ramb_tile %d %d" % idx, ic, idx[0], idx[1], ic.ramb_tiles[idx], ic.tile_db(idx[0], idx[1]))

for idx in ic.ramt_tiles:
    print_tile(".ramt_tile %d %d" % idx, ic, idx[0], idx[1], ic.ramt_tiles[idx], ic.tile_db(idx[0], idx[1]))

for bit in ic.extra_bits:
    print()
    print(".extra_bit %d %d %d" % bit)
    print(" ".join(ic.lookup_extra_bit(bit)))

print()

