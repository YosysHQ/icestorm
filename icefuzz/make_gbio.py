#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_gbio")
os.mkdir("work_gbio")

for idx in range(num):
    with open("work_gbio/gbio_%02d.v" % idx, "w") as f:
        glbs = np.random.permutation(list(range(8)))
        print("""
            module top (
                inout [7:0] pin,
                input latch_in,
                input clk_en,
                input clk_in,
                input clk_out,
                input oen,
                input dout_0,
                input dout_1,
                output [7:0] din_0,
                output [7:0] din_1,
                output [7:0] globals,
                output reg q
            );
                SB_GB_IO #(
                    .PIN_TYPE(6'b 1100_00),
                    .PULLUP(1'b0),
                    .NEG_TRIGGER(1'b0),
                    .IO_STANDARD("SB_LVCMOS")
                ) PINS [7:0] (
                    .PACKAGE_PIN(pin),
                    .LATCH_INPUT_VALUE(%s),
                    .CLOCK_ENABLE(%s),
                    .INPUT_CLK(%s),
                    .OUTPUT_CLK(%s),
                    .OUTPUT_ENABLE(%s),
                    .D_OUT_0(%s),
                    .D_OUT_1(%s),
                    .D_IN_0(%s),
                    .D_IN_1(%s),
                    .GLOBAL_BUFFER_OUTPUT(%s)
                );

                always @(posedge globals[%d], posedge globals[%d])
                    if (globals[%d])
                        q <= 0;
                    else if (globals[%d])
                        q <= globals[%d];
            endmodule
        """ % (
            np.random.choice(["latch_in", "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_en",   "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_in",   "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_out",  "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["oen",      "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["dout_1",   "globals", "globals^dout_0", "din_0+din_1", "~din_0"]),
            np.random.choice(["dout_0",   "globals", "globals^dout_1", "din_0+din_1", "~din_1"]),
            np.random.choice(["din_0",    "{din_0[3:0], din_0[7:4]}"]),
            np.random.choice(["din_1",    "{din_1[1:0], din_1[7:2]}"]),
            np.random.choice(["globals",  "{globals[0], globals[7:1]}"]),
            glbs[0], glbs[1], glbs[1], glbs[2], glbs[3]
        ), file=f)
    with open("work_gbio/gbio_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(8):
            print("set_io pin[%d] %s" % (i, p[i]), file=f)
            print("set_io din_0[%d] %s" % (i, p[8+i]), file=f)
            print("set_io din_1[%d] %s" % (i, p[2*8+i]), file=f)
            print("set_io globals[%d] %s" % (i, p[3*8+i]), file=f)
        for i, n in enumerate("latch_in clk_en clk_in clk_out oen dout_0 dout_1".split()):
            print("set_io %s %s" % (n, p[4*8+i]), file=f)
        print("set_io q %s" % (p[-1]), file=f)

with open("work_gbio/Makefile", "w") as f:
    print("all: %s" % " ".join(["gbio_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("gbio_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh gbio_%02d > gbio_%02d.log 2>&1 && rm -rf gbio_%02d.tmp || tail gbio_%02d.log" % (i, i, i, i), file=f)

