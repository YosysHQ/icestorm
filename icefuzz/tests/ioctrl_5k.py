#!/usr/bin/env python3

import fileinput

for line in fileinput.input():
    line = line.split()
    if len(line) == 0:
        continue
    if line[0] == ".io_tile":
        current_tile = (int(line[1]), int(line[2]))
    if line[0] == "IoCtrl" and line[1] == "REN_0":
        ren = (current_tile[0], current_tile[1], 0)
    if line[0] == "IoCtrl" and line[1] == "REN_1":
        ren = (current_tile[0], current_tile[1], 1)
    if line[0] == "IOB_0":
        iob = (current_tile[0], current_tile[1], 0)
    if line[0] == "IOB_1":
        iob = (current_tile[0], current_tile[1], 1)

print("(%2d, %2d, %2d, %2d, %2d, %2d)," % (iob[0], iob[1], iob[2], ren[0], ren[1], ren[2]))

