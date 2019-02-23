#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

assert device_class in ["5k", "u4k"]

working_dir = "work_%s_dsp" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

def randbin(n):
    return  "".join([np.random.choice(["0", "1"]) for i in range(n)])

#Only certain combinations are allowed in icecube, list them here
#This is not a complete set, but enough to cover all bits except cbit13, which
#is not set in any allowed config (?)
allowed_configs = [("0010000010000001001110110", "SB_MAC16_MUL_U_8X8_ALL_PIPELINE"),
                   ("1110000010000001001110110", "SB_MAC16_MUL_S_8X8_ALL_PIPELINE"),
                   ("0010000010000001000000000", "SB_MAC16_MUL_U_8X8_BYPASS"),
                   ("1110000010000001000000000", "SB_MAC16_MUL_S_8X8_BYPASS"),
                   ("0000000011000001111110110", "SB_MAC16_MUL_U_16X16_ALL_PIPELINE"),
                   ("1100000011000001111110110", "SB_MAC16_MUL_S_16X16_ALL_PIPELINE"),
                   ("0000000011000001110000110", "SB_MAC16_MUL_U_16X16_IM_BYPASS"),
                   ("1100000011000001110000110", "SB_MAC16_MUL_S_16X16_IM_BYPASS"),
                   ("0000000011000001100000000", "SB_MAC16_MUL_U_16X16_BYPASS"),
                   ("1100000011000001100000000", "SB_MAC16_MUL_S_16X16_BYPASS"),
                   ("0010000101000010111111111", "SB_MAC16_MAC_U_8X8_ALL_PIPELINE"),
                   ("0010000101000010100001111", "SB_MAC16_MAC_U_8X8_IM_BYPASS"),
                   ("0010000101000010100000000", "SB_MAC16_MAC_U_8X8_BYPASS"),
                   ("0000001001100100111111111", "SB_MAC16_MAC_U_16X16_ALL_PIPELINE"),
                   ("0001001001100100111111111", "SB_MAC16_MAC_U_16X16_CASC_ALL_PIPELINE"),
                   ("0001101001100100111111111", "SB_MAC16_MAC_U_16X16_CIN_ALL_PIPELINE"),
                   ("0000001001100100110001111", "SB_MAC16_MAC_U_16X16_IM_BYPASS"),
                   ("0000001001100100100000000", "SB_MAC16_MAC_U_16X16_BYPASS"),
                   ("1100001001100100110001111", "SB_MAC16_MAC_S_16X16_IM_BYPASS"),
                   ("0010000001000000100001111", "SB_MAC16_ACC_U_16P16_ALL_PIPELINE"),
                   ("0010000001000000100000000", "SB_MAC16_ACC_U_16P16_BYPASS"),
                   ("0010000001100000100001111", "SB_MAC16_ACC_U_32P32_ALL_PIPELINE"),
                   ("0010000001100000100000000", "SB_MAC16_ACC_U_32P32_BYPASS"),
                   ("0010010001001000100001111", "SB_MAC16_ADS_U_16P16_ALL_PIPELINE"),
                   ("0010010000001000000000000", "SB_MAC16_ADS_U_16P16_BYPASS"),
                   ("0010010001101000100001111", "SB_MAC16_ADS_U_32P32_ALL_PIPELINE"),
                   ("0010010000101000000000000", "SB_MAC16_ADS_U_32P32_BYPASS"),
                   ("0010010101001010111111111", "SB_MAC16_MAS_U_8X8_ALL_PIPELINE")]


coverage = set()
for c in allowed_configs:
    cfg, name = c
    for i in range(25):
        if cfg[i] == "1":
            coverage.add(i)

assert len(coverage) >= 24

#print(len(coverage))
#print(coverage)

