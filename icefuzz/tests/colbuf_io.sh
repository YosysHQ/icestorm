#!/bin/bash

set -ex

mkdir -p colbuf_io.work
cd colbuf_io.work

glb_pins="93 21 128 50 20 94 49 129"

pins="
	1 2 3 4 7 8 9 10 11 12 19 22 23 24 25 26 28 29 31 32 33 34
	37 38 41 42 43 44 45 47 48 52 56 58 60 61 62 63 64
	73 74 75 76 78 79 80 81 87 88 90 91 95 96 97 98 101 102 104 105 106 107
	112 113 114 115 116 117 118 119 120 121 122 134 135 136 137 138 139 141 142 143 144
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="colbuf_io_$pin"
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
	bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done

