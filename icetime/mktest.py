#!/usr/bin/env python3

import sys, os, re, shutil
import numpy as np

max_span_hack = True

pins = np.random.permutation("""
    1 2 3 4 7 8 9 10 11 12 19 22 23 24 25 26 28 29 31 32 33 34
    37 38 41 42 43 44 45 47 48 52 56 58 60 61 62 63 64
    73 74 75 76 78 79 80 81 87 88 90 91 95 96 97 98 101 102 104 105 106 107
    112 113 114 115 116 117 118 119 120 121 122 134 135 136 137 138 139 141 142 143 144
""".split())

io_names = None
mode = sys.argv[1]

with open("%s.v" % sys.argv[1], "w") as f:
    if mode == "test0":
        io_names = [ "clk", "i0", "o0", "o1", "o2" ]
        print("module top(input clk, i0, output o0, o1, o2);", file=f)
        print("  reg [31:0] state;", file=f)
        print("  always @(posedge clk) state <= ((state << 5) + state) ^ i0;", file=f)
        print("  assign o0 = ^state, o1 = |state, o2 = state[31:16] + state[15:0];", file=f)
        print("endmodule", file=f)
    if mode == "test1":
        io_names = [ "clk", "i0", "i1", "i2", "i3", "o0", "o1", "o2", "o3" ]
        print("module top(input clk, i0, i1, i2, i3, output o0, o1, o2, o3);", file=f)
        print("  reg [15:0] din, dout;", file=f)
        print("  always @(posedge clk) din <= {din, i3, i2, i1, i0};", file=f)
        print("  always @(posedge clk) dout <= din + {din[7:0], din[15:8]};", file=f)
        print("  assign {o3, o2, o1, o0} = dout >> din;", file=f)
        print("endmodule", file=f)
    if mode == "test2":
        io_names = [ "clk", "i0", "i1", "i2", "i3", "o0", "o1", "o2", "o3" ]
        print("""
          module top(input clk, i0, i1, i2, i3, output reg o0, o1, o2, o3);
            reg [7:0] raddr, waddr, rdata, wdata;
            reg [7:0] memory [0:255];
            always @(posedge clk) begin
              case ({i0, i1, i2})
                0: raddr <= {raddr, i3};
                1: waddr <= {waddr, i3};
                2: wdata <= {wdata, i3};
                3: rdata <= memory[raddr];
                4: memory[waddr] <= wdata;
                5: {o0, o1, o2, o3} <= rdata[3:0];
                6: {o0, o1, o2, o3} <= rdata[7:4];
              endcase
            end
          endmodule
        """, file=f)
    if mode == "test3":
        io_names = [ "clk", "i0", "i1", "i2", "i3", "o0", "o1", "o2", "o3", "o4" ]
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
    if mode == "test4":
        io_names = [ "clk", "i", "s", "o" ]
        print("""
          module top(input clk, i, s, output reg o);
            reg re1, rclke1, we1, wclke1;
            reg [7:0] raddr1, waddr1;
            reg [15:0] rdata1, wdata1, mask1;
            wire [15:0] rdata1_unreg;

            reg re2, rclke2, we2, wclke2;
            reg [7:0] raddr2, waddr2;
            reg [15:0] rdata2, wdata2, mask2;
            wire [15:0] rdata2_unreg;

            always @(posedge clk) begin
              o <= rdata1[15];
              {rdata1, rdata2} <= {rdata1, rdata2} << 1;
              {raddr1, waddr1, wdata1, mask1, re1, rclke1, we1, wclke1,
               raddr2, waddr2, wdata2, mask2, re2, rclke2, we2, wclke2} <=
                ({raddr1, waddr1, wdata1, mask1, re1, rclke1, we1, wclke1,
                  raddr2, waddr2, wdata2, mask2, re2, rclke2, we2, wclke2} << 1) | i;
              if (s) begin
                rdata1 <= rdata1_unreg;
                rdata2 <= rdata2_unreg;
              end
            end

            SB_RAM40_4K mem1 (
              .RDATA(rdata1_unreg),
              .RCLK(clk),
              .RCLKE(rclke1),
              .RE(re1),
              .RADDR(raddr1),
              .WCLK(clk),
              .WCLKE(wclke1),
              .WE(we1),
              .WADDR(waddr1),
              .MASK(mask1),
              .WDATA(wdata1)
            );

            SB_RAM40_4K mem2 (
              .RDATA(rdata2_unreg),
              .RCLK(clk),
              .RCLKE(rclke2),
              .RE(re2),
              .RADDR(raddr1), // <- cascade
              .WCLK(clk),
              .WCLKE(wclke2),
              .WE(we2),
              .WADDR(waddr1), // <- cascade
              .MASK(mask2),
              .WDATA(wdata2)
            );
          endmodule
        """, file=f)

with open("%s.pcf" % sys.argv[1], "w") as f:
    for i, name in enumerate(io_names):
        print("set_io %s %s" % (name, pins[i]), file=f)

