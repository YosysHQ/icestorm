#!/bin/bash

mkdir -p pinloc-1k-qn84
cd pinloc-1k-qn84

pins="
	A1  B1  A2  B2  A3  B3  A4  B4  A5  B5  A8  A9  B7  A10 B8  A11 B9  A12
	A13 B10 B11 A14 B12 A16 B13 B14 A19 B15 A20 B17 A22 A23 B18 B19 A25 A26
	B20 B21 A27 A29 B22 B23 A31 B24 A32 A33 A34 B26 A35 B27 A38 B29	A39 B30
	A40 B31 A41 A43 B32 A44 A45 B34 A46 B35 A47 B36 A48
"

if [ $(echo $pins | wc -w) -ne 67 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-qn84_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-qn84_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp1k-qn84 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-qn84.mk

set -ex
make -f pinloc-1k-qn84.mk -j4
python3 ../pinlocdb.py pinloc-1k-qn84_*.exp > ../pinloc-1k-qn84.txt

