#!/bin/bash

set -e
lattice_simlib="/opt/lscc/iCEcube2.2014.12/verilog/sb_ice_syn.v"

mkdir -p test_pio.work
cd test_pio.work

for NEGTRIG in 0 1; do
for INTYPE in 00 01 10 11; do
for OUTTYPE in 0000 0110 1010 1110 0101 1001 1101 \
               0100 1000 1100 0111 1011 1111; do
	pf="test_pio_${OUTTYPE}${INTYPE}${NEGTRIG}"
	echo "Testing ${pf}..."
	if ! test -f ${pf}.bin; then
		cat > ${pf}.v <<- EOT
			module top (
			    inout pin,
			    input latch_in,
			    input clk_en,
			    input clk_in,
			    input clk_out,
			    input oen,
			    input dout_0,
			    input dout_1,
			    output din_0,
			    output din_1,
			    output global
			);
			    SB_GB_IO #(
				.PIN_TYPE(6'b${OUTTYPE}${INTYPE}),
				.PULLUP(1'b0),
				.NEG_TRIGGER(1'b${NEGTRIG}),
				.IO_STANDARD("SB_LVCMOS")
			    ) pin_gb_io (
				.PACKAGE_PIN(pin),
				.GLOBAL_BUFFER_OUTPUT(global),
				.LATCH_INPUT_VALUE(latch_in),
				.CLOCK_ENABLE(clk_en),
				.INPUT_CLK(clk_in),
				.OUTPUT_CLK(clk_out),
				.OUTPUT_ENABLE(oen),
				.D_OUT_0(dout_0),
				.D_OUT_1(dout_1),
				.D_IN_0(din_0),
				.D_IN_1(din_1)
			    );
			endmodule
		EOT
		bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	fi
	python3 ../../../icebox/icebox_vlog.py -P ${pf}.psb ${pf}.txt > ${pf}_out.v
	iverilog -D"VCDFILE=\"${pf}_tb.vcd\"" -DINTYPE=${INTYPE} -o ${pf}_tb \
			-s testbench ../test_pio_tb.v ${pf}.v ${pf}_out.v $lattice_simlib 2> /dev/null
	./${pf}_tb > ${pf}_tb.txt
	if grep ERROR ${pf}_tb.txt; then exit 1; fi
done; done; done

echo "All tests passed."

