#!/bin/bash

set -ex

mkdir -p colbuf_io_5k.work
cd colbuf_io_5k.work

glb_pins="20 35 37 44"

pins="
2 3 4 6 9 10 11 12
	13 18 19 20 21
	25 26 27 28 31 32 34 35 36
	37 38 42 43 44 45 46 47 48
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="colbuf_io_5k_$pin"
	gpin=$( echo $glb_pins | tr ' ' '\n' | grep -v $pin | sort -R | head -n1; )
	cat > ${pf}.v <<- EOT
		module top (input clk, data, output pin);
			SB_IO #(
				.PIN_TYPE(6'b 0101_00)
			) pin_obuf (
				.PACKAGE_PIN(pin),
				.OUTPUT_CLK(clk),
				.D_OUT_0(data)
			);
		endmodule
	EOT
	echo "set_io pin $pin" > ${pf}.pcf
	echo "set_io clk $gpin" >> ${pf}.pcf
	ICEDEV=up5k-sg48 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done
