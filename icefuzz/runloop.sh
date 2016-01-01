#!/bin/bash

i=0
while true; do
	echo; git diff cached_*.txt | diffstat
	echo; echo -n "[$(date '+%H:%M:%S')] Iteration $(( ++i )) "
	{ echo; echo; echo; echo; echo; echo; echo "Iteration $i"; date; } >> runloop.log
	if make clean > >( gawk '{ print >> "runloop.log"; printf("x"); fflush(""); }'; ) 2>&1 &&
		make -j6 > >( gawk '{ print >> "runloop.log"; printf("m"); fflush(""); }'; ) 2>&1 &&
		make -j6 check > >( gawk '{ print >> "runloop.log"; if (NR % 100 == 0) printf("c"); fflush(""); }'; ) 2>&1
	then
		echo -n " OK"
	else
		echo " ERROR"; echo
		tail runloop.log
		exit 1
	fi
done

