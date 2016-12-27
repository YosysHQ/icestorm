#!/bin/bash

set -ex

mkdir -p colbuf_logic.work
cd colbuf_logic.work

glb_pins="93 21 128 50 20 94 49 129"

for x in 1 2 {4..9} 11 12; do
for y in {1..16}; do
	pf="colbuf_logic_${x}_${y}"
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
	bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done

