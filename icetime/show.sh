#!/bin/bash

set -ex

yosys -p '
	cd equiv
	equiv_mark
	select -write equiv_graph.segs w:seg_*_gate a:equiv_region!=0 %i
	show -prefix equiv_graph -format dot a:equiv_region!=0 %co2 a:equiv_region!=0 %ci2
' $1.il

./icetime -P tq144 -p $1.pcf $1.asc $( sed 's,_gate$,,; s,.*_,-g ,;' < equiv_graph.segs ) > /dev/null

{
	egrep -v '^}' icetime_graph.dot
	egrep -v '^(digraph|label=|})' equiv_graph.dot

	for seg in $( sed 's,equiv/,,' equiv_graph.segs ); do
		n=$( awk "/$seg/ { print \$1; }" equiv_graph.dot )
		s=$( echo $seg | sed 's,_[0-9]*_gate$,,' )
		echo "  $n:s -> $s:n [style=bold];"
	done
	echo "}"
} > $1.dot

rm -f equiv_graph.segs
rm -f equiv_graph.dot
rm -f icetime_graph.dot