for idx in range(num):
    with open(working_dir + "/dsp_%02d.v" % idx, "w") as f:
        glbs = ["glb[%d]" % i for i in range(np.random.randint(8)+1)]
        
        config = allowed_configs[np.random.randint(len(allowed_configs))]
        params, cfgname = config
        with open(working_dir + "/dsp_%02d.dsp" % idx, "w") as dspf:
            dspf.write(cfgname + "\n")
        params = params[::-1]
        
        # TODO: ce should be on this list, but causes routing failures
        glbs_choice = ["clk", "a", "b", "c", "d,", "ah", "bh", "ch", "dh", "irt", "irb", "ort", "orb", "olt", "olb", "ast", "asb", "oht", "ohb", "sei"]
        print("""
            module top (
                input  [%d:0] glb_pins,
                input  [%d:0] in_pins,
                output [15:0] out_pins
            );
            wire [%d:0] glb, glb_pins;
            SB_GB gbufs [%d:0] (
                .USER_SIGNAL_TO_GLOBAL_BUFFER(glb_pins),
                .GLOBAL_BUFFER_OUTPUT(glb)
            );
        """ % (len(glbs)-1, len(pins) - len(glbs) - 16 - 1, len(glbs)-1, len(glbs)-1), file=f)
        bits = ["in_pins[%d]" % i for i in range(100)]
        bits = list(np.random.permutation(bits))
        for i in range(num_dsp):
            tmp = list(np.random.permutation(bits))
            bits_c          = [tmp.pop() for k in range(16)]
            bits_a          = [tmp.pop() for k in range(16)]
            bits_b          = [tmp.pop() for k in range(16)]
            bits_d          = [tmp.pop() for k in range(16)]
            bit_ce          = tmp.pop()
            bit_clk         = tmp.pop()
            bit_ahold       = tmp.pop()
            bit_bhold       = tmp.pop()
            bit_chold       = tmp.pop()
            bit_dhold       = tmp.pop()
            bit_irsttop     = tmp.pop()
            bit_irstbot     = tmp.pop()
            bit_orsttop     = tmp.pop()
            bit_orstbot     = tmp.pop()
            bit_oloadtop    = tmp.pop()
            bit_oloadbot    = tmp.pop()
            bit_addsubtop   = tmp.pop()
            bit_addsubbot   = tmp.pop()
            bit_oholdtop    = tmp.pop()
            bit_oholdbot    = tmp.pop()
            
            aci_opts = ["1'b0"]
            if i > 0 and i % 4 != 0:
                aci_opts.append("out_%d[33]" % (i-1));
            sei_opts = ["1'b0"]
            if i > 0 and i % 4 != 0:
                sei_opts.append("out_%d[34]" % (i - 1));
                                
            bit_ci          = tmp.pop()
            bit_accumci     = np.random.choice(aci_opts)
            bit_signextin   = np.random.choice(sei_opts)

            if len(glbs) != 0:
                s = np.random.choice(glbs_choice)
                glbs_choice.remove(s)
                if s == "clk":      bit_clk         = glbs.pop()
                if s == "a":        bits_a[np.random.randint(len(bits_a))] = glbs.pop()
                if s == "b":        bits_b[np.random.randint(len(bits_b))] = glbs.pop()
                if s == "c":        bits_c[np.random.randint(len(bits_c))] = glbs.pop()
                if s == "d":        bits_d[np.random.randint(len(bits_d))] = glbs.pop()
                if s == "ah":       bit_ahold       = glbs.pop()
                if s == "bh":       bit_bhold       = glbs.pop()
                if s == "ch":       bit_chold       = glbs.pop()
                if s == "dh":       bit_dhold       = glbs.pop()
                if s == "irt":      bit_irsttop     = glbs.pop()
                if s == "irb":      bit_irstbot     = glbs.pop()
                if s == "ort":      bit_orsttop     = glbs.pop()
                if s == "orb":      bit_orstbot     = glbs.pop()
                if s == "olt":      bit_oloadtop    = glbs.pop()
                if s == "olb":      bit_oloadbot    = glbs.pop()
                if s == "ast":      bit_addsubtop   = glbs.pop()
                if s == "asb":      bit_addsubbot   = glbs.pop()
                if s == "oht":      bit_oholdtop    = glbs.pop()
                if s == "ohb":      bit_oholdbot    = glbs.pop()
                if s == "ci":       bit_ci          = glbs.pop()
                

            bits_a = "{%s}" % ", ".join(bits_a)
            bits_b = "{%s}" % ", ".join(bits_b)
            bits_c = "{%s}" % ", ".join(bits_c)
            bits_d = "{%s}" % ", ".join(bits_d)

            negclk = randbin(1)
            
            print("""
                wire [34:0] out_%d;
                SB_MAC16 #(
                    .NEG_TRIGGER(1'b%s),
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
                ) dsp_%d (
                    .CLK(%s),
                    .CE(%s),
                    .C(%s),
                    .A(%s),
                    .B(%s),
                    .D(%s),
                    .AHOLD(%s),
                    .BHOLD(%s),
                    .CHOLD(%s),
                    .DHOLD(%s),
                    .IRSTTOP(%s),
                    .IRSTBOT(%s),
                    .ORSTTOP(%s),
                    .ORSTBOT(%s),
                    .OLOADTOP(%s),
                    .OLOADBOT(%s),
                    .ADDSUBTOP(%s),
                    .ADDSUBBOT(%s),
                    .OHOLDTOP(%s),
                    .OHOLDBOT(%s),
                    .CI(%s),
                    .ACCUMCI(%s),
                    .SIGNEXTIN(%s),
                    .O(out_%d[31:0]),
                    .CO(out_%d[32]),
                    .ACCUMCO(out_%d[33]),
                    .SIGNEXTOUT(out_%d[34])
                );"""
            % (
                i,
                negclk,
                params[0], params[1], params[2], params[3],
                params[4], params[5], params[6], params[7],
                params[8:10][::-1], params[10:12][::-1], params[12], params[13:15][::-1],
                params[15:17][::-1], params[17:19][::-1], params[19], params[20:22][::-1],
                params[22], params[23], params[24],
                i,
                bit_clk, bit_ce, bits_c, bits_a, bits_b, bits_d,
                bit_ahold, bit_bhold, bit_chold, bit_dhold,
                bit_irsttop, bit_irstbot, bit_orsttop, bit_orstbot,
                bit_oloadtop, bit_oloadbot, bit_addsubtop, bit_addsubbot,
                bit_oholdtop, bit_oholdbot,
                bit_ci, bit_accumci, bit_signextin,
                i, i, i, i
            ), file=f)
            bits = list(np.random.permutation(bits))
            for k in range(33):
                bits[k] = "out_%d[%d] ^ %s" % (i, k, bits[k])
        for k in range(16):
           print("assign out_pins[%d] = out_%d[%d] ^ out_%d[%d];" % (k, i, np.random.randint(33), i, np.random.randint(33)), file=f)
        print("endmodule", file=f)
    with open(working_dir + "/dsp_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for i in range(len(pins) - len(glbs) - 16):
            print("set_io in_pins[%d] %s" % (i, p.pop()), file=f)
        for i in range(16):
            print("set_io out_pins[%d] %s" % (i, p.pop()), file=f)


output_makefile(working_dir, "dsp")
