#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_fanout" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)


for idx in range(num):
    output_count = len(pins) - 2
    with open(working_dir + "/fanout_%02d.v" % idx, "w") as f:
        print("module top(input [1:0] a, output [%d:0] y);" % (output_count,), file=f)
        print("  assign y = {%d{a}};" % (output_count,), file=f)
        print("endmodule", file=f)
    with open(working_dir + "/fanout_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(output_count):
            print("set_io y[%d] %s" % (i, p[i]), file=f)
        print("set_io a[0] %s" % p[output_count], file=f)
        print("set_io a[1] %s" % p[output_count+1], file=f)


output_makefile(working_dir, "fanout")
