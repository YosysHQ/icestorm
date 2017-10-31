#!/bin/bash

set -ex

mkdir -p ioctrl.work
cd ioctrl.work

pins="2 3 4 6 9 10 11 12
	13 14 15 16 17 18 19 20 21 23
	25 26 27 28 31 32 34 35 36
	37 38 42 43 44 45 46 47 48
	"
pins="$( echo $pins )"

for pin in $pins; do
	pf="ioctrl_$pin"
	echo "module top (output pin); assign pin = 1; endmodule" > ${pf}.v
	echo "set_io pin $pin" > ${pf}.pcf
	bash ../../icecube.sh -up5k ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
done

set +x
echo "--snip--"
for pin in $pins; do
	python3 ../ioctrl_5k.py ioctrl_${pin}.exp
done | tee ioctrl_db.txt
echo "--snap--"
