#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

os.system("rm -rf work_ram40")
os.mkdir("work_ram40")

for idx in range(num):
    with open("work_ram40/ram40_%02d.v" % idx, "w") as f:
        glbs = ["glb[%d]" % i for i in range(np.random.randint(9))]
        glbs_choice = ["wa", "ra", "msk", "wd", "we", "wce", "wc", "re", "rce", "rc"]
        print("""
            module top (
                input  [%d:0] glb_pins,
                input  [59:0] in_pins,
                output [15:0] out_pins
            );
            wire [%d:0] glb, glb_pins;
            SB_GB gbufs [%d:0] (
                .USER_SIGNAL_TO_GLOBAL_BUFFER(glb_pins),
                .GLOBAL_BUFFER_OUTPUT(glb)
            );
        """ % (len(glbs)-1, len(glbs)-1, len(glbs)-1), file=f)
        bits = ["in_pins[%d]" % i for i in range(60)]
        bits = list(np.random.permutation(bits))
        for i in range(num_ramb40):
            tmp = list(np.random.permutation(bits))
            rmode = np.random.randint(4)
            if rmode == 3:
                wmode = np.random.randint(1, 4)
            else:
                wmode = np.random.randint(4)
            raddr_bits = (8, 9, 10, 11)[rmode]
            waddr_bits = (8, 9, 10, 11)[wmode]
            rdata_bits = (16, 8, 4, 2)[rmode]
            wdata_bits = (16, 8, 4, 2)[wmode]
            bits_waddr = [tmp.pop() for k in range(waddr_bits)]
            bits_raddr = [tmp.pop() for k in range(raddr_bits)]
            bits_mask  = [tmp.pop() for k in range(16)]
            bits_wdata = [tmp.pop() for k in range(wdata_bits)]
            bit_we     = tmp.pop()
            bit_wclke  = tmp.pop()
            bit_wclk   = tmp.pop()
            bit_re     = tmp.pop()
            bit_rclke  = tmp.pop()
            bit_rclk   = tmp.pop()
            if len(glbs) != 0:
                s = np.random.choice(glbs_choice)
                glbs_choice.remove(s)
                if s == "wa":  bits_waddr[np.random.randint(len(bits_waddr))] = glbs.pop()
                if s == "ra":  bits_raddr[np.random.randint(len(bits_raddr))] = glbs.pop()
                if s == "msk": bits_mask [np.random.randint(len(bits_mask ))] = glbs.pop()
                if s == "wd":  bits_wdata[np.random.randint(len(bits_wdata))] = glbs.pop()
                if s == "we":  bit_we    = glbs.pop()
                if s == "wce": bit_wclke = glbs.pop()
                if s == "wc":  bit_wclk  = glbs.pop()
                if s == "re":  bit_re    = glbs.pop()
                if s == "rce": bit_rclke = glbs.pop()
                if s == "rc":  bit_rclk  = glbs.pop()
            bits_waddr = "{%s}" % ", ".join(bits_waddr)
            bits_raddr = "{%s}" % ", ".join(bits_raddr)
            bits_mask  = "{%s}" % ", ".join(bits_mask)
            bits_wdata = "{%s}" % ", ".join(bits_wdata)
            if wmode != 0: bits_mask = ""
            memtype = np.random.choice(["", "NR", "NW", "NRNW"])
            wclksuffix = "N" if memtype in ["NW", "NRNW"] else ""
            rclksuffix = "N" if memtype in ["NR", "NRNW"] else ""
            print("""
                wire [%d:0] rdata_%d;
                SB_RAM40_4K%s #(
                    .READ_MODE(%d),
                    .WRITE_MODE(%d)
                ) ram_%d (
                    .WADDR(%s),
                    .RADDR(%s),
                    .MASK(%s),
                    .WDATA(%s),
                    .RDATA(rdata_%d),
                    .WE(%s),
                    .WCLKE(%s),
                    .WCLK%s(%s),
                    .RE(%s),
                    .RCLKE(%s),
                    .RCLK%s(%s)
                );
            """ % (
                rdata_bits-1, i, memtype, rmode, wmode, i,
                bits_waddr, bits_raddr, bits_mask, bits_wdata, i,
                bit_we, bit_wclke, wclksuffix, bit_wclk,
                bit_re, bit_rclke, rclksuffix, bit_rclk
            ), file=f)
            bits = list(np.random.permutation(bits))
            for k in range(rdata_bits):
                bits[k] = "rdata_%d[%d] ^ %s" % (i, k, bits[k])
        print("assign out_pins = rdata_%d;" % i, file=f)
        print("endmodule", file=f)
    with open("work_ram40/ram40_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for i in range(60):
            print("set_io in_pins[%d] %s" % (i, p.pop()), file=f)
        for i in range(16):
            print("set_io out_pins[%d] %s" % (i, p.pop()), file=f)

with open("work_ram40/Makefile", "w") as f:
    print("all: %s" % " ".join(["ram40_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("ram40_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh ram40_%02d > ram40_%02d.log 2>&1 && rm -rf ram40_%02d.tmp || tail ram40_%02d.log" % (i, i, i, i), file=f)

