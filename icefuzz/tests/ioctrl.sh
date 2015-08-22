#!/bin/bash

set -ex

mkdir -p ioctrl.work
cd ioctrl.work

pins="
	1 2 3 4 7 8 9 10 11 12 19 20 21 22 23 24 25 26 28 29 31 32 33 34
	37 38 39 41 42 43 44 45 47 48 49 50 52 56 58 60 61 62 63 64 67 68 70 71
	73 74 75 76 78 79 80 81 87 88 90 91 93 94 95 96 97 98 99 101 102 104 105 106 107
	112 113 114 115 116 117 118 119 120 121 122 128 129 134 135 136 137 138 139 141 142 143 144
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="ioctrl_$pin"
	echo "module top (output pin); assign pin = 1; endmodule" > ${pf}.v
	echo "set_io pin $pin" > ${pf}.pcf
	bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.txt > ${pf}.exp
done

set +x
echo "--snip--"
for pin in $pins; do
	python3 ../ioctrl.py ioctrl_${pin}.exp
done | tee ioctrl_db.txt
echo "--snap--"

