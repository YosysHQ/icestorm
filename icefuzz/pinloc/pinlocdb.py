#!/usr/bin/env python3

import re
from sys import argv

ieren_db = [ ]
pinloc_db = [ ]

for arg in argv[1:]:
    pin = re.search(r"_([^.]*)", arg).group(1)
    with open(arg, "r") as f:
        tile = [0, 0]
        iob = [0, 0, 0]
        ioctrl = [0, 0, 0]

        for line in f:
            match = re.match(r"^\.io_tile (\d+) (\d+)", line)
            if match:
                tile = [int(match.group(1)), int(match.group(2))]

            match = re.match(r"^IOB_(\d+)", line)
            if match:
                iob = tile + [int(match.group(1))]

            match = re.match(r"^IoCtrl REN_(\d+)", line)
            if match:
                ioctrl = tile + [int(match.group(1))]

        ieren_db.append(tuple(iob + ioctrl))
        pinloc_db.append(tuple(['"' + pin + '"'] + iob))

print()
print("# ieren_db")
for entry in sorted(ieren_db):
    print("(%2d, %2d, %d, %2d, %2d, %d)," % entry)

print()
print("# pinloc_db")
for entry in sorted(pinloc_db):
    print("(%5s, %2d, %2d, %d)," % entry)

print()

