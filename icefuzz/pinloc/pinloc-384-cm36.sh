#!/bin/bash

mkdir -p pinloc-384-cm36
cd pinloc-384-cm36

pins="
        A1 A2 A3
        B1    B3 B4 B5 B6
        C1 C2 C3    C5 C6
        D1          D5 D6
        E1 E2 E3 E4 E5 E6
           F2 F3    F5
"

if [ $(echo $pins | wc -w) -ne 25 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-384-cm36_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-384-cm36_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp384-cm36 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-384-cm36.mk

set -ex
make -f pinloc-384-cm36.mk -j4
python3 ../pinlocdb.py pinloc-384-cm36_*.exp > ../pinloc-384-cm36.txt

