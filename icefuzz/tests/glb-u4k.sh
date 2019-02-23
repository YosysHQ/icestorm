#!/bin/bash

set -ex

mkdir -p glb_u4k.work
cd glb_u4k.work

glb_pins="20 35 37 44"

for gpin in $glb_pins; do
    pf="glb_u4k_pin_$gpin"
    cat > ${pf}.v <<- EOT
		module top (input clk, data, output pin);
			wire gc;
			SB_GB_IO #(
				.PIN_TYPE(6'b 0000_00),
				.PULLUP(1'b0),
				.NEG_TRIGGER(1'b0),
				.IO_STANDARD("SB_LVCMOS")
			) gbuf (
				.PACKAGE_PIN(clk),
				.GLOBAL_BUFFER_OUTPUT(gc)
			);
			SB_IO #(
				.PIN_TYPE(6'b 0101_00)
			) pin_obuf (
				.PACKAGE_PIN(pin),
				.OUTPUT_CLK(gc),
				.D_OUT_0(data)
			);
		endmodule
	EOT
    echo "set_io clk $gpin" > ${pf}.pcf
    ICEDEV=u4k-sg48 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
    ../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
    rm -rf ${pf}.tmp
done

oscs="HF LF"

for osc in $oscs; do
    pf="glb_u4k_${osc}"
    cat > ${pf}.v <<- EOT
		module top (input data, output pin);
			wire clk;
			SB_${osc}OSC osc(
				.CLK${osc}PU(1'b1),
				.CLK${osc}EN(1'b1),
				.CLK${osc}(clk)
			);
			SB_IO #(
				.PIN_TYPE(6'b 0101_00)
			) pin_obuf (
				.PACKAGE_PIN(pin),
				.OUTPUT_CLK(clk),
				.D_OUT_0(data)
			);
		endmodule
	EOT
    ICEDEV=u4k-sg48 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
    ../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
    rm -rf ${pf}.tmp
done

pf="glb_u4k_gbufin"
cat > ${pf}.v <<- EOT
		module top (input [7:0] clk, data, output [7:0] pin);
			wire [7:0] gc;
			SB_GB gbufin[7:0] (
				.USER_SIGNAL_TO_GLOBAL_BUFFER(clk),
				.GLOBAL_BUFFER_OUTPUT(gc)
			);
			SB_IO #(
				.PIN_TYPE(6'b 0101_00)
			) pin_obuf[7:0] (
				.PACKAGE_PIN(pin),
				.OUTPUT_CLK(gc),
				.D_OUT_0(data)
			);
		endmodule
	EOT
# echo "set_io clk 10" > ${pf}.pcf
ICEDEV=u4k-sg48 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
rm -rf ${pf}.tmp
