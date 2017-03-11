#!/bin/bash

for f in colbuf_io_384.work/*.exp colbuf_logic_384.work/*.exp; do
	echo $f >&2
	python3 colbuf_384.py $f
done | sort -u > colbuf_384.txt

get_colbuf_data()
{
	tr -d '(,)' < colbuf_384.txt
}

{
	echo "<svg xmlns=\"http://www.w3.org/2000/svg\" height=\"580\" width=\"460\">"
	for x in {1..7}; do
		echo "<line x1=\"$((10+x*30))\" y1=\"10\" x2=\"$((10+x*30))\" y2=\"$((10+18*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for y in {1..9}; do
		echo "<line x1=\"10\" y1=\"$((10+y*30))\" x2=\"$((10+14*30))\" y2=\"$((10+y*30))\" style=\"stroke:rgb(0,0,0);stroke-width:3\" />"
	done
	for x in {0..7}; do
		echo "<text x=\"$((10+$x*30+7))\" y=\"$((10+18*30+15))\" fill=\"black\">$x</text>"
	done
	for y in {0..9}; do
		echo "<text x=\"$((10+14*30+5))\" y=\"$((10+(17-y)*30+20))\" fill=\"black\">$y</text>"
	done
	while read x1 y1 x2 y2; do
		echo "<line x1=\"$((10+x1*30+15))\" y1=\"$((10+(17-y1)*30+15))\" x2=\"$((10+x2*30+15))\" y2=\"$((10+(17-y2)*30+15))\" style=\"stroke:rgb(255,0,0);stroke-width:5\" />"
	done < <( get_colbuf_data; )
	while read x1 y1 x2 y2; do
		echo "<circle cx=\"$((10+x1*30+15))\" cy=\"$((10+(17-y1)*30+15))\" r=\"5\" fill=\"gray\" />"
	done < <( get_colbuf_data; )
	echo "</svg>"
} > colbuf_384.svg

