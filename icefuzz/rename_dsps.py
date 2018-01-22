#!/usr/bin/env python3

import sys, os

dsptype = None
dsppath = sys.argv[1].replace(".vsb", ".dsp")

if os.path.exists(dsppath):
    with open(dsppath, 'r') as f:
        dsptype = f.readline().strip()
        
with open("tmedges.tmp", "a") as outfile:
    with open("tmedges_unrenamed.tmp", "r") as infile:
        for line in infile:
            if "SB_MAC16" in line:
                if dsptype is not None:
                    outfile.write(line.replace("SB_MAC16", dsptype))
            else:
                outfile.write(line)
