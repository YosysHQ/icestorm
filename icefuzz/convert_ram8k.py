#!/usr/bin/python2
# convert 1k ramb/ramt to 8k ramb/ramt and vice versa

subst_rules = [
    ["/RE",     "/WE"   ],
    ["/RCLK",   "/WCLK" ],
    ["/RCLKE",  "/WCLKE"],
    ["DATA_8",  "DATA_7"],
    ["DATA_9",  "DATA_6"],
    ["DATA_10", "DATA_5"],
    ["DATA_11", "DATA_4"],
    ["DATA_12", "DATA_3"],
    ["DATA_13", "DATA_2"],
    ["DATA_14", "DATA_1"],
    ["DATA_15", "DATA_0"],
]

import fileinput
for line in fileinput.input():
    line = line.strip()
    for r in subst_rules:
        if line.endswith(r[0]):
            line = line[:-len(r[0])] + r[1]
            break
        if line.endswith(r[1]):
            line = line[:-len(r[1])] + r[0]
            break
    print(line)