with open("%s.ys" % sys.argv[1], "w") as f:
    print("echo on", file=f)
    print("read_verilog -lib cells.v", file=f)
    print("read_verilog %s_ref.v" % sys.argv[1], file=f)
    print("read_verilog %s_out.v" % sys.argv[1], file=f)
    print("prep", file=f)
    print("equiv_make top chip equiv", file=f)
    print("# check -assert", file=f)
    print("cd equiv", file=f)
    print("script %s.lc" % sys.argv[1], file=f)
    print("rename -hide w:N_*", file=f)
    print("equiv_struct -maxiter 100", file=f)
    print("opt_clean -purge", file=f)
    print("write_ilang %s.il" % sys.argv[1], file=f)
    print("equiv_status -assert", file=f)

assert os.system("bash ../icefuzz/icecube.sh %s.v" % sys.argv[1]) == 0
os.rename("%s.v" % sys.argv[1], "%s_in.v" % sys.argv[1])

if False:
    assert os.system("python3 ../icebox/icebox_explain.py %s.asc > %s.ex" % (sys.argv[1], sys.argv[1])) == 0

with open("%s_ref.v" % sys.argv[1], "w") as f:
    for line in open("%s.vsb" % sys.argv[1], "r"):
        if re.match(r" *defparam .*\.(IO_STANDARD|PULLUP|INIT_.|WRITE_MODE|READ_MODE)=", line):
            continue

        line = line.replace(" Span4Mux_s0_h ",   " Span4Mux_h4 "  if max_span_hack else " Span4Mux_h0 ")
        line = line.replace(" Span4Mux_s1_h ",   " Span4Mux_h4 "  if max_span_hack else " Span4Mux_h1 ")
        line = line.replace(" Span4Mux_s2_h ",   " Span4Mux_h4 "  if max_span_hack else " Span4Mux_h2 ")
        line = line.replace(" Span4Mux_s3_h ",   " Span4Mux_h4 "  if max_span_hack else " Span4Mux_h3 ")
        line = line.replace(" Span4Mux_h ",      " Span4Mux_h4 "  if max_span_hack else " Span4Mux_h4 ")

        line = line.replace(" Span4Mux_s0_v ",   " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v0 ")
        line = line.replace(" Span4Mux_s1_v ",   " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v1 ")
        line = line.replace(" Span4Mux_s2_v ",   " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v2 ")
        line = line.replace(" Span4Mux_s3_v ",   " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v3 ")
        line = line.replace(" Span4Mux_v ",      " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v4 ")
        line = line.replace(" Span4Mux ",        " Span4Mux_v4 "  if max_span_hack else " Span4Mux_v4 ")

        line = line.replace(" Span12Mux_s0_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h0 ")
        line = line.replace(" Span12Mux_s1_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h1 ")
        line = line.replace(" Span12Mux_s2_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h2 ")
        line = line.replace(" Span12Mux_s3_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h3 ")
        line = line.replace(" Span12Mux_s4_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h4 ")
        line = line.replace(" Span12Mux_s5_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h5 ")
        line = line.replace(" Span12Mux_s6_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h6 ")
        line = line.replace(" Span12Mux_s7_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h7 ")
        line = line.replace(" Span12Mux_s8_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h8 ")
        line = line.replace(" Span12Mux_s9_h ",  " Span12Mux_h12 " if max_span_hack else " Span12Mux_h9 ")
        line = line.replace(" Span12Mux_s10_h ", " Span12Mux_h12 " if max_span_hack else " Span12Mux_h10 ")
        line = line.replace(" Span12Mux_s11_h ", " Span12Mux_h12 " if max_span_hack else " Span12Mux_h11 ")
        line = line.replace(" Span12Mux ",       " Span12Mux_h12 " if max_span_hack else " Span12Mux_h12 ")

        line = line.replace(" Span12Mux_s0_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v0 ")
        line = line.replace(" Span12Mux_s1_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v1 ")
        line = line.replace(" Span12Mux_s2_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v2 ")
        line = line.replace(" Span12Mux_s3_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v3 ")
        line = line.replace(" Span12Mux_s4_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v4 ")
        line = line.replace(" Span12Mux_s5_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v5 ")
        line = line.replace(" Span12Mux_s6_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v6 ")
        line = line.replace(" Span12Mux_s7_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v7 ")
        line = line.replace(" Span12Mux_s8_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v8 ")
        line = line.replace(" Span12Mux_s9_v ",  " Span12Mux_v12 " if max_span_hack else " Span12Mux_v9 ")
        line = line.replace(" Span12Mux_s10_v ", " Span12Mux_v12 " if max_span_hack else " Span12Mux_v10 ")
        line = line.replace(" Span12Mux_s11_v ", " Span12Mux_v12 " if max_span_hack else " Span12Mux_v11 ")
        line = line.replace(" Span12Mux_v ",     " Span12Mux_v12 " if max_span_hack else " Span12Mux_v12 ")

        f.write(line)

assert os.system("yosys -qp 'select -write %s.lc t:LogicCell40' %s_ref.v" % (sys.argv[1], sys.argv[1])) == 0
assert os.system(r"sed -i -r 's,.*/(.*)LC_(.*),equiv_add -try -cell \1LC_\2_gold lc40_\2_gate,' %s.lc" % sys.argv[1]) == 0

os.remove("%s.bin" % sys.argv[1])
os.remove("%s.vsb" % sys.argv[1])
os.remove("%s.glb" % sys.argv[1])
os.remove("%s.psb" % sys.argv[1])
os.remove("%s.sdf" % sys.argv[1])
shutil.rmtree("%s.tmp" % sys.argv[1])

