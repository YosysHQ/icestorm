#!/usr/bin/env python3

from sys import argv, exit

asc_bits = set()
glb_bits = set()

# parsing .asc file
try:
    with open(argv[1]) as f:
        current_tile = None
        current_line = None
        for line in f:
            if line.startswith("."):
                if line.find("_tile ") >= 0:
                    f = line.split()
                    current_tile = "%02d.%02d" % (int(f[1]), int(f[2]))
                    current_line = 0
                else:
                    current_tile = None
                    current_line = None
                continue

            if current_tile is not None:
                for i in range(len(line)):
                    if line[i] == '1':
                        asc_bits.add("%s.%02d.%02d" % (current_tile, current_line, i))
                current_line += 1
except FileNotFoundError:
    print("ASC file doesn't exist, skipping glbcheck!.")
    # The asc file may not exist for innocent reasons, such as 
    # the icecube router failing. So exit with code 0 to keep
    # the fuzz Makefile happy
    exit(0)
# parsing .glb file
with open(argv[2]) as f:
    current_tile = None
    for line in f:
        if line.startswith(("Tile", "IO_Tile", "RAM_Tile", "LogicTile", "DSP_Tile", "IpCon_Tile")):
            f = line.replace("IO_", "").replace("RAM_", "").replace("DSP_","").replace("IpCon_","").split("_")
            assert len(f) == 3
            current_tile = "%02d.%02d" % (int(f[1]), int(f[2]))
            continue

        if line.find("GlobalNetwork") >= 0:
            current_tile = None
            continue

        if current_tile is not None:
            f = line.replace("(", "").replace(")", "").split()
            if len(f) >= 2:
                glb_bits.add("%s.%02d.%02d" % (current_tile, int(f[1]), int(f[0])))

# compare and report
if asc_bits == glb_bits:
    print("ASC and GLB files match.")
    exit(0)

only_in_asc = asc_bits - glb_bits
only_in_glb = glb_bits - asc_bits
assert len(only_in_asc) != 0 or len(only_in_glb) != 0

print("Only in ASC:")
for bit in sorted(only_in_asc):
  print(bit)

print()

print("Only in GLB:")
for bit in sorted(only_in_glb):
  print(bit)

exit(1)
