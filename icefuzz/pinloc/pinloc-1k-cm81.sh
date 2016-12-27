#!/bin/bash

mkdir -p pinloc-1k-cm81
cd pinloc-1k-cm81

pins="
	A1 A2 A3 A4 A6 A7 A8 A9
	B1 B2 B3 B4 B5 B6 B7 B8 B9
	C1 C2 C3 C4 C5 C9
	D1 D2 D3 D5 D6 D7 D8 D9
	E1 E2 E3 E4 E5 E7 E8
	F1 F3 F7 F8
	G1 G3 G4 G5 G6 G7 G8 G9
	H1 H4 H5 H7 H9
	J1 J2 J3 J4 J6 J7 J8 J9
"

if [ $(echo $pins | wc -w) -ne 63 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-cm81_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-cm81_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp1k-cm81 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-cm81.mk

set -ex
make -f pinloc-1k-cm81.mk -j4
python3 ../pinlocdb.py pinloc-1k-cm81_*.exp > ../pinloc-1k-cm81.txt

