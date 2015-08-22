#!/bin/bash

# for f in colbuf_io.work/*.exp colbuf_logic.work/*.exp colbuf_ram.work/*.exp; do
# 	python3 colbuf.py $f
# done | sort -u > colbuf.txt

get_colbuf_data()
{
	# tr -d '(,)' < colbuf.txt
	for x in {0..2} {4..9} {11..13}; do
		echo $x 4 $x 0
		echo $x 5 $x 8
		echo $x 12 $x 9
		echo $x 13 $x 17
	done
	for x in 3 10; do
		echo $x 3 $x 0
		echo $x 3 $x 4
		echo $x 5 $x 8
		echo $x 11 $x 9
		echo $x 11 $x 12
		echo $x 13 $x 17
	done
}

{
	echo "<svg xmlns=\"http://www.w3.org/2000/svg\" height=\"580\" width=\"460\">"
	for x in {1..13}; do
		echo "<line x1=\"$((10+x*30))\" y1=\"10\" x2=\"$((10+x*30))\" y2=\"$((10+18*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for y in {1..17}; do
		echo "<line x1=\"10\" y1=\"$((10+y*30))\" x2=\"$((10+14*30))\" y2=\"$((10+y*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for x in {0..13}; do
		echo "<text x=\"$((10+$x*30+7))\" y=\"$((10+18*30+15))\" fill=\"black\">$x</text>"
	done
	for y in {0..17}; do
		echo "<text x=\"$((10+14*30+5))\" y=\"$((10+(17-y)*30+20))\" fill=\"black\">$y</text>"
	done
	while read x1 y1 x2 y2; do
		echo "<line x1=\"$((10+x1*30+15))\" y1=\"$((10+(17-y1)*30+15))\" x2=\"$((10+x2*30+15))\" y2=\"$((10+(17-y2)*30+15))\" style=\"stroke:rgb(255,0,0);stroke-width:5\" />"
	done < <( get_colbuf_data; )
	while read x1 y1 x2 y2; do
		echo "<circle cx=\"$((10+x1*30+15))\" cy=\"$((10+(17-y1)*30+15))\" r=\"5\" fill=\"gray\" />"
	done < <( get_colbuf_data; )
	echo "</svg>"
} > colbuf.svg

