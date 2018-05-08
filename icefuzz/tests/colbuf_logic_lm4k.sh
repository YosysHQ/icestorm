#!/bin/bash

set -ex

mkdir -p colbuf_logic_lm4k.work
cd colbuf_logic_lm4k.work

glb_pins="A3 A4 D2 E2 E5 G3"

for y in {1..32}; do
for y in {1..20}; do
	pf="colbuf_logic_lm4k_${x}_${y}"
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
	ICEDEV=lm4k-cm49 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done

