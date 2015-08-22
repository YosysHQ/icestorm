#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

from numpy.random import randint, choice, permutation

num_xor = 8
num_luts = 8
num_outputs_range = (5, 20)

os.system("rm -rf work_iopack")
os.mkdir("work_iopack")

def get_pin_directions():
    pindirs = ["i" for i in range(len(pins))]
    for i in range(randint(num_outputs_range[0], num_outputs_range[1])):
        pindirs[randint(len(pins))] = "o"
    return pindirs

def get_nearby_inputs(p, n, r):
    while True:
        ipins = list()
        for i in range(-r, +r):
            ip = (p + i + len(pins)) % len(pins)
            if pindirs[ip] == "i":
                ipins.append(ip)
        if len(ipins) >= n:
            break
        r += 4
    return [choice(ipins) for i in range(n)]

for idx in range(num):
    with open("work_iopack/iopack_%02d.v" % idx, "w") as f:
        pindirs = get_pin_directions()
        print("module top(%s);" % ", ".join(["%sput p%d" % ("in" if pindirs[i] == "i" else "out", i) for i in range(len(pins))]), file=f)
        for outp in range(len(pins)):
            if pindirs[outp] == "o":
                xor_nets = set(["%sp%d" % (choice(["~", ""]), p) for p in get_nearby_inputs(outp, num_xor, 2 + randint(10))])
                for i in range(num_luts):
                    print("  localparam [15:0] p%d_lut%d = 16'd %d;" % (outp, i, randint(2**16)), file=f)
                    print("  wire p%d_in%d = p%d_lut%d >> {%s};" % (outp, i, outp, i,
                            ", ".join(["p%d" % p for p in get_nearby_inputs(outp + randint(-10, +11), 4, 4)])), file=f)
                    xor_nets.add("%sp%d_in%d" % (choice(["~", ""]), outp, i))
                print("  assign p%d = ^{%s};" % (outp, ", ".join(sorted(xor_nets))), file=f)
        print("endmodule", file=f)
    with open("work_iopack/iopack_%02d.pcf" % idx, "w") as f:
        for i in range(len(pins)):
            print("set_io p%d %s" % (i, pins[i]), file=f)

with open("work_iopack/Makefile", "w") as f:
    print("all: %s" % " ".join(["iopack_%02d.bin" % i for i in range(num)]), file=f)
    for i in range(num):
        print("iopack_%02d.bin:" % i, file=f)
        print("\t-bash ../icecube.sh iopack_%02d > iopack_%02d.log 2>&1 && rm -rf iopack_%02d.tmp || tail iopack_%02d.log" % (i, i, i, i), file=f)

