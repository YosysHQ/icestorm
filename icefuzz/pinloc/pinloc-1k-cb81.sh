#!/bin/bash

mkdir -p pinloc-1k-cb81
cd pinloc-1k-cb81

pins="
	A2 A3 A4 A7 A8
	B1 B2 B3 B4 B5 B6 B7 B8
	C1 C2 C3 C4 C5 C6 C7 C8 C9
	D1 D2 D3 D4 D5 D6 D7 D8
	E1 E2 E3 E6 E7 E8 E9
	F2 F3 F6 F7 F8 F9
	G1 G2 G3 G4 G5 G6 G7 G8 G9
	H2 H3 H4 H5 H7 H8
	J2 J3 J7 J8
"

if [ $(echo $pins | wc -w) -ne 62 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-cb81_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-cb81_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp1k-cb81 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-cb81.mk

set -ex
make -f pinloc-1k-cb81.mk -j4
python3 ../pinlocdb.py pinloc-1k-cb81_*.exp > ../pinloc-1k-cb81.txt

