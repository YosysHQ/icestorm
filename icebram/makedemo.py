#!/usr/bin/env python3

import numpy as np

while True:
    bram_width = 4 * np.random.randint(1, 9)
    bram_depth = 256 * np.random.randint(1, 9)
    numrports = np.random.randint(1, 5)
    if bram_width * bram_depth * numrports < 16*4096: break

with open("demo.v", "wt") as f:
    print("// bram_width = %d" % bram_width, file=f)
    print("// bram_depth = %d" % bram_depth, file=f)
    print("// numrports = %d" % numrports, file=f)
    print("module demo (", file=f)
    for i in range(numrports):
        print("  input [%d:0] raddr%d," % (np.ceil(np.log2(bram_depth))-1, i), file=f)
        print("  output reg [%d:0] rdata%d," % (bram_width-1, i), file=f)
    print("  input [%d:0] waddr," % (np.ceil(np.log2(bram_depth))-1), file=f)
    print("  input [%d:0] wdata," % (bram_width-1), file=f)
    print("  input wen, clk", file=f)
    print(");", file=f)
    print("  reg [%d:0] memory [0:%d];" % (bram_width-1, bram_depth-1), file=f)
    print("  initial $readmemh(\"demo_dat0.hex\", memory);", file=f)
    for i in range(numrports):
        print("  always @(posedge clk) rdata%d <= memory[raddr%d];" % (i, i), file=f)
    print("  always @(posedge clk) if (wen) memory[waddr] <= wdata;", file=f)
    print("endmodule", file=f)

with open("demo_tb.v", "wt") as f:
    print("module demo_tb;", file=f)
    print("  reg clk = 0;", file=f)
    print("  always #5 clk = ~clk;", file=f)
    print("  integer i, errcnt = 0;", file=f)
    print("  reg [%d:0] addr;" % (np.ceil(np.log2(bram_depth))-1), file=f)
    for i in range(numrports):
        print("  wire [%d:0] rdata%d;" % (bram_width-1, i), file=f)
    print("  reg [%d:0] refmem [0:%d];" % (bram_width-1, bram_depth-1), file=f)
    print("  initial $readmemh(\"demo_dat1.hex\", refmem);", file=f)
    print("  demo uut (", file=f)
    for i in range(numrports):
        print("    .raddr%d(addr+%d'd%d)," % (i, np.ceil(np.log2(bram_depth)), i), file=f)
        print("    .rdata%d(rdata%d)," % (i, i), file=f)
    print("    .wen(1'b0),", file=f)
    print("    .clk(clk)", file=f)
    print("  );", file=f)
    print("  initial begin", file=f)
    print("    repeat (10) @(negedge clk);", file=f)
    print("    for (i = 0; i < %d; i = i + %d) begin" % (bram_depth, numrports), file=f)
    print("      addr <= i;", file=f)
    print("      @(posedge clk);", file=f)
    print("      @(negedge clk);", file=f)
    for i in range(numrports):
        print("      if (i+%d < %d && refmem[i+%d] !== rdata%d) begin errcnt = errcnt+1; " % (i, bram_depth, i, i) +
                "$display(\"ERROR @%%x: %%0%dx != %%0%dx\", i+%d, refmem[i+%d], rdata%d); end" % (bram_width/4, bram_width/4, i, i, i), file=f)
    print("    end", file=f)
    print("    if (errcnt == 0)", file=f)
    print("      $display(\"All tests OK.\");", file=f)
    print("    else", file=f)
    print("      $display(\"Found %1d ERROR(s).\", errcnt);", file=f)
    print("    $finish;", file=f)
    print("  end", file=f)
    print("endmodule", file=f)

with open("demo_dat0.hex", "wt") as f:
    for i in range(bram_depth):
        print("%0*x" % (bram_width//4, np.random.randint(1 << bram_width)), file=f)

with open("demo_dat1.hex", "wt") as f:
    for i in range(bram_depth):
        print("%0*x" % (bram_width//4, np.random.randint(1 << bram_width)), file=f)

