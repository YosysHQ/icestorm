#!/usr/bin/env python3
import os
import sys, re

db = set()
text_db = dict()
mode_8k = False
mode_384 = False
cur_text_db = None
max_x, max_y = 0, 0

device_class = os.getenv("ICEDEVICE")

for filename in sys.argv[1:]:
    with open(filename, "r") as f:
        ignore = False
        for line in f:
            if line == "\n":
                pass
            elif line.startswith("GlobalNetwork"):
                cur_text_db = set()
                ignore = False
            elif line.startswith("IO"):
                match = re.match("IO_Tile_(\d+)_(\d+)", line)
                assert match
                max_x = max(max_x, int(match.group(1)))
                max_y = max(max_y, int(match.group(2)))
                cur_text_db = text_db.setdefault("io", set())
                ignore = False
            elif line.startswith("Logic"):
                cur_text_db = text_db.setdefault("logic", set())
                ignore = False
            elif line.startswith("RAM"):
                match = re.match(r"RAM_Tile_\d+_(\d+)", line)
                if int(match.group(1)) % 2 == 1:
                    cur_text_db = text_db.setdefault("ramb_" + device_class if device_class in ["5k", "8k"] else "ramb", set())
                else:
                    cur_text_db = text_db.setdefault("ramt_" + device_class if device_class in ["5k", "8k"] else "ramt", set())
                ignore = False
            elif device_class == "5k" and line.startswith("IpCon"):
                cur_text_db = text_db.setdefault("ipcon_5k", set())
                ignore = False
            elif device_class == "u4k" and line.startswith("IpCon"):
                cur_text_db = text_db.setdefault("ipcon_5k", set())
                ignore = False
            elif device_class == "5k" and line.startswith("DSP"):
                match = re.match(r"DSP_Tile_\d+_(\d+)", line)
                ypos = int(match.group(1))
                dsp_idx = None
                if ypos in [5, 10, 15, 23]:
                    dsp_idx = 0
                if ypos in [6, 11, 16, 24]:
                    dsp_idx = 1
                if ypos in [7, 12, 17, 25]:
                    dsp_idx = 2
                if ypos in [8, 13, 18, 26]:
                    dsp_idx = 3
                assert dsp_idx != None
                cur_text_db = text_db.setdefault("dsp%d_5k" % dsp_idx, set())
                ignore = False
            elif device_class == "u4k" and line.startswith("DSP"):
                match = re.match(r"DSP_Tile_\d+_(\d+)", line)
                ypos = int(match.group(1))
                dsp_idx = None
                if ypos in [5, 13]:
                    dsp_idx = 0
                if ypos in [6, 14]:
                    dsp_idx = 1
                if ypos in [7, 15]:
                    dsp_idx = 2
                if ypos in [8, 16]:
                    dsp_idx = 3
                assert dsp_idx != None
                cur_text_db = text_db.setdefault("dsp%d_5k" % dsp_idx, set())
                ignore = False
            elif not ignore:
                print("'" + line + "'")
                assert line.startswith(" "), line
                cur_text_db.add(line)

def logic_op_prefix(match):
    x = int(match.group(1))
    y = int(match.group(2))
    if x == 0: return " IO_L.logic_op_"
    if y == 0: return " IO_B.logic_op_"
    if x == max_x: return " IO_R.logic_op_"
    if y == max_y: return " IO_T.logic_op_"
    assert False

for tile_type in text_db:
    for line in text_db[tile_type]:
        line = re.sub(" T_(\d+)_(\d+)\.logic_op_", logic_op_prefix, line)
        line = re.sub(" T_\d+_\d+\.", " ", line)
        m = re.match(" *(\([\d ]+\)) +\([\d ]+\) +\([\d ]+\) +(.*\S)", line)
        if m: db.add("%s %s %s" % (tile_type, m.group(1), m.group(2)))

for line in sorted(db):
    print(line)
