#!/bin/bash

mkdir -p pinloc-u4k-sg48
cd pinloc-u4k-sg48

pins="
	2 3 4 6 9 10 11 12
	13 14 15 16 17 18 19 20 21 23
	25 26 27 28 31 32 34 35 36
	37 38 42 43 44 45 46 47 48
"

if [ $(echo $pins | wc -w) -ne 36 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-u4k-sg48_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-u4k-sg48_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=u4k-sg48 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-u4k-sg48.mk

set -ex
make -f pinloc-u4k-sg48.mk -j4
python3 ../pinlocdb.py pinloc-u4k-sg48_*.exp > ../pinloc-u4k-sg48.txt
