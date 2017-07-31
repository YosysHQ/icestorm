#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_mem" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for idx in range(num):
    with open(working_dir + "/mem_%02d.v" % idx, "w") as f:
        print("""
          module top(input clk, i0, i1, i2, i3, output reg o0, o1, o2, o3, o4);
            reg [9:0] raddr, waddr, rdata, wdata;
            reg [9:0] memory [0:1023];
            always @(posedge clk) begin
              case ({i0, i1, i2})
                0: raddr <= {raddr, i3};
                1: waddr <= {waddr, i3};
                2: wdata <= {wdata, i3};
                3: rdata <= memory[raddr];
                4: memory[waddr] <= wdata;
                5: rdata <= memory[waddr];
                6: {o0, o1, o2, o3, o4} <= rdata[4:0];
                7: {o0, o1, o2, o3, o4} <= rdata[9:5];
              endcase
            end
          endmodule
        """, file=f)
    with open(working_dir + "/mem_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for port in [ "clk", "i0", "i1", "i2", "i3", "o0", "o1", "o2", "o3", "o4" ]:
            print("set_io %s %s" % (port, p.pop()), file=f)


output_makefile(working_dir, "mem")

