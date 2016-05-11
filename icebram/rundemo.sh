#!/bin/bash
set -ex

python3 makedemo.py
yosys -p 'synth_ice40 -blif demo.blif' demo.v
arachne-pnr -d 8k -w demo.pcf -o demo.asc demo.blif

if true; then
    cp demo.asc demo_new.asc
    cp demo_dat0.hex demo_dat1.hex
else
    ./icebram -o demo_new.asc demo.asc demo_dat0.hex demo_dat1.hex
fi

icebox_vlog -n demo -p demo.pcf -c demo_new.asc > demo_new.v
iverilog -o demo.vvp demo_tb.v demo_new.v $( yosys-config --datdir/ice40/cells_sim.v )
vvp -N demo.vvp
