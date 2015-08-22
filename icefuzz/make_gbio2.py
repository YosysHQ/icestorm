#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_gbio2")
os.mkdir("work_gbio2")

for idx in range(num):
    with open("work_gbio2/gbio2_%02d.v" % idx, "w") as f:
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
        """, file=f);
        for k in range(8):
            print("""
                SB_GB_IO #(
                    .PIN_TYPE(6'b %s),
                    .PULLUP(1'b %s),
                    .NEG_TRIGGER(1'b %s),
                    .IO_STANDARD("SB_LVCMOS")
                ) \pin[%d]_gb_io (
                    .PACKAGE_PIN(pin[%d]),
                    .LATCH_INPUT_VALUE(latch_in),
                    .CLOCK_ENABLE(clk_en),
                    .INPUT_CLK(clk_in),
                    .OUTPUT_CLK(clk_out),
                    .OUTPUT_ENABLE(oen),
                    .D_OUT_0(dout_0),
                    .D_OUT_1(dout_1),
                    .D_IN_0(din_0[%d]),
                    .D_IN_1(din_1[%d]),
                    .GLOBAL_BUFFER_OUTPUT(globals[%d])
                );
            """ % (
                np.random.choice(["1100_00", "1010_10", "1010_00", "0000_11", "1111_00"]),
                np.random.choice(["0", "1"]),
                np.random.choice(["0", "1"]),
                k, k, k, k, k
            ), file=f)
        print("""
                always @(posedge globals[%d], posedge globals[%d])
                    if (globals[%d])
                        q <= 0;
                    else if (globals[%d])
                        q <= globals[%d];
            endmodule
        """ % (
            glbs[0], glbs[1], glbs[1], glbs[2], glbs[3]
        ), file=f)
    with open("work_gbio2/gbio2_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        for i in range(8):
            print("set_io pin[%d] %s" % (i, p[i]), file=f)
            print("set_io din_0[%d] %s" % (i, p[8+i]), file=f)
            print("set_io din_1[%d] %s" % (i, p[2*8+i]), file=f)
            print("set_io globals[%d] %s" % (i, p[3*8+i]), file=f)
        for i, n in enumerate("latch_in clk_en clk_in clk_out oen dout_0 dout_1".split()):
            print("set_io %s %s" % (n, p[4*8+i]), file=f)
        print("set_io q %s" % (p[-1]), file=f)

with open("work_gbio2/Makefile", "w") as f:
    print("all: %s" % " ".join(["gbio2_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("gbio2_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh gbio2_%02d > gbio2_%02d.log 2>&1 && rm -rf gbio2_%02d.tmp || tail gbio2_%02d.log" % (i, i, i, i), file=f)

