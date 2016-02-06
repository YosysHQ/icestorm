#!/bin/bash

mkdir -p pinloc-1k-swg16tr
cd pinloc-1k-swg16tr

pins="
	A2 A4 B1 B2 B3 C1 C2 C3 D1 D3
"

if [ $(echo $pins | wc -w) -ne 10 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-swg16tr_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-swg16tr_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp1k-swg16tr bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-swg16tr.mk

set -ex
make -f pinloc-1k-swg16tr.mk -j4
python3 ../pinlocdb.py pinloc-1k-swg16tr_*.exp > ../pinloc-1k-swg16tr.txt

