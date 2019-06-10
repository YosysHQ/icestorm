#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

device_class = os.getenv("ICEDEVICE")

assert device_class == "u4k"

working_dir = "work_%s_uip" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)
def randbin(n):
    return  "".join([np.random.choice(["0", "1"]) for i in range(n)])
for idx in range(num):
    with open(working_dir + "/uip_%02d.v" % idx, "w") as f:
        glbs = ["glb[%d]" % i for i in range(np.random.randint(6)+1)]

        print("""
            module top (
                input  [%d:0] glb_pins,
                input  [%d:0] in_pins,
                input   [2:0] led_data,
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

        # tmp = list(np.random.permutation(bits))
        # glbs = list(glbs_orig)

        # bit_clk = np.random.choice([glbs.pop(), tmp.pop()])
        # bit_rst = np.random.choice([glbs.pop(), tmp.pop()])
        # bit_paramsok = tmp.pop()
        # bits_color = [tmp.pop() for k in range(4)]
        # bits_bright = [tmp.pop() for k in range(4)]
        # bits_ramp = [tmp.pop() for k in range(4)]
        # bits_rate = [tmp.pop() for k in range(4)]

        # print("""
		# 	wire [2:0] pwm_out;
		# 	SB_RGB_IP rgb_ip (
		# 		.CLK(%s),
		# 		.RST(%s),
		# 		.PARAMSOK(%s),
		# 		.RGBCOLOR({%s,%s,%s,%s}),
		# 		.BRIGHTNESS({%s,%s,%s,%s}),
		# 		.BREATHRAMP({%s,%s,%s,%s}),
		# 		.BLINKRATE({%s,%s,%s,%s}),
		# 		.REDPWM(pwm_out[0]),
		# 		.GREENPWM(pwm_out[1]),
		# 		.BLUEPWM(pwm_out[2])
		# 	);
		# """ % (
        #     bit_clk, bit_rst, bit_paramsok, *bits_color, *bits_bright, *bits_ramp, *bits_rate
		# ), file=f)

        # bits.append("pwm_out[0]")
        # bits.append("pwm_out[1]")
        # bits.append("pwm_out[2]")

        current_choices = ["0b000000", "0b000001", "0b000011", "0b000111", "0b001111", "0b011111", "0b111111"]

        currents = [np.random.choice(current_choices) for i in range(3)]

        bit_curren = np.random.choice(bits)
        bit_rgbleden = np.random.choice(bits)
        bits_pwm = [np.random.choice([np.random.choice(bits), "led_data[%d]" % i]) for i in range(3)]

        print("""
			wire rgbpu;
			SB_LED_DRV_CUR led_drv_cur (
				.EN(%s),
				.LEDPU(rgbpu)
			);

            SB_RGB_DRV #(
                .RGB0_CURRENT(\"%s\"),
                .RGB1_CURRENT(\"%s\"),
                .RGB2_CURRENT(\"%s\")
            ) rgb_drv (
                .RGBLEDEN(%s),
                .RGBPU(rgbpu),
                .RGB0PWM(%s),
                .RGB1PWM(%s),
                .RGB2PWM(%s),
                .RGB0(led_pins[0]),
                .RGB1(led_pins[1]),
                .RGB2(led_pins[2])
            );
        """ % (
            bit_curren, currents[0], currents[1], currents[2],
            bit_rgbleden, bits_pwm[0], bits_pwm[1], bits_pwm[2]
        ), file = f)

        # TODO: I2C and SPI

        print("endmodule", file=f)
    with open(working_dir + "/uip_%02d.pcf" % idx, "w") as f:
        p = list(np.random.permutation(pins))
        for i in range(len(pins) - len(glbs) - 16):
            print("set_io in_pins[%d] %s" % (i, p.pop()), file=f)
        for i in range(len(led_pins)):
            print("set_io led_pins[%d] %s" % (i, led_pins[i]), file=f)

output_makefile(working_dir, "uip")
