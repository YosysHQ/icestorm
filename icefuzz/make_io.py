#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_io")
os.mkdir("work_io")

for idx in range(num):
    with open("work_io/io_%02d.v" % idx, "w") as f:
        glbs = np.random.permutation(list(range(8)))
        print("""
            module top (
                inout [3:0] pin,
                input [3:0] latch_in,
                input [3:0] clk_en,
                input [3:0] clk_in,
                input [3:0] clk_out,
                input [3:0] oen,
                input [3:0] dout_0,
                input [3:0] dout_1,
                output [3:0] din_0,
                output [3:0] din_1
            );
                SB_IO #(
                    .PIN_TYPE(6'b %s_%s),
                    .PULLUP(1'b %s),
                    .NEG_TRIGGER(1'b %s),
                    .IO_STANDARD("SB_LVCMOS")
                ) PINS [3:0] (
                    .PACKAGE_PIN(pin),
                    .LATCH_INPUT_VALUE(latch_in),
                    .CLOCK_ENABLE(clk_en),
                    .INPUT_CLK(clk_in),
                    .OUTPUT_CLK(clk_out),
                    .OUTPUT_ENABLE(oen),
                    .D_OUT_0(dout_0),
                    .D_OUT_1(dout_1),
                    .D_IN_0(din_0),
                    .D_IN_1(din_1)
                );
            endmodule
        """ % (
            np.random.choice(["0000", "0110", "1010", "1110", "0101", "1001", "1101", "0100", "1000", "1100", "0111", "1111"]),
            np.random.choice(["00", "01", "10", "11"]), np.random.choice(["0", "1"]), np.random.choice(["0", "1"])
        ), file=f)
    with open("work_io/io_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for k in ["pin", "latch_in", "clk_en", "clk_in", "clk_out", "oen", "dout_0", "dout_1", "din_0", "din_1"]:
            for i in range(4):
                print("set_io %s[%d] %s" % (k, i, p.pop()), file=f)

with open("work_io/Makefile", "w") as f:
    print("all: %s" % " ".join(["io_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("io_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh io_%02d > io_%02d.log 2>&1 && rm -rf io_%02d.tmp || tail io_%02d.log" % (i, i, i, i), file=f)

