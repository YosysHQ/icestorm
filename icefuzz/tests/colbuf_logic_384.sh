#!/bin/bash

set -ex

mkdir -p colbuf_logic_384.work
cd colbuf_logic_384.work

glb_pins="B4 C4 D2 D6 D7 E2 F3 F4"

for x in 1 2 3 4 5 6; do
for y in 1 2 3 4 5 6 7 8; do
	pf="colbuf_logic_384_${x}_${y}"
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
	ICEDEV=lp384-cm49 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done

