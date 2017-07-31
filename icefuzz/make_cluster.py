#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_cluster" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for idx in range(num):
    with open(working_dir + "/cluster_%02d.v" % idx, "w") as f:
        print("module top(input [3:0] a, output [3:0] y);", file=f)
        print("  assign y = {|a, &a, ^a, a[3:2] == a[1:0]};", file=f)
        print("endmodule", file=f)
    with open(working_dir + "/cluster_%02d.pcf" % idx, "w") as f:
        i = np.random.randint(len(pins))
        netnames = np.random.permutation(["a[%d]" % i for i in range(4)] + ["y[%d]" % i for i in range(4)])
        for net in netnames:
            print("set_io %s %s" % (net, pins[i]), file=f)
            i = (i + 1) % len(pins)

output_makefile(working_dir, "cluster")
