#!/bin/bash

mkdir -p pinloc-4k-cm121
cd pinloc-4k-cm121

pins="
	A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11
	B1 B2 B3 B4 B5 B6 B7 B8 B9 B11
	C1 C2 C3 C4 C7 C8 C9 C11
	D1 D2 D3 D5 D7 D9 D10 D11
	E1 E2 E3 E8 E9 E10 E11
	F1 F2 F3 F4 F9 F10 F11
	G1 G2 G3 G8 G9 G10 G11
	H1 H2 H3 H7 H9 H10 H11
	J1 J2 J3 J4 J5 J7 J8 J9 J10 J11
	K1 K2 K3 K4 K5 K6 K7 K9 K10 K11
	L1 L2 L3 L4 L5 L7 L8 L10
"

if [ $(echo $pins | wc -w) -ne 93 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-4k-cm121_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-4k-cm121_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp4k-cm121 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-4k-cm121.mk

set -ex
make -f pinloc-4k-cm121.mk -j4
python3 ../pinlocdb.py pinloc-4k-cm121_*.exp > ../pinloc-4k-cm121.txt

