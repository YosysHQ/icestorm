#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_prim" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

w = len(pins) // 4

for idx in range(num):
    with open(working_dir + "/prim_%02d.v" % idx, "w") as f:
        clkedge = np.random.choice(["pos", "neg"])
        print("module top(input clk, input [%s:0] a, b, output reg x, output reg [%s:0] y);""" % ( w-1, w-1 ), file=f)
        print("  reg [%s:0] aa, bb;""" % ( w-1 ), file=f)
        print("  always @(%sedge clk) aa <= a;" % clkedge, file=f)
        print("  always @(%sedge clk) bb <= b;" % clkedge, file=f)
        if np.random.choice([True, False]):
            print("  always @(%sedge clk) x <= %s%s;" % (clkedge, np.random.choice(["^", "&", "|", "!"]), np.random.choice(["a", "b", "y"])), file=f)
        else:
            print("  always @(%sedge clk) x <= a%sb;" % (clkedge, np.random.choice(["&&", "||"])), file=f)
        if np.random.choice([True, False]):
            print("  always @(%sedge clk) y <= a%sb;" % (clkedge, np.random.choice(["+", "-", "&", "|"])), file=f)
        else:
            print("  always @(%sedge clk) y <= %s%s;" % (clkedge, np.random.choice(["~", "-", ""]), np.random.choice(["a", "b"])), file=f)
        print("endmodule", file=f)
    with open(working_dir + "/prim_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        if np.random.choice([True, False]):
            for i in range(w):
                print("set_io a[%d] %s" % (i, p[i]), file=f)
        if np.random.choice([True, False]):
            for i in range(w):
                print("set_io b[%d] %s" % (i, p[w+i]), file=f)
        if np.random.choice([True, False]):
            for i in range(w):
                print("set_io y[%d] %s" % (i, p[2*w+i]), file=f)
        if np.random.choice([True, False]):
            print("set_io x %s" % p[3*w], file=f)
        if np.random.choice([True, False]):
            print("set_io y %s" % p[3*w+1], file=f)
        if np.random.choice([True, False]):
            print("set_io clk %s" % p[3*w+2], file=f)


output_makefile(working_dir, "prim")
