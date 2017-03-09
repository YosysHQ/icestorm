#!/bin/bash

mkdir -p pinloc-384-cm49
cd pinloc-384-cm49

pins="
        A1 A2 A3 A4 A5 A6 A7
        B1 B2 B3 B4
        C1 C2    C4 C5 C6 C7
        D1 D2 D3 D4    D6 D7
           E2          E6 E7
        F1 F2 F3 F4 F5 F6 F7
        G1    G3 G4    G6
"


if [ $(echo $pins | wc -w) -ne 37 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-384-cm49_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-384-cm49_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp384-cm49 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-384-cm49.mk

set -ex
make -f pinloc-384-cm49.mk -j4
python3 ../pinlocdb.py pinloc-384-cm49_*.exp > ../pinloc-384-cm49.txt

