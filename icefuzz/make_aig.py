#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_aig" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

w = len(pins) // 2

for idx in range(num):
    with open(working_dir + "/aig_%02d.v" % idx, "w") as f:
        print("module top(input [%d:0] a, output [%d:0] y);" % (w-1, w-1), file=f)

        sigs = ["a[%d]" % i for i in range(w)]
        netidx = 0

        for i in range(100 if num_ramb40 < 20 else 1000):
            netidx += 1
            newnet = "n_%d" % netidx

            print("  wire %s = %s%s && %s%s;" % (newnet,
                    np.random.choice(["", "!"]), np.random.choice(sigs),
                    np.random.choice(["", "!"]), np.random.choice(sigs)), file=f)

            sigs.append(newnet)

        while len(sigs) > w:
            netidx += 1
            newnet = "n_%d" % netidx

            a = np.random.choice(sigs)
            sigs.remove(a)

            b = np.random.choice(sigs)
            sigs.remove(b)

            print("  wire %s = %s%s && %s%s;" % (newnet,
                    np.random.choice(["", "!"]), a,
                    np.random.choice(["", "!"]), b), file=f)

            sigs.append(newnet)

        for i in range(w):
            print("  assign y[%d] = %s;" % (i, sigs[i]), file=f)

        print("endmodule", file=f)

    with open(working_dir + "/aig_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(w):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
            print("set_io y[%d] %s" % (i, p[i+w]), file=f)


output_makefile(working_dir, "aig")
