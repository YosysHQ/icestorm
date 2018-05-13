#!/bin/bash

set -ex

mkdir -p ioctrl.work
cd ioctrl.work

pins="
  A1 A2 A3 A4 A5 A6 A7
  B1 B2    B4    B6 B7
  C1    C3 C4    C6 C7
  D1 D2 D3       D6 D7
  E1 E2 E3 E4 E5 E6 E7
     F2 F3 F4 F5 F6 F7
        G3       G6
"

pins="$( echo $pins )"

for pin in $pins; do
	pf="ioctrl_$pin"
	echo "module top (output pin); assign pin = 1; endmodule" > ${pf}.v
	echo "set_io pin $pin" > ${pf}.pcf
	bash ../../icecube.sh -lm4k ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
done

set +x
echo "--snip--"
for pin in $pins; do
	python3 ../ioctrl_5k.py ioctrl_${pin}.exp
done | tee ioctrl_db.txt
echo "--snap--"
