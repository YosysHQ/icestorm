#!/bin/bash

pins="
	1 2 3 4 7 8 9 10 11 12 19 20 21 22 23 24 25 26 28 29 31 32 33 34
	37 38 39 41 42 43 44 45 47 48 49 50 52 56 58 60 61 62 63 64 67 68 70 71
	73 74 75 76 78 79 80 81 87 88 90 91 93 94 95 96 97 98 99 101 102 104 105 106 107
	112 113 114 115 116 117 118 119 120 121 122 128 129 134 135 136 137 138 139 141 142 143 144
"

{
	echo -n "all:"
	for pin in $pins; do
		id="pinloc-1k-tq144_${pin}"
		echo -n " ${id}.exp"
	done
	echo

	for pin in $pins; do
		id="pinloc-1k-tq144_${pin}"
		echo "module top(output y); assign y = 0; endmodule" > ${id}.v
		echo "set_io y ${pin}" >> ${id}.pcf
		echo; echo "${id}.exp:"
		echo "	ICEDEV=hx1k-tq144 bash ../icecube.sh ${id} > ${id}.log 2>&1"
		echo "	../../icebox/icebox_explain.py ${id}.txt > ${id}.exp.new"
		echo "	rm -rf ${id}.tmp"
		echo "	mv ${id}.exp.new ${id}.exp"
	done
} >  pinloc-1k-tq144.mk

set -ex
make -f pinloc-1k-tq144.mk -j4
python3 pinlocdb.py pinloc-1k-tq144_*.exp > pinloc-1k-tq144.txt

