#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_gbio2" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for p in gpins:
    if p in pins: pins.remove(p)

# We can either tickle every global buffer or we don't have enough pins to do
# the full logic for each one.
w = min(min((len(pins) - 8) // 4, len(gpins)), 8)

for idx in range(num):
    with open(working_dir + "/gbio2_%02d.v" % idx, "w") as f:
        glbs = np.random.permutation(list(range(8)))
        print("""
            module top (
                inout [%s:0] pin,
                input latch_in,
                input clk_en,
                input clk_in,
                input clk_out,
                input oen,
                input dout_0,
                input dout_1,
                output [%s:0] din_0,
                output [%s:0] din_1,
                output [%s:0] globals,
                output reg q
            );
        """ % (
            w-1, w-1, w-1, w-1
        ), file=f);
        for k in range(w):
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
    with open(working_dir + "/gbio2_%02d.pcf" % idx, "w") as f:
        p = np.random.permutation(pins)
        g = np.random.permutation(gpins)
        for i in range(w):
            print("set_io pin[%d] %s" % (i, g[i]), file=f)
            print("set_io din_0[%d] %s" % (i, p[w+i]), file=f)
            print("set_io din_1[%d] %s" % (i, p[2*w+i]), file=f)
            print("set_io globals[%d] %s" % (i, p[3*w+i]), file=f)
        for i, n in enumerate("latch_in clk_en clk_in clk_out oen dout_0 dout_1".split()):
            print("set_io %s %s" % (n, p[4*w+i]), file=f)
        print("set_io q %s" % (p[-1]), file=f)


output_makefile(working_dir, "gbio2")
