#!/bin/bash
set -ex

python3 makedemo.py
yosys -p 'synth_ice40 -json demo.json' demo.v
nextpnr-ice40 --hx8k --package bg121 --pcf-allow-unconstrained --asc demo.asc --json demo.json

./icebram -v demo_dat0.hex demo_dat1.hex < demo.asc > demo_new.asc

icebox_vlog -n demo -p demo.pcf -c demo_new.asc > demo_new.v
iverilog -o demo.vvp demo_tb.v demo_new.v $( yosys-config --datdir/ice40/cells_sim.v )
vvp -N demo.vvp
