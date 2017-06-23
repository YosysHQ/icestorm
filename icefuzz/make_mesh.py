#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_mesh")
os.mkdir("work_mesh")

# This test maps a random set of pins to another random set of outputs.

device_class = os.getenv("ICEDEVICE")

for idx in range(num):
    io_count = len(pins) // 2
    with open("work_mesh/mesh_%02d.v" % idx, "w") as f:
        print("module top(input [%d:0] a, output [%d:0] y);" % (io_count, io_count), file=f)
        print("  assign y = a;", file=f)
        print("endmodule", file=f)
    with open("work_mesh/mesh_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(io_count):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
        for i in range(io_count):
            print("set_io y[%d] %s" % (i, p[io_count+i]), file=f)

with open("work_mesh/Makefile", "w") as f:
    print("all: %s" % " ".join(["mesh_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("mesh_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh mesh_%02d > mesh_%02d.log 2>&1 && rm -rf mesh_%02d.tmp || tail mesh_%02d.log" % (i, i, i, i), file=f)
