#!/usr/bin/env python3

import fileinput

colbuf_tile = None
glbnet_tile = None

for line in fileinput.input():
    line = line.split()
    if len(line) == 0:
        continue
    if line[0] in [".io_tile", ".logic_tile", ".ramb_tile", ".ramt_tile"]:
        current_tile = (int(line[1]), int(line[2]))
    if line[0] == "ColBufCtrl":
        assert colbuf_tile is None
        colbuf_tile = current_tile
    if line[0] == "buffer" and line[1].startswith("glb_netwk_"):
        assert glbnet_tile is None
        glbnet_tile = current_tile

print("(%2d, %2d, %2d, %2d)," % (colbuf_tile[0], colbuf_tile[1], glbnet_tile[0], glbnet_tile[1]))

