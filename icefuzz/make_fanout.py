#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_fanout")
os.mkdir("work_fanout")

for idx in range(num):
    with open("work_fanout/fanout_%02d.v" % idx, "w") as f:
        print("module top(input [1:0] a, output [63:0] y);", file=f)
        print("  assign y = {32{a}};", file=f)
        print("endmodule", file=f)
    with open("work_fanout/fanout_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(64):
            print("set_io y[%d] %s" % (i, p[i]), file=f)
        print("set_io a[0] %s" % p[64], file=f)
        print("set_io a[1] %s" % p[65], file=f)

with open("work_fanout/Makefile", "w") as f:
    print("all: %s" % " ".join(["fanout_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("fanout_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh fanout_%02d > fanout_%02d.log 2>&1 && rm -rf fanout_%02d.tmp || tail fanout_%02d.log" % (i, i, i, i), file=f)

