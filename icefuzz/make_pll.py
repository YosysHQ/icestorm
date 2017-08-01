#!/usr/bin/env python3

from fuzzconfig import *
import numpy as np
import os

from numpy.random import randint, choice, permutation

def randbin(n):
    return  "".join([choice(["0", "1"]) for i in range(n)])

for p in gpins:
    if p in pins: pins.remove(p)

device_class = os.getenv("ICEDEVICE")

working_dir = "work_%s_pll" % (device_class, )

os.system("rm -rf " + working_dir)
os.mkdir(working_dir)

for idx in range(num):
    pin_names = list()
    vlog_body = list()
    pll_inst = list()

    pll_type = choice(["SB_PLL40_CORE", "SB_PLL40_2F_CORE", "SB_PLL40_PAD", "SB_PLL40_2_PAD", "SB_PLL40_2F_PAD"])

    pll_inst.append("%s uut (" % pll_type)

    if pll_type.endswith("_PAD"):
        pin_names.append("packagepin")
        vlog_body.append("input packagepin;")
        pll_inst.append("  .PACKAGEPIN(packagepin),")
    else:
        pin_names.append("referenceclk")
        vlog_body.append("input referenceclk;")
        pll_inst.append("  .REFERENCECLK(referenceclk),")

    for pin in ["a", "b"]:
        pin_names.append(pin)
        vlog_body.append("input %s;" % pin)

    for pin in ["w", "x", "y", "z"]:
        pin_names.append(pin)
        vlog_body.append("output %s%s;" % ("reg " if pin in ["y", "z"] else "", pin))

    for pin in ["EXTFEEDBACK", "BYPASS", "RESETB", "LOCK", "LATCHINPUTVALUE", "SDI", "SDO", "SCLK"]:
        pin_names.append(pin.lower())
        vlog_body.append("%sput %s;" % ("out" if pin in ["LOCK", "SDO"] else "in", pin.lower()))
        pll_inst.append("  .%s(%s)," % (pin, pin.lower()))

    if pll_type.find("_2_") < 0 and pll_type.find("_2F_") < 0:
        for pin in ["PLLOUTCORE", "PLLOUTGLOBAL"]:
            vlog_body.append("wire %s;" % pin.lower())
            pll_inst.append("  .%s(%s)," % (pin, pin.lower()))
        vlog_body.append("assign w = plloutcore ^ a;")
        vlog_body.append("assign x = plloutcore ^ b;")
        vlog_body.append("always @(posedge plloutglobal) y <= a;")
        vlog_body.append("always @(posedge plloutglobal) z <= b;")
    else:
        for pin in ["PLLOUTCOREA", "PLLOUTCOREB", "PLLOUTGLOBALA", "PLLOUTGLOBALB"]:
            vlog_body.append("wire %s;" % pin.lower())
            pll_inst.append("  .%s(%s)," % (pin, pin.lower()))
        vlog_body.append("assign w = plloutcorea ^ a;")
        vlog_body.append("assign x = plloutcoreb ^ b;")
        vlog_body.append("always @(posedge plloutglobala) y <= a;")
        vlog_body.append("always @(posedge plloutglobalb) z <= b;")

    for i in range(8):
        pin_names.append("dynamicdelay_%d" % i)
        vlog_body.append("input dynamicdelay_%d;" % i)
    pll_inst.append("  .DYNAMICDELAY({%s})" % ", ".join(["dynamicdelay_%d" % i for i in range(7, -1, -1)]))
    pll_inst.append(");")

    divq = randbin(3)
    if divq == "000": divq = "001"
    if divq == "111": divq = "110"
    pll_inst.append("defparam uut.DIVR = 4'b%s;" % randbin(4))
    pll_inst.append("defparam uut.DIVF = 7'b%s;" % randbin(7))
    pll_inst.append("defparam uut.DIVQ = 3'b%s;" % divq)
    pll_inst.append("defparam uut.FILTER_RANGE = 3'b%s;" %  randbin(3))
    pll_inst.append("defparam uut.FEEDBACK_PATH = \"%s\";" % choice(["DELAY", "SIMPLE", "PHASE_AND_DELAY", "EXTERNAL"]))

    if choice([True, False]):
        pll_inst.append("defparam uut.DELAY_ADJUSTMENT_MODE_FEEDBACK = \"FIXED\";")
        pll_inst.append("defparam uut.FDA_FEEDBACK = 4'b%s;" %  randbin(4))
    else:
        pll_inst.append("defparam uut.DELAY_ADJUSTMENT_MODE_FEEDBACK = \"DYNAMIC\";")
        pll_inst.append("defparam uut.FDA_FEEDBACK = 4'b1111;")

    if choice([True, False]):
        pll_inst.append("defparam uut.DELAY_ADJUSTMENT_MODE_RELATIVE = \"FIXED\";")
        pll_inst.append("defparam uut.FDA_RELATIVE = 4'b%s;" %  randbin(4))
    else:
        pll_inst.append("defparam uut.DELAY_ADJUSTMENT_MODE_RELATIVE = \"DYNAMIC\";")
        pll_inst.append("defparam uut.FDA_RELATIVE = 4'b1111;")

    pll_inst.append("defparam uut.SHIFTREG_DIV_MODE = 1'b%s;" %  randbin(1))

    if pll_type.find("_2_") < 0 and pll_type.find("_2F_") < 0:
        pll_inst.append("defparam uut.PLLOUT_SELECT = \"%s\";" % choice(["GENCLK", "GENCLK_HALF", "SHIFTREG_90deg", "SHIFTREG_0deg"]))
    elif pll_type.find("_2F_") < 0:
        pll_inst.append("defparam uut.PLLOUT_SELECT_PORTB = \"%s\";" % choice(["GENCLK", "GENCLK_HALF", "SHIFTREG_90deg", "SHIFTREG_0deg"]))
    else:
        pll_inst.append("defparam uut.PLLOUT_SELECT_PORTA = \"%s\";" % choice(["GENCLK", "GENCLK_HALF", "SHIFTREG_90deg", "SHIFTREG_0deg"]))
        pll_inst.append("defparam uut.PLLOUT_SELECT_PORTB = \"%s\";" % choice(["GENCLK", "GENCLK_HALF", "SHIFTREG_90deg", "SHIFTREG_0deg"]))

    if pll_type.find("_2_") < 0 and pll_type.find("_2F_") < 0:
        pll_inst.append("defparam uut.ENABLE_ICEGATE = 1'b0;")
    else:
        pll_inst.append("defparam uut.ENABLE_ICEGATE_PORTA = 1'b0;")
        pll_inst.append("defparam uut.ENABLE_ICEGATE_PORTB = 1'b0;")

    pll_inst.append("defparam uut.TEST_MODE = 1'b0;")

    with open(working_dir + "/pll_%02d.v" % idx, "w") as f:
        print("module top(%s);" % ", ".join(pin_names), file=f)
        print("\n".join(vlog_body), file=f)
        print("\n".join(pll_inst), file=f)
        print("endmodule", file=f)

    with open(working_dir + "/pll_%02d.pcf" % idx, "w") as f:
        for pll_pin, package_pin in zip(pin_names, list(permutation(pins))[0:len(pin_names)]):
            if pll_pin == "packagepin": package_pin = "49"
            print("set_io %s %s" % (pll_pin, package_pin), file=f)


output_makefile(working_dir, "pll")

