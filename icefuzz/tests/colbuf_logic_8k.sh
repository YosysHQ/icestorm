#!/bin/bash

set -ex

mkdir -p colbuf_logic_8k.work
cd colbuf_logic_8k.work

glb_pins="C8 F7 G1 H11 H16 J3 K9 R9"

for x in {1..7} {9..24} {26..32}; do
for y in {1..32}; do
	pf="colbuf_logic_8k_${x}_${y}"
	gpin=$( echo $glb_pins | tr ' ' '\n' | sort -R | head -n1; )
	cat > ${pf}.v <<- EOT
		module top (input c, d, output q);
			SB_DFF dff (
				.C(c),
				.D(d),
				.Q(q)
			);
		endmodule
	EOT
	echo "set_location dff $x $y 0" > ${pf}.pcf
	echo "set_io c $gpin" >> ${pf}.pcf
	ICEDEV=hx8k-ct256 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done

