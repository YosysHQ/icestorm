#!/bin/bash

set -ex

mkdir -p io_latched.work
cd io_latched.work

pins="
	1 2 3 4 7 8 9 10 11 12 19 22 23 24 25 26 28 29 31 32 33 34
	37 38 41 42 43 44 45 47 48 52 56 58 60 61 62 63 64
	73 74 75 76 78 79 80 81 87 88 90 91 95 96 97 98 101 102 104 105 106 107
	112 113 114 115 116 117 118 119 120 121 122 134 135 136 137 138 139 141 142 143 144
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
	bash ../../icecube.sh ${pf}.v
	../../../icebox/icebox_vlog.py -SP ${pf}.psb ${pf}.asc > ${pf}.ve
done

