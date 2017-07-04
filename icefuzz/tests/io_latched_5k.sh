#!/bin/bash

set -ex

mkdir -p io_latched_5k.work
cd io_latched_5k.work

pins="
2 3 4 6 9 10 11 12
13 18 19 20 21 23
25 26 27 28 31 32 34 35 36
37 38 42 43 44 45 46 47 48
"
pins="$( echo $pins )"

for pin in $pins ; do
	pf="io_latched_$pin"
	cp ../io_latched.v ${pf}.v
	read pin_latch pin_data < <( echo $pins | tr ' ' '\n' | grep -v $pin | sort -R; )
	{
		echo "set_io pin $pin"
		echo "set_io latch_in $pin_latch"
		echo "set_io data_out $pin_data"
	} > ${pf}.pcf
	ICEDEV=up5k-sg48 bash ../../icecube.sh ${pf}.v
	../../../icebox/icebox_vlog.py -SP ${pf}.psb ${pf}.asc > ${pf}.ve
done
