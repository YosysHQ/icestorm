#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_pin2pin" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for idx in range(num):
    with open(working_dir + "/pin2pin_%02d.v" % idx, "w") as f:
        print("module top(input a, output y);", file=f)
        print("  assign y = a;", file=f)
        print("endmodule", file=f)
    with open(working_dir + "/pin2pin_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        print("set_io a %s" % p[0], file=f)
        print("set_io y %s" % p[1], file=f)


output_makefile(working_dir, "pin2pin")

