module top (
	inout [7:0] pin,
	input in,
	output out
);
	wire [7:0] glbl, clk;
	reg [7:0] q;

	SB_GB_IO #(
		.PIN_TYPE(6'b 0000_11),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b0),
		.IO_STANDARD("SB_LVCMOS")
	) PIO[7:0] (
		.PACKAGE_PIN(pin),
		.LATCH_INPUT_VALUE(1'b1),
		.CLOCK_ENABLE(),
		.INPUT_CLK(),
		.OUTPUT_CLK(),
		.OUTPUT_ENABLE(),
		.D_OUT_0(),
		.D_OUT_1(),
		.D_IN_0(),
		.D_IN_1(),
		.GLOBAL_BUFFER_OUTPUT(glbl)
	);

	assign clk[0] = glbl[0]; // glb_netwk_4
	assign clk[1] = glbl[1]; // glb_netwk_1
	assign clk[2] = glbl[2]; // glb_netwk_6
	assign clk[3] = glbl[3]; // glb_netwk_3
	assign clk[4] = glbl[4]; // glb_netwk_0
	assign clk[5] = glbl[5]; // glb_netwk_5
	assign clk[6] = glbl[6]; // glb_netwk_2
	assign clk[7] = glbl[7]; // glb_netwk_7

	genvar i;
	generate for (i = 0; i < 8; i=i+1) begin
		always @(posedge clk[i]) q[i] <= in;
	end endgenerate
	assign out = ^{q, in};
endmodule
