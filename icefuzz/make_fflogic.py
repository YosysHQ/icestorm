#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_fflogic")
os.mkdir("work_fflogic")

def random_op():
    return np.random.choice(["+", "-", "*", "^", "&", "|"])

def print_seq_op(dst, src1, src2, op, f):
    mode = np.random.choice(list("abc"))
    negreset = np.random.choice(["!", ""])
    enable = np.random.choice(["if (en) ", ""])
    if mode == "a":
        print("  always @(%sedge clk) begin" % np.random.choice(["pos", "neg"]), file=f)
        print("    %s%s <= %s %s %s;" % (enable, dst, src1, op, src2), file=f)
        print("  end", file=f)
    elif mode == "b":
        print("  always @(%sedge clk) begin" % np.random.choice(["pos", "neg"]), file=f)
        print("    if (%srst)" % negreset, file=f)
        print("      %s <= %d;" % (dst, np.random.randint(2**16)), file=f)
        print("    else", file=f)
        print("      %s%s <= %s %s %s;" % (enable, dst, src1, op, src2), file=f)
        print("  end", file=f)
    elif mode == "c":
        print("  always @(%sedge clk, %sedge rst) begin" % (np.random.choice(["pos", "neg"]), "neg" if negreset == "!" else "pos"), file=f)
        print("    if (%srst)" % negreset, file=f)
        print("      %s <= %d;" % (dst, np.random.randint(2**16)), file=f)
        print("    else", file=f)
        print("      %s%s <= %s %s %s;" % (enable, dst, src1, op, src2), file=f)
        print("  end", file=f)
    else:
        assert False

for idx in range(num):
    with open("work_fflogic/fflogic_%02d.v" % idx, "w") as f:
        print("module top(input clk, rst, en, input [15:0] a, b, c, d, output [15:0] y, output z);", file=f)
        print("  reg [15:0] p, q;", file=f)
        print_seq_op("p", "a", "b", random_op(), f)
        print_seq_op("q", "c", "d", random_op(), f)
        print("  assign y = p %s q, z = clk ^ rst ^ en;" % random_op(), file=f)
        print("endmodule", file=f)

with open("work_fflogic/Makefile", "w") as f:
    print("all: %s" % " ".join(["fflogic_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("fflogic_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh fflogic_%02d > fflogic_%02d.log 2>&1 && rm -rf fflogic_%02d.tmp || tail fflogic_%02d.log" % (i, i, i, i), file=f)

