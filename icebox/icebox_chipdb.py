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

mode_8k = False

def usage():
    print("""
Usage: icebox_chipdb [options] [bitmap.txt]

    -8
        create chipdb for 8k device
""")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "8")
except:
    usage()

for o, a in opts:
    if o == "-8":
        mode_8k = True
    else:
        usage()

ic = icebox.iceconfig()
if mode_8k:
    ic.setup_empty_8k()
else:
    ic.setup_empty_1k()

all_tiles = set()
for x in range(ic.max_x+1):
    for y in range(ic.max_y+1):
        if ic.tile(x, y) is not None:
            all_tiles.add((x, y))

seg_to_net = dict()
net_to_segs = list()

print("""#
# IceBox Chip Database Dump (iCE40 %s)
#
#
# Quick File Format Reference:
# ----------------------------
#
# .device DEVICE WIDTH HEIGHT NUM_NETS
#
#    declares the device type
#
#
# .pins PACKAGE
# PIN_NUM TILE_X TILE_Y PIO_NUM
# ...
#
#    associates a package pin with an IO tile and block, and global network
#
#
# .gbufin
# TILE_X TILE_Y GLB_NUM
# ...
#
#    associates an IO tile with the global network can drive via fabout
#
#
# .gbufpin
# TILE_X TILE_Y PIO_NUM GLB_NUM
# ...
#
#    associates an IO tile with the global network can drive via the pad
#
#
# .iolatch
# TILE_X TILE_Y
# ...
#
#    specifies the IO tiles that drive the latch signal for the bank via fabout
#
#
# .ieren
# PIO_TILE_X PIO_TILE_Y PIO_NUM IEREN_TILE_X IEREN_TILE_Y IEREN_NUM
# ...
#
#    associates an IO block with an IeRen-block
#
#
# .colbuf
# SOURCE_TILE_X SOURCE_TILE_Y DEST_TILE_X DEST_TILE_Y
# ...
#
#    declares the positions of the column buffers
#
#
# .io_tile X Y
# .logic_tile X Y
# .ramb_tile X Y
# .ramt_tile X Y
#
#    declares the existence of a IO/LOGIC/RAM tile with the given coordinates
#
#
# .io_tile_bits COLUMNS ROWS
# .logic_tile_bits COLUMNS ROWS
# .ramb_tile_bits COLUMNS ROWS
# .ramt_tile_bits COLUMNS ROWS
# FUNCTION_1 CONFIG_BITS_NAMES_1
# FUNCTION_2 CONFIG_BITS_NAMES_2
# ...
#
#    declares non-routing configuration bits of IO/LOGIC/RAM tiles
#
#
# .extra_cell X Y <cell-type>
# KEY MULTI-FIELD-VALUE
# ....
#
#    declares a special-purpose cell that is not part of the FPGA fabric
#
# 
# .extra_bits
# FUNCTION BANK_NUM ADDR_X ADDR_Y
# ...
#
#    declares non-routing global configuration bits
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
""" % ic.device)

all_group_segments = ic.group_segments(all_tiles, connect_gb=False)

print(".device %s %d %d %d" % (ic.device, ic.max_x+1, ic.max_y+1, len(all_group_segments)))
print()

for key in list(icebox.pinloc_db.keys()):
    key_dev, key_package = key.split("-")
    if key_dev == ic.device:
        print(".pins %s" % (key_package))
        for entry in sorted(icebox.pinloc_db[key]):
            print("%s %d %d %d" % entry)
        print()

print(".gbufin")
for entry in sorted(ic.gbufin_db()):
    print(" ".join(["%d" % k for k in entry]))
print()

print(".gbufpin")
for padin, pio in enumerate(ic.padin_pio_db()):
    entry = pio + (padin,)
    print(" ".join(["%d" % k for k in entry]))
print()

print(".iolatch")
for entry in sorted(ic.iolatch_db()):
    print(" ".join(["%d" % k for k in entry]))
print()

print(".ieren")
for entry in sorted(ic.ieren_db()):
    print(" ".join(["%d" % k for k in entry]))
print()

print(".colbuf")
for entry in sorted(ic.colbuf_db()):
    print(" ".join(["%d" % k for k in entry]))
print()

for idx in sorted(ic.io_tiles):
    print(".io_tile %d %d" % idx)
print()

for idx in sorted(ic.logic_tiles):
    print(".logic_tile %d %d" % idx)
print()

for idx in sorted(ic.ramb_tiles):
    print(".ramb_tile %d %d" % idx)
print()

for idx in sorted(ic.ramt_tiles):
    print(".ramt_tile %d %d" % idx)
print()

def print_tile_nonrouting_bits(tile_type, idx):
    tx = idx[0]
    ty = idx[1]
    
    tile = ic.tile(tx, ty)
    
    print(".%s_tile_bits %d %d" % (tile_type, len(tile[0]), len(tile)))
    
    function_bits = dict()
    for entry in ic.tile_db(tx, ty):
        if not ic.tile_has_entry(tx, ty, entry):
            continue
        if entry[1] in ("routing", "buffer"):
            continue
        
        func = ".".join(entry[1:])
        function_bits[func] = entry[0]
    
    for x in sorted(function_bits):
        print(" ".join([x] + function_bits[x]))
    print()

print_tile_nonrouting_bits("logic", list(ic.logic_tiles.keys())[0])
print_tile_nonrouting_bits("io", list(ic.io_tiles.keys())[0])
print_tile_nonrouting_bits("ramb", list(ic.ramb_tiles.keys())[0])
print_tile_nonrouting_bits("ramt", list(ic.ramt_tiles.keys())[0])

print(".extra_cell 0 0 WARMBOOT")
for key in sorted(icebox.warmbootinfo_db[ic.device]):
    print("%s %s" % (key, " ".join([str(k) for k in icebox.warmbootinfo_db[ic.device][key]])))
print()

for pllid in ic.pll_list():
    pllinfo = icebox.pllinfo_db[pllid]
    print(".extra_cell %d %d PLL" % pllinfo["LOC"])
    for key in sorted(pllinfo):
        if key != "LOC":
            print("%s %s" % (key, " ".join([str(k) for k in pllinfo[key]])))
    print()

print(".extra_bits")
extra_bits = dict()
for idx in sorted(ic.extra_bits_db()):
    extra_bits[".".join(ic.extra_bits_db()[idx])] = " ".join(["%d" % k for k in idx])
for idx in sorted(extra_bits):
    print("%s %s" % (idx, extra_bits[idx]))
print()

for group in sorted(all_group_segments):
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

