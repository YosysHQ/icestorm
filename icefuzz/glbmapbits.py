#!/usr/bin/env python3

import re
import fileinput

tiletype = ""
x, y = 0, 0

for line in fileinput.input():
    if line.startswith("LogicTile"):
        fields = line.split("_")
        tiletype = "Logic"
        x, y = int(fields[1]), int(fields[2])
        continue

    if line.startswith("RAM_Tile") or line.startswith("IO_Tile"):
        fields = line.split("_")
        tiletype = fields[0]
        x, y = int(fields[2]), int(fields[3])
        continue

    if line.startswith("GlobalNetwork"):
        tiletype = ""
        continue

    if tiletype != "":
        fields = re.split('[ ()]*', line.strip())
        if len(fields) <= 1: continue
        fields = [int(fields[i+1]) for i in range(4)]
        print("%-5s %2d %2d %2d %2d %3d %3d" % (tiletype, x, y, fields[0], fields[1], fields[2], fields[3]))

