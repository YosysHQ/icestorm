#!/bin/bash

pins="
	B1 C1 C3 D3 D4 E4 D1 E1 F4 F3 H3 H1 G1 G3 G4 H4 J1 J3 K4 K3 M1 L1 P1 N1 M3
	L4 P2 P3 M4 L5 P4 L6 P5 M6 P7 P8 M7 P9 L7 M8 L8 M9 L9 P10 M10 L10 M11 P11
	P12 P13 L11 M12 P14 L12 N14 M14 L14 K12 K11 K14 J12 J11 H12 H11 F14 G14
	G12 G11 F12 E14 F11 E12 D14 C14 E11 B14 D12 A14 A13 C12 A12 C11 C10 D11
	A10 D10 C9 D9 C8 D8 A7 A6 C7 D7 C6 A5 A4 D6 C5 A2 D5 A1 C4 A9 F1 F7 G7 G8
	G9 H6 H7 H8 J14 J8 L3 P6 F8 G6 H9 J4 J7 A8 F6 F9 H14 J9 M5 E3 J6 K1 A3 A11
"

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-cb132_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-cb132_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=hx1k-cb132 bash ../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-cb132.mk

set -ex
make -f pinloc-1k-cb132.mk -j4
python3 pinlocdb.py pinloc-1k-cb132_*.exp > pinloc-1k-cb132.txt

