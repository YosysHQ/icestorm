#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_cluster")
os.mkdir("work_cluster")

for idx in range(num):
    with open("work_cluster/cluster_%02d.v" % idx, "w") as f:
        print("module top(input [3:0] a, output [3:0] y);", file=f)
        print("  assign y = {|a, &a, ^a, a[3:2] == a[1:0]};", file=f)
        print("endmodule", file=f)
    with open("work_cluster/cluster_%02d.pcf" % idx, "w") as f:
        i = np.random.randint(len(pins))
        netnames = np.random.permutation(["a[%d]" % i for i in range(4)] + ["y[%d]" % i for i in range(4)])
        for net in netnames:
            print("set_io %s %s" % (net, pins[i]), file=f)
            i = (i + 1) % len(pins)

with open("work_cluster/Makefile", "w") as f:
    print("all: %s" % " ".join(["cluster_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("cluster_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh cluster_%02d > cluster_%02d.log 2>&1 && rm -rf cluster_%02d.tmp || tail cluster_%02d.log" % (i, i, i, i), file=f)

