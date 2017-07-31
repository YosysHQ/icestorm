#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_fflogic" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

w = (len(pins) - 4) // 5

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
    with open(working_dir + "/fflogic_%02d.v" % idx, "w") as f:
        print("module top(input clk, rst, en, input [%d:0] a, b, c, d, output [%d:0] y, output z);" % (w-1, w-1), file=f)
        print("  reg [%d:0] p, q;" % (w-1,), file=f)

        print_seq_op("p", "a", "b", random_op(), f)
        print_seq_op("q", "c", "d", random_op(), f)
        print("  assign y = p %s q, z = clk ^ rst ^ en;" % random_op(), file=f)
        print("endmodule", file=f)


output_makefile(working_dir, "fflogic")
