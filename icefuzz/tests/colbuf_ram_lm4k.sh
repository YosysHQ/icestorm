#!/bin/bash

set -ex

mkdir -p colbuf_ram_lm4k.work
cd colbuf_ram_lm4k.work

glb_pins="A3 A4 D2 E2 E5 G3"

for x in 6 19; do
for y in {1..20}; do
	pf="colbuf_ram_lm4k_${x}_${y}"
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
	ICEDEV=lm4k-cm49 bash ../../icecube.sh ${pf}.v > ${pf}.log 2>&1
	../../../icebox/icebox_explain.py ${pf}.asc > ${pf}.exp
	rm -rf ${pf}.tmp
done; done
