#!/bin/bash

set -ex

mkdir -p io_latched_lm4k.work
cd io_latched_lm4k.work

pins="
  A1 A2 A3 A4 A5 A6 A7
  B1 B2    B4    B6 B7
  C1    C3 C4    C6 C7
  D1 D2 D3       D6 D7
  E1 E2 E3 E4 E5    E7
     F2 F3 F4       F7
        G3
"
pins="$( echo $pins )"

for pin in $pins; do
	pf="io_latched_$pin"
	cp ../io_latched.v ${pf}.v
	read pin_latch pin_data < <( echo $pins | tr ' ' '\n' | grep -v $pin | sort -R; )
	{
		echo "set_io pin $pin"
		echo "set_io latch_in $pin_latch"
		echo "set_io data_out $pin_data"
	} > ${pf}.pcf
	ICEDEV=lm4k-cm49 bash ../../icecube.sh ${pf}.v
	../../../icebox/icebox_vlog.py -SP ${pf}.psb ${pf}.asc > ${pf}.ve
done

