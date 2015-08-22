#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_logic")
os.mkdir("work_logic")

def random_op():
    return np.random.choice(["+", "-", "^", "&", "|", "&~", "|~"])

for idx in range(num):
    with open("work_logic/logic_%02d.v" % idx, "w") as f:
        print("module top(input [15:0] a, b, c, d, output [15:0] y);", file=f)
        print("  assign y = (a %s b) %s (c %s d);" % (random_op(), random_op(), random_op()), file=f)
        print("endmodule", file=f)
    with open("work_logic/logic_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(16):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
            print("set_io b[%d] %s" % (i, p[i+16]), file=f)
            print("set_io c[%d] %s" % (i, p[i+32]), file=f)
            print("set_io d[%d] %s" % (i, p[i+48]), file=f)
            print("set_io y[%d] %s" % (i, p[i+64]), file=f)

with open("work_logic/Makefile", "w") as f:
    print("all: %s" % " ".join(["logic_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("logic_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh logic_%02d > logic_%02d.log 2>&1 && rm -rf logic_%02d.tmp || tail logic_%02d.log" % (i, i, i, i), file=f)

