#!/usr/bin/env python3

import os, sys

device = "up5k"

# This script is designed to determine which DSPs have configuration bits
# not in their usual position, as in some cases DSP and IPConnect tiles have
# their config bits swapped

# Unfortunately, arbitrary configurations are not allowed by icecube, so
# we define a set that gives us maximum coverage (full coverage is not
# possible as one CBIT is never set)

allowed_configs = ["1110000010000001001110110", "0010000101000010111111111", "0001111000101100000000000"]

coverage = set()
for c in allowed_configs:
    for i in range(25):
        if c[i] == "1":
            coverage.add(i)

assert len(coverage) >= 24

def parse_exp(f):
    current_x = 0
    current_y = 0
    bits = set()
    for line in f:
        splitline = line.split(' ')
        if splitline[0].endswith("_tile"):
            current_x = int(splitline[1])
            current_y = int(splitline[2])
        elif splitline[0] == "IpConfig":
            if splitline[1][:5] == "CBIT_":
                bitidx = int(splitline[1][5:])
                bits.add((current_x, current_y, bitidx))    
    return bits
dsp_locs = [( 0, 5, 0), ( 0, 10, 0), ( 0, 15, 0), ( 0, 23, 0),
            (25, 5, 0), (25, 10, 0), (25, 15, 0), (25, 23, 0)]
            
dsp_data = {}

if not os.path.exists("./work_dsp_cbit"):
    os.mkdir("./work_dsp_cbit")

for loc in dsp_locs:
    x, y, z = loc
    missing_bits = set()
    new_bits = set()
    for config in allowed_configs:
        params = config[::-1]
        with open("./work_dsp_cbit/dsp_cbit.v","w") as f:
            print("""
            module top(input clk, input a, input b, input c, input d, output y);
            """, file=f)
            print("""
                SB_MAC16 #(
                    .C_REG(1'b%s),
                    .A_REG(1'b%s),
                    .B_REG(1'b%s),
                    .D_REG(1'b%s),
                    .TOP_8x8_MULT_REG(1'b%s),
                    .BOT_8x8_MULT_REG(1'b%s),
                    .PIPELINE_16x16_MULT_REG1(1'b%s),
                    .PIPELINE_16x16_MULT_REG2(1'b%s),
                    .TOPOUTPUT_SELECT(2'b%s),
                    .TOPADDSUB_LOWERINPUT(2'b%s),
                    .TOPADDSUB_UPPERINPUT(1'b%s),
                    .TOPADDSUB_CARRYSELECT(2'b%s),
                    .BOTOUTPUT_SELECT(2'b%s),
                    .BOTADDSUB_LOWERINPUT(2'b%s),
                    .BOTADDSUB_UPPERINPUT(1'b%s),
                    .BOTADDSUB_CARRYSELECT(2'b%s),
                    .MODE_8x8(1'b%s),
                    .A_SIGNED(1'b%s),
                    .B_SIGNED(1'b%s)
                ) dsp (
                    .CLK(clk),
                    .C(c),
                    .A(a),
                    .B(b),
                    .D(d),
                    .O(y)
                );"""
                % (
                params[0], params[1], params[2], params[3],
                params[4], params[5], params[6], params[7],
                params[8:10][::-1], params[10:12][::-1], params[12], params[13:15][::-1],
                params[15:17][::-1], params[17:19][::-1], params[19], params[20:22][::-1],
                params[22], params[23], params[24]), file=f)
            print("endmodule",file=f)
        with open("./work_dsp_cbit/dsp_cbit.pcf","w") as f:
            print("set_location dsp %d %d %d" % loc, file=f)
        retval = os.system("bash ../../icecube.sh -" + device + " ./work_dsp_cbit/dsp_cbit.v > ./work_dsp_cbit/icecube.log 2>&1")
        if retval != 0:
            sys.stderr.write('ERROR: icecube returned non-zero error code\n')
            sys.exit(1)
        retval = os.system("../../../icebox/icebox_explain.py ./work_dsp_cbit/dsp_cbit.asc > ./work_dsp_cbit/dsp_cbit.exp")
        if retval != 0:
            sys.stderr.write('ERROR: icebox_explain returned non-zero error code\n')
            sys.exit(1)
        bits = set()
        known = set()
        with open('./work_dsp_cbit/dsp_cbit.exp', 'r') as f:
            bits = parse_exp(f)
        for i in range(25):
            if params[i] == "1":
                exp_pos = (x, y + (i // 8), i % 8)
                if exp_pos not in bits:
                    missing_bits.add(exp_pos)
                else:
                    known.add(exp_pos)
        for bit in bits:
            if bit not in known:
                new_bits.add(bit)
    if len(missing_bits) > 0 or len(new_bits) > 0:
        print("DSP (%d, %d):" % (x, y))
        for bit in missing_bits:
            print("\tMissing (%d, %d, CBIT_%d)" % bit)
        for bit in new_bits:
            print("\tNew: (%d, %d, CBIT_%d)" % bit)
        dsp_data[loc] = (missing_bits, new_bits)
with open("dsp_cbits_%s.txt" % device, 'w') as f:
    for loc in dsp_data:
        x, y, z = loc
        missing_bits, new_bits = dsp_data[loc]
        print("DSP (%d, %d):" % (x, y), file=f)
        for bit in missing_bits:
            print("\tMissing (%d, %d, CBIT_%d)" % bit,file=f)
        for bit in new_bits:
            print("\tNew: (%d, %d, CBIT_%d)" % bit,file=f)
