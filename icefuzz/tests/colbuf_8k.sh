#!/bin/bash

for f in colbuf_io_8k.work/*.exp colbuf_logic_8k.work/*.exp colbuf_ram_8k.work/*.exp; do
	echo $f >&2
	python3 colbuf.py $f
done | sort -u > colbuf_8k.txt

get_colbuf_data()
{
	tr -d '(,)' < colbuf_8k.txt
	# for x in {0..2} {4..9} {11..13}; do
	# 	echo $x 4 $x 0
	# 	echo $x 5 $x 8
	# 	echo $x 12 $x 9
	# 	echo $x 13 $x 17
	# done
	# for x in 3 10; do
	# 	echo $x 3 $x 0
	# 	echo $x 3 $x 4
	# 	echo $x 5 $x 8
	# 	echo $x 11 $x 9
	# 	echo $x 11 $x 12
	# 	echo $x 13 $x 17
	# done
}

{
	echo "<svg xmlns=\"http://www.w3.org/2000/svg\" height=\"1050\" width=\"1050\">"
	for x in {1..33}; do
		echo "<line x1=\"$((10+x*30))\" y1=\"10\" x2=\"$((10+x*30))\" y2=\"$((10+34*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for y in {1..33}; do
		echo "<line x1=\"10\" y1=\"$((10+y*30))\" x2=\"$((10+34*30))\" y2=\"$((10+y*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for x in {0..33}; do
		echo "<text x=\"$((10+$x*30+7))\" y=\"$((10+34*30+15))\" fill=\"black\">$x</text>"
	done
	for y in {0..33}; do
		echo "<text x=\"$((10+34*30+5))\" y=\"$((10+(33-y)*30+20))\" fill=\"black\">$y</text>"
	done
	while read x1 y1 x2 y2; do
		echo "<line x1=\"$((10+x1*30+15))\" y1=\"$((10+(33-y1)*30+15))\" x2=\"$((10+x2*30+15))\" y2=\"$((10+(33-y2)*30+15))\" style=\"stroke:rgb(255,0,0);stroke-width:5\" />"
	done < <( get_colbuf_data; )
	while read x1 y1 x2 y2; do
		echo "<circle cx=\"$((10+x2*30+15))\" cy=\"$((10+(33-y2)*30+15))\" r=\"4\" fill=\"blue\" />"
	done < <( get_colbuf_data; )
	while read x1 y1 x2 y2; do
		echo "<circle cx=\"$((10+x1*30+15))\" cy=\"$((10+(33-y1)*30+15))\" r=\"5\" fill=\"gray\" />"
	done < <( get_colbuf_data; )
	echo "</svg>"
} > colbuf_8k.svg

