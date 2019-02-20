#!/bin/bash

set -ex

mkdir -p colbuf_logic_u4k.work
cd colbuf_logic_u4k.work

glb_pins="20 35 37 44"

for x in {1..5} {7..18} {20..24}; do
for y in {1..20}; do
	pf="colbuf_logic_u4k_${x}_${y}"
        [ -f ${pf}.exp ] && continue
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
        [ $x = 7 -a $y = 20 ] && continue
	ICEDEV=u4k-sg48 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done
