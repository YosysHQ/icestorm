#!/bin/bash

mkdir -p pinloc-1k-cm121
cd pinloc-1k-cm121

pins="
	A1 A2 A3 A5 A7 A8 A9 A10 A11
	B1 B2 B3 B4 B5 B7 B8 B9 B10 B11
	C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11
	D1 D2 D3 D4 D5 D6 D10 D11
	E2 E3 E4 E6 E7 E8 E9 E10
	F2 F3 F4 F5 F6 F8 F9 F11
	G2 G4 G8 G9 G11
	H1 H2 H4 H5 H6 H7 H8 H9 H10 H11
	J1 J2 J5 J6 J8 J10 J11
	K1 K2 K3 K4 K5 K7 K8 K9 K10 K11
	L1 L2 L3 L4 L5 L7 L9 L10 L11
"

if [ $(echo $pins | wc -w) -ne 95 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-cm121_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-cm121_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp1k-cm121 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-cm121.mk

set -ex
make -f pinloc-1k-cm121.mk -j4
python3 ../pinlocdb.py pinloc-1k-cm121_*.exp > ../pinloc-1k-cm121.txt
