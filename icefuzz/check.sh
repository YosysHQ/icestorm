#!/bin/bash

set -ex

for id; do
	id=${id%.bin}
	icebox_vlog_opts="-Sa"
	if test -f $id.pcf; then icebox_vlog_opts="$icebox_vlog_opts -p $id.pcf"; fi
	if test -f $id.psb; then icebox_vlog_opts="$icebox_vlog_opts -P $id.psb"; fi

	../icepack/iceunpack $id.bin $id.asc
	../icebox/icebox_vlog.py $icebox_vlog_opts $id.asc > $id.ve

	yosys -p "
		read_verilog $id.v
		read_verilog $id.ve
		read_verilog -lib +/ice40/cells_sim.v
		rename top gold
		rename chip gate

		proc
		splitnets -ports
		clean -purge

		## Variant 1 ##

		# miter -equiv -flatten gold gate equiv
		# tee -q synth -top equiv
		# sat -verify -prove trigger 0 -show-ports equiv

		## Variant 2 ##

		# miter -equiv -flatten -ignore_gold_x -make_outcmp -make_outputs gold gate equiv
		# hierarchy -top equiv
		# sat -max_undef -prove trigger 0 -show-ports equiv

		## Variant 3 ##

		equiv_make gold gate equiv
		hierarchy -top equiv
		opt -share_all

		equiv_simple
		equiv_induct
		equiv_status -assert
	"

	touch $id.ok
done

