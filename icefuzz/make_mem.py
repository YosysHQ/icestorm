#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_mem")
os.mkdir("work_mem")

for idx in range(num):
    with open("work_mem/mem_%02d.v" % idx, "w") as f:
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
    with open("work_mem/mem_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for port in [ "clk", "i0", "i1", "i2", "i3", "o0", "o1", "o2", "o3", "o4" ]:
            print("set_io %s %s" % (port, p.pop()), file=f)

with open("work_mem/Makefile", "w") as f:
    print("all: %s" % " ".join(["mem_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("mem_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh mem_%02d > mem_%02d.log 2>&1 && rm -rf mem_%02d.tmp || tail mem_%02d.log" % (i, i, i, i), file=f)

