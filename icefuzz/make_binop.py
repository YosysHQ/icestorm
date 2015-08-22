#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_binop")
os.mkdir("work_binop")

for idx in range(num):
    with open("work_binop/binop_%02d.v" % idx, "w") as f:
        print("module top(input a, b, output y);", file=f)
        print("  assign y = a%sb;" % np.random.choice([" ^ ", " ^ ~", " & ", " & ~", " | ", " | ~"]), file=f)
        print("endmodule", file=f)
    with open("work_binop/binop_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        print("set_io a %s" % p[0], file=f)
        print("set_io b %s" % p[1], file=f)
        print("set_io y %s" % p[2], file=f)

with open("work_binop/Makefile", "w") as f:
    print("all: %s" % " ".join(["binop_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("binop_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh binop_%02d > binop_%02d.log 2>&1 && rm -rf binop_%02d.tmp || tail binop_%02d.log" % (i, i, i, i), file=f)

