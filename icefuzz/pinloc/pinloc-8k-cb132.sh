#!/bin/bash

mkdir -p pinloc-8k-cb132
cd pinloc-8k-cb132

pins="
	A1 A2 A3 A4 A5 A6 A7 A10 A11 A12 B1 B14
	C1 C3 C4 C5 C6 C7 C9 C10 C11 C12 C14
	D1 D3 D4 D5 D6 D7 D9 D10 D11 D12 D14
	E1 E4 E11 E12 E14 F3 F4 F11 F12 F14
	G1 G3 G4 G11 G12 G14 H1 H3 H4 H11 H12
	J1 J3 J11 J12 K3 K4 K11 K12 K14
	L1 L4 L5 L6 L8 L9 L12 L14
	M1 M3 M4 M6 M7 M9 M11 M12 N1 N14
	P1 P2 P3 P4 P5 P7 P8 P9 P10 P11 P12 P13 P14
"

if [ $(echo $pins | wc -w) -ne 95 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-8k-cb132_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-8k-cb132_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=hx8k-cb132 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-8k-cb132.mk

set -ex
make -f pinloc-8k-cb132.mk -j4
python3 ../pinlocdb.py pinloc-8k-cb132_*.exp > ../pinloc-8k-cb132.txt

