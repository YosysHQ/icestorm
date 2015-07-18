module top (input a, b, c, d, e, f, g, output y);
	wire cascade;

	SB_LUT4 #(
		.LUT_INIT(16'b 1100_1100_1100_1010)
	) src_lut (
		.O(cascade),
		.I0(a),
		.I1(b),
		.I2(c),
		.I3(d)
	);

	SB_LUT4 #(
		.LUT_INIT(16'b 1000_0100_0010_0001)
	) dst_lut (
		.O(y),
		.I0(e),
		.I1(f),
		.I2(cascade),
		.I3(g)
	);
endmodule
