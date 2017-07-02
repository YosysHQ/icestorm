#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_binop" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for idx in range(num):
    with open(working_dir + "/binop_%02d.v" % idx, "w") as f:
        print("module top(input a, b, output y);", file=f)
        print("  assign y = a%sb;" % np.random.choice([" ^ ", " ^ ~", " & ", " & ~", " | ", " | ~"]), file=f)
        print("endmodule", file=f)
    with open(working_dir + "/binop_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        print("set_io a %s" % p[0], file=f)
        print("set_io b %s" % p[1], file=f)
        print("set_io y %s" % p[2], file=f)


output_makefile(working_dir, "binop")

