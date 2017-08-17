#!/bin/bash

mkdir -p pinloc-384-qn32
cd pinloc-384-qn32

pins="
	1 2 5 6 7 8
	12 13 14 15
	18 19 20 22 23
	26 27 29 30 31 32
"

if [ $(echo $pins | wc -w) -ne 21 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-384-qn32_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-384-qn32_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=lp384-qn32 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-384-qn32.mk

set -ex
make -f pinloc-384-qn32.mk -j4
python3 ../pinlocdb.py pinloc-384-qn32_*.exp > ../pinloc-384-qn32.txt
