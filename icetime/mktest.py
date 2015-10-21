#!/usr/bin/env python3

import sys, os, shutil
import numpy as np

pins = np.random.permutation("""
    1 2 3 4 7 8 9 10 11 12 19 22 23 24 25 26 28 29 31 32 33 34
    37 38 41 42 43 44 45 47 48 52 56 58 60 61 62 63 64
    73 74 75 76 78 79 80 81 87 88 90 91 95 96 97 98 101 102 104 105 106 107
    112 113 114 115 116 117 118 119 120 121 122 134 135 136 137 138 139 141 142 143 144
""".split())

with open("%s.v" % sys.argv[1], "w") as f:
    print("module top(input i0, output o0, o1, o2, o3);", file=f)
    print("  assign {o0, o1, o2, o3} = {i0, i0, !i0, !i0};", file=f)
    print("endmodule", file=f)

with open("%s.pcf" % sys.argv[1], "w") as f:
    print("set_io i0 %s" % pins[0], file=f)
    print("set_io o0 %s" % pins[1], file=f)
    print("set_io o1 %s" % pins[2], file=f)
    print("set_io o2 %s" % pins[3], file=f)
    print("set_io o3 %s" % pins[4], file=f)

os.system("bash ../icefuzz/icecube.sh %s.v" % sys.argv[1])
os.rename("%s.v" % sys.argv[1], "%s_in.v" % sys.argv[1])
os.rename("%s.vsb" % sys.argv[1], "%s_ref.v" % sys.argv[1])

os.remove("%s.bin" % sys.argv[1])
os.remove("%s.glb" % sys.argv[1])
os.remove("%s.psb" % sys.argv[1])
os.remove("%s.sdf" % sys.argv[1])
shutil.rmtree("%s.tmp" % sys.argv[1])

