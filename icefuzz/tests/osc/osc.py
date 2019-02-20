#!/usr/bin/env python3

import os, sys

device = "u4k"

if not os.path.exists("./work_osc"):
    os.mkdir("./work_osc")

def run(route_fabric):
    name = "./work_osc/osc_cbit_fabric_%d" % route_fabric
    with open(name+'.v',"w") as f:
        print("""
    module top(
        input clkhfpu,
        input clkhfen,
        input clklfpu,
        input clklfen,
        output pin,
        output pin2,
        input data
        );

    wire clkhf;
    SB_HFOSC #(
        .CLKHF_DIV("%s")
    ) hfosc (
        .CLKHFPU(clkhfpu),
        .CLKHFEN(clkhfen),
        .CLKHF(clkhf)
    ); /* synthesis ROUTE_THROUGH_FABRIC = %d */

    SB_IO #(
        .PIN_TYPE(6'b 0101_00)
    ) pin_obuf (
        .PACKAGE_PIN(pin),
        .OUTPUT_CLK(clkhf),
        .D_OUT_0(data)
    );

    wire clklf;
    SB_LFOSC lfosc (
        .CLKLFPU(clklfpu),
        .CLKLFEN(clklfen),
        .CLKLF(clklf)
    ); /* synthesis ROUTE_THROUGH_FABRIC = %d */

    SB_IO #(
        .PIN_TYPE(6'b 0101_00)
    ) pin2_obuf (
        .PACKAGE_PIN(pin2),
        .OUTPUT_CLK(clklf),
        .D_OUT_0(data)
    );

    endmodule
    """ % (
        "0b11", route_fabric, route_fabric
        ), file=f)

    retval = os.system("bash ../../icecube.sh -" + device + " " + name+".v > ./work_osc/icecube.log 2>&1")
    if retval != 0:
        sys.stderr.write('ERROR: icecube returned non-zero error code\n')
        sys.exit(1)
    retval = os.system("../../../icebox/icebox_explain.py " + name+".asc > " + name+".exp")
    if retval != 0:
        sys.stderr.write('ERROR: icebox_explain returned non-zero error code\n')
        sys.exit(1)
    retval = os.system("../../../icebox/icebox_vlog.py " + name+".asc > " + name+".ve")
    if retval != 0:
        sys.stderr.write('ERROR: icebox_vlog returned non-zero error code\n')
        sys.exit(1)

run(0)
run(1)
