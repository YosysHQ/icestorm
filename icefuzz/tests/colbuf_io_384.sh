#!/bin/bash

set -ex

mkdir -p colbuf_io_384.work
cd colbuf_io_384.work

glb_pins="B4 C4 D2 D6 D7 E2 F3 F4"

pins="
        A1 A2 A3 A4 A5 A6 A7
        B1 B2 B3 B4
        C1 C2    C4 C5 C6 C7
        D1 D2 D3 D4    D6 D7
           E2          E6 E7
        F1 F2 F3 F4 F5 F6 F7
        G1    G3 G4    G6
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="colbuf_io_384_$pin"
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
	ICEDEV=lp384-cm49 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done

