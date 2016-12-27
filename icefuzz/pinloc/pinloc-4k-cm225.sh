#!/bin/bash

mkdir -p pinloc-4k-cm225
cd pinloc-4k-cm225

pins="
	A1 A2 A5 A6 A7 A8 A9 A11 A15
	B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 B13 B14 B15
	C1 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12 C13 C14
	D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D13 D14 D15
	E2 E3 E4 E5 E6 E9 E10 E11 E13 E14
	F1 F2 F3 F4 F5 F7 F9 F11 F12 F13 F14 F15
	G2 G4 G5 G10 G11 G12 G13 G14 G15
	H1 H2 H3 H4 H5 H6 H11 H12 H13 H14
	J1 J2 J3 J4 J5 J10 J11 J12 J14 J15
	K1 K4 K5 K9 K11 K12 K13 K15
	L3 L4 L5 L6 L7 L9 L10 L11 L12 L13
	M1 M2 M3 M4 M5 M6 M7 M8 M9 M11 M12 M13 M15
	N2 N3 N4 N5 N6 N7 N9 N10 N12
	P1 P2 P4 P5 P6 P7 P8 P9 P10 P11 P12 P13 P14 P15
	R1 R2 R3 R4 R5 R6 R9 R10 R11 R12 R14 R15
"

if [ $(echo $pins | wc -w) -ne 167 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-4k-cm225_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-4k-cm225_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp4k-cm225 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-4k-cm225.mk

set -ex
make -f pinloc-4k-cm225.mk -j4
python3 ../pinlocdb.py pinloc-4k-cm225_*.exp > ../pinloc-4k-cm225.txt

