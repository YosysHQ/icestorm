#!/bin/bash

set -ex

mkdir -p io_latched_384.work
cd io_latched_384.work

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
	pf="io_latched_384_$pin"
	cp ../io_latched.v ${pf}.v
	read pin_latch pin_data < <( echo $pins | tr ' ' '\n' | grep -v $pin | sort -R; )
	{
		echo "set_io pin $pin"
		echo "set_io latch_in $pin_latch"
		echo "set_io data_out $pin_data"
	} > ${pf}.pcf
	ICEDEV=lp384-cm49 bash ../../icecube.sh ${pf}.v
	../../../icebox/icebox_vlog.py -SP ${pf}.psb ${pf}.asc > ${pf}.ve
done

