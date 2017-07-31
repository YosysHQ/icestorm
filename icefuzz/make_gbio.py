#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_gbio" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for p in gpins:
    if p in pins: pins.remove(p)

# We can either tickle every global buffer or we don't have enough pins to do
# the full logic for each one.
w = min(min((len(pins) - 8) // 4, len(gpins)), 8)

for idx in range(num):
    with open(working_dir + "/gbio_%02d.v" % idx, "w") as f:
        glbs = np.random.permutation(list(range(8)))

        if w <= 4:
          din_0 = (w - 2, w)
        else:
          din_0 = (3, "%d:4" % (w - 1,))
        din_0 = np.random.choice(["din_0",    "{din_0[%d:0], din_0[%s]}" % din_0])
        din_1 = np.random.choice(["din_1",    "{din_1[1:0], din_1[%d:2]}" % (w - 1,)])
        globals_0 = np.random.choice(["globals",  "{globals[0], globals[%d:1]}" % (w - 1, )])
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
                SB_GB_IO #(
                    .PIN_TYPE(6'b 1100_00),
                    .PULLUP(1'b0),
                    .NEG_TRIGGER(1'b0),
                    .IO_STANDARD("SB_LVCMOS")
                ) PINS [%s:0] (
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
            w-1, w-1, w-1, w-1, w-1,
            np.random.choice(["latch_in", "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_en",   "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_in",   "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["clk_out",  "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["oen",      "globals", "din_0+din_1", "din_0^din_1"]),
            np.random.choice(["dout_1",   "globals", "globals^dout_0", "din_0+din_1", "~din_0"]),
            np.random.choice(["dout_0",   "globals", "globals^dout_1", "din_0+din_1", "~din_1"]),
            din_0,
            din_1,
            globals_0,
            glbs[0], glbs[1], glbs[1], glbs[2], glbs[3]
        ), file=f)
    with open(working_dir + "/gbio_%02d.pcf" % idx, "w") as f:
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


output_makefile(working_dir, "gbio")
