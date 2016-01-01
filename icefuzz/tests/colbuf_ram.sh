#!/bin/bash

set -ex

mkdir -p colbuf_ram.work
cd colbuf_ram.work

glb_pins="93 21 128 50 20 94 49 129"

for x in 3 10; do
for y in {1..16}; do
	pf="colbuf_ram_${x}_${y}"
	gpin=$( echo $glb_pins | tr ' ' '\n' | sort -R | head -n1; )
	if [ $((y % 2)) == 1 ]; then
		clkport="WCLK"
		other_clkport="RCLK"
	else
		clkport="RCLK"
		other_clkport="WCLK"
	fi
	cat > ${pf}.v <<- EOT
		module top (input c, oc, input [1:0] d, output [1:0] q);
			wire gc;
			SB_GB_IO #(
				.PIN_TYPE(6'b 0000_00),
				.PULLUP(1'b0),
				.NEG_TRIGGER(1'b0),
				.IO_STANDARD("SB_LVCMOS")
			) gbuf (
				.PACKAGE_PIN(c),
				.GLOBAL_BUFFER_OUTPUT(gc)
			);
			SB_RAM40_4K #(
				.READ_MODE(3),
				.WRITE_MODE(3)
			) ram40 (
				.WADDR(11'b0),
				.RADDR(11'b0),
				.$clkport(gc),
				.$other_clkport(oc),
				.RDATA(q),
				.WDATA(d),
				.WE(1'b1),
				.WCLKE(1'b1),
				.RE(1'b1),
				.RCLKE(1'b1)
			);
		endmodule
	EOT
	echo "set_location ram40 $x $((y - (1 - y%2))) 0" > ${pf}.pcf
	echo "set_io oc 1" >> ${pf}.pcf
	echo "set_io c $gpin" >> ${pf}.pcf
	bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done

