#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

assert device_class == "5k"

working_dir = "work_%s_upip" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)
def randbin(n):
    return  "".join([np.random.choice(["0", "1"]) for i in range(n)])
for idx in range(num):
    with open(working_dir + "/upip_%02d.v" % idx, "w") as f:
        glbs = ["glb[%d]" % i for i in range(np.random.randint(6)+1)]

        print("""
            module top (
                input  [%d:0] glb_pins,
                input  [%d:0] in_pins,
                output [15:0] out_pins,
                output [%d:0] led_pins
            );
            wire [%d:0] glb, glb_pins;
            SB_GB gbufs [%d:0] (
                .USER_SIGNAL_TO_GLOBAL_BUFFER(glb_pins),
                .GLOBAL_BUFFER_OUTPUT(glb)
            );
        """ % (len(glbs)-1, len(pins) - len(glbs) - 16 - 1, len(led_pins)-1, len(glbs)-1, len(glbs)-1), file=f)
        bits = ["in_pins[%d]" % (i % (len(pins) - len(glbs) - 16 - 1)) for i in range(60)]
        bits = list(np.random.permutation(bits))    
        #Internal oscillators
        tmp =  ["in_pins[%d]" % i for i in range(len(pins) - len(glbs) - 16 - 1)]
        tmp = list(np.random.permutation(tmp))
        for osc in ["LF", "HF"]:
            bit_pu = tmp.pop()
            bit_en = tmp.pop()
            bit_clk = "clk_" + osc
            glbs.append(bit_clk)
            param = ""
            if osc == "HF": #only HFOSC has a divider:
                param = "#(.CLKHF_DIV(\"0b%s\"))" % randbin(2) 
            
            route = np.random.choice(["", "/* synthesis ROUTE_THROUGH_FABRIC = 1 */"])
            
            print("""
                SB_%sOSC %s osc_%s (
                    .CLK%sPU(%s),
                    .CLK%sEN(%s),
                    .CLK%s(%s)
                ) %s;
            """ % (
                osc, param, osc, osc, bit_pu,
                osc, bit_en, osc, bit_clk, route
            ), file=f)
        glbs_orig = list(glbs)
        #256k SPRAM blocks    
        for i in range(num_spram256ka):
            tmp = list(np.random.permutation(bits))
        
            bits_addr       = [tmp.pop() for k in range(14)]
            bits_mask       = [tmp.pop() for k in range(4)]
            bits_wdata      = [tmp.pop() for k in range(16)]
            bit_wren        = tmp.pop()
            bit_cs          = tmp.pop()
            bit_clock       = tmp.pop()
            bit_standby     = tmp.pop()
            bit_sleep       = tmp.pop()
            bit_poweroff    = tmp.pop()
            
            glbs_choice = ["clk", "a", "msk", "wd", "we", "cs", "stb", "slp", "po"]
            
            if len(glbs) != 0:
                s = np.random.choice(glbs_choice)
                glbs_choice.remove(s)
                if s == "clk":  bit_clock       = glbs.pop()
                if s == "a":    bits_addr[np.random.randint(len(bits_addr))] = glbs.pop()
                if s == "msk":  bits_mask [np.random.randint(len(bits_mask ))] = glbs.pop()
                if s == "wd":   bits_wdata[np.random.randint(len(bits_wdata))] = glbs.pop()
                if s == "we":   bit_wren        = glbs.pop()
                if s == "cs":   bit_cs          = glbs.pop()
                if s == "stb":  bit_standby     = glbs.pop()
                if s == "slp":  bit_sleep       = glbs.pop()
                if s == "po":   bit_poweroff    = glbs.pop()
            bits_addr = "{%s}" % ", ".join(bits_addr)
            bits_mask  = "{%s}" % ", ".join(bits_mask)
            bits_wdata = "{%s}" % ", ".join(bits_wdata)

            print("""
                wire [15:0] rdata_%d;
                SB_SPRAM256KA spram_%d (
                    .ADDRESS(%s),
                    .DATAIN(%s),
                    .MASKWREN(%s),
                    .WREN(%s),
                    .CHIPSELECT(%s),
                    .CLOCK(%s),
                    .STANDBY(%s),
                    .SLEEP(%s),
                    .POWEROFF(%s),
                    .DATAOUT(rdata_%d)
                );
            """ % (
                i, i,
                bits_addr, bits_wdata, bits_mask, bit_wren, 
                bit_cs, bit_clock, bit_standby, bit_sleep,
                bit_poweroff, i
            ), file=f)
            bits = list(np.random.permutation(bits))
            if np.random.choice(["XOR", "MULT"]) == "MULT":
                #stress routing at sides more with a multiply
                print("""
                wire [31:0] mult_res_%d;
                assign mult_res_%d = rdata_%d * %s;
                """ % (
                    i, i, i, ("{%s}" % ", ".join(bits[0:32]))
                ), file=f)
                for k in range(32):
                    bits[k] = "mult_res_%d[%d]" % (i, k)
            else:
                for k in range(16):
                    bits[k] = "rdata_%d[%d] ^ %s" % (i, k, bits[k])
        
        # Internal PWM IP
        tmp = list(np.random.permutation(bits))
        glbs = list(glbs_orig)
        bit_cs = tmp.pop()
        bit_clk = np.random.choice([glbs.pop(), tmp.pop()])
        bit_rst = np.random.choice([glbs.pop(), tmp.pop()])
        bit_den = tmp.pop()
        bit_exe = tmp.pop()
        
        bits_dat = [tmp.pop() for k in range(8)] 
        bits_addr = [tmp.pop() for k in range(4)] 

        print("""
            wire [2:0] pwm_out;
            SB_LEDDA_IP ledda (
                .LEDDCS(%s),
                .LEDDCLK(%s),
                .LEDDDAT7(%s),
                .LEDDDAT6(%s),
                .LEDDDAT5(%s),
                .LEDDDAT4(%s),
                .LEDDDAT3(%s),
                .LEDDDAT2(%s),
                .LEDDDAT1(%s),
                .LEDDDAT0(%s),
                .LEDDADDR3(%s),
                .LEDDADDR2(%s),
                .LEDDADDR1(%s),
                .LEDDADDR0(%s),
                .LEDDDEN(%s),
                .LEDDEXE(%s),
                .LEDDRST(%s),
                .PWMOUT0(pwm_out[0]),
                .PWMOUT1(pwm_out[1]),
                .PWMOUT2(pwm_out[2])
            );
        """ % (
        bit_cs, bit_clk, bits_dat[7], bits_dat[6], bits_dat[5], bits_dat[4],
        bits_dat[3], bits_dat[2], bits_dat[1], bits_dat[0], bits_addr[3],
        bits_addr[2], bits_addr[1], bits_addr[0], bit_den, bit_exe, bit_rst
        ), file=f)        
        
        bits.append("pwm_out[0]")
        bits.append("pwm_out[1]")
        bits.append("pwm_out[2]")

        # Constant current LED driver
        current_choices = ["0b000000", "0b000001", "0b000011", "0b000111", "0b001111", "0b011111", "0b111111"]
        current_modes = ["0b0", "0b1"]
        
        currents = [np.random.choice(current_choices) for i in range(3)]
        
        bit_curren = np.random.choice(bits)
        bit_rgbleden = np.random.choice(bits)
        bits_pwm = [np.random.choice([np.random.choice(bits), "pwm_out[%d]" % i]) for i in range(3)]

        print("""
            SB_RGBA_DRV #(
                .CURRENT_MODE(\"%s\"),
                .RGB0_CURRENT(\"%s\"),
                .RGB1_CURRENT(\"%s\"),
                .RGB2_CURRENT(\"%s\")
            ) rgba_drv (
                .CURREN(%s),
                .RGBLEDEN(%s),
                .RGB0PWM(%s),
                .RGB1PWM(%s),
                .RGB2PWM(%s),
                .RGB0(led_pins[0]),
                .RGB1(led_pins[1]),
                .RGB2(led_pins[2])
            );
        """ % (
            np.random.choice(current_modes), currents[0], currents[1], currents[2],
            bit_curren, bit_rgbleden, bits_pwm[0], bits_pwm[1], bits_pwm[2]
        ), file = f)
        
        # TODO: I2C and SPI
        
        print("assign out_pins = rdata_%d;" % i, file=f)
        print("endmodule", file=f)
    with open(working_dir + "/upip_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for i in range(len(pins) - len(glbs) - 16):
            print("set_io in_pins[%d] %s" % (i, p.pop()), file=f)
        for i in range(16):
            print("set_io out_pins[%d] %s" % (i, p.pop()), file=f)
        for i in range(len(led_pins)):
            print("set_io led_pins[%d] %s" % (i, led_pins[i]), file=f)

output_makefile(working_dir, "upip")
