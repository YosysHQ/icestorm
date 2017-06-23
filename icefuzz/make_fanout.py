#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_fanout")
os.mkdir("work_fanout")


for idx in range(num):
    output_count = len(pins) - 2
    with open("work_fanout/fanout_%02d.v" % idx, "w") as f:
        print("module top(input [1:0] a, output [%d:0] y);" % (output_count,), file=f)
        print("  assign y = {%d{a}};" % (output_count,), file=f)
        print("endmodule", file=f)
    with open("work_fanout/fanout_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(output_count):
            print("set_io y[%d] %s" % (i, p[i]), file=f)
        print("set_io a[0] %s" % p[output_count], file=f)
        print("set_io a[1] %s" % p[output_count+1], file=f)

with open("work_fanout/Makefile", "w") as f:
    print("all: %s" % " ".join(["fanout_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("fanout_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh fanout_%02d > fanout_%02d.log 2>&1 && rm -rf fanout_%02d.tmp || tail fanout_%02d.log" % (i, i, i, i), file=f)
