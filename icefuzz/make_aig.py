#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_aig")
os.mkdir("work_aig")

for idx in range(num):
    with open("work_aig/aig_%02d.v" % idx, "w") as f:
        print("module top(input [31:0] a, output [31:0] y);", file=f)

        sigs = ["a[%d]" % i for i in range(32)]
        netidx = 0

        for i in range(100 if num_ramb40 < 20 else 1000):
            netidx += 1
            newnet = "n_%d" % netidx

            print("  wire %s = %s%s && %s%s;" % (newnet,
                    np.random.choice(["", "!"]), np.random.choice(sigs),
                    np.random.choice(["", "!"]), np.random.choice(sigs)), file=f)

            sigs.append(newnet)

        while len(sigs) > 32:
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

        for i in range(32):
            print("  assign y[%d] = %s;" % (i, sigs[i]), file=f)

        print("endmodule", file=f)

    with open("work_aig/aig_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(32):
            print("set_io a[%d] %s" % (i, p[i]), file=f)
            print("set_io y[%d] %s" % (i, p[i+32]), file=f)

with open("work_aig/Makefile", "w") as f:
    print("all: %s" % " ".join(["aig_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("aig_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh aig_%02d > aig_%02d.log 2>&1 && rm -rf aig_%02d.tmp || tail aig_%02d.log" % (i, i, i, i), file=f)

