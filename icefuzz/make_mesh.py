#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os


device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_mesh" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

# This test maps a random set of pins to another random set of outputs.

device_class = os.getenv("ICEDEVICE")

for idx in range(num):
    io_count = len(pins) // 2
    with open(working_dir + "/mesh_%02d.v" % idx, "w") as f:
        print("module top(input [%d:0] a, output [%d:0] y);" % (io_count, io_count), file=f)
        print("  assign y = a;", file=f)
        print("endmodule", file=f)
    with open(working_dir + "/mesh_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(io_count):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
        for i in range(io_count):
            print("set_io y[%d] %s" % (i, p[io_count+i]), file=f)


output_makefile(working_dir, "mesh")
