#!/bin/bash

mkdir -p pinloc-1k-vq100
cd pinloc-1k-vq100

pins="
	1 2 3 4 7 8 9 10 12 13 15 16 18 19 20 21 24 25
	26 27 28 29 30 33 34 36 37 40 41 42 45 46 48 49
	51 52 53 54 56 57 59 60 62 63 64 65 66 68 69 71 72 73 74
	78 79 80 81 82 83 85 86 87 89 90 91 93 94 95 96 97 99 100
"

if [ $(echo $pins | wc -w) -ne 72 ]; then
	echo "Incorrect number of pins:" $(echo $pins | wc -w)
	exit 1
fi

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-vq100_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-vq100_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=hx1k-vq100 bash ../../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../../icebox/icebox_explain.py ${id}.asc > ${id}.exp.new"
		echo "	! grep '^Warning: pin' ${id}.log"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-vq100.mk

set -ex
make -f pinloc-1k-vq100.mk -j4
python3 ../pinlocdb.py pinloc-1k-vq100_*.exp > ../pinloc-1k-vq100.txt

