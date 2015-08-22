#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_pin2pin")
os.mkdir("work_pin2pin")

for idx in range(num):
    with open("work_pin2pin/pin2pin_%02d.v" % idx, "w") as f:
        print("module top(input a, output y);", file=f)
        print("  assign y = a;", file=f)
        print("endmodule", file=f)
    with open("work_pin2pin/pin2pin_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        print("set_io a %s" % p[0], file=f)
        print("set_io y %s" % p[1], file=f)

with open("work_pin2pin/Makefile", "w") as f:
    print("all: %s" % " ".join(["pin2pin_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("pin2pin_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh pin2pin_%02d > pin2pin_%02d.log 2>&1 && rm -rf pin2pin_%02d.tmp || tail pin2pin_%02d.log" % (i, i, i, i), file=f)

