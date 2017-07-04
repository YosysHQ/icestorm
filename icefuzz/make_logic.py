#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_logic" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

def random_op():
    return np.random.choice(["+", "-", "^", "&", "|", "&~", "|~"])

for idx in range(num):
    bus_width = len(pins) // 5
    with open(working_dir + "/logic_%02d.v" % idx, "w") as f:
        print("module top(input [%d:0] a, b, c, d, output [%d:0] y);" % (bus_width, bus_width), file=f)
        print("  assign y = (a %s b) %s (c %s d);" % (random_op(), random_op(), random_op()), file=f)
        print("endmodule", file=f)
    with open(working_dir + "/logic_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(bus_width):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
            print("set_io b[%d] %s" % (i, p[i+bus_width]), file=f)
            print("set_io c[%d] %s" % (i, p[i+bus_width*2]), file=f)
            print("set_io d[%d] %s" % (i, p[i+bus_width*3]), file=f)
            print("set_io y[%d] %s" % (i, p[i+bus_width*4]), file=f)

output_makefile(working_dir, "logic")
