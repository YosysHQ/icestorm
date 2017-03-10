#!/bin/bash

set -ex

mkdir -p ioctrl_384.work
cd ioctrl_384.work

pins="
        A1 A2 A3 A4 A5 A6 A7
        B1 B2 B3 B4
        C1 C2    C4 C5 C6 C7
        D1 D2 D3 D4    D6 D7
           E2          E6 E7
        F1 F2 F3 F4 F5 F6 F7
        G1    G3 G4    G6
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="ioctrl_384_$pin"
	echo "module top (output pin); assign pin = 1; endmodule" > ${pf}.v
	echo "set_io pin $pin" > ${pf}.pcf
	ICEDEV=lp384-cm49 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
done

set +x
echo "--snip--"
for pin in $pins; do
	python3 ../ioctrl_384.py ioctrl_384_${pin}.exp
done | tee ioctrl_384_db.txt
echo "--snap--"

