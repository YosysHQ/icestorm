module top (
	inout [7:0] pin,
	input latch_in,
	input clk_en,
	input clk_in,
	input clk_out,
	input oen,
	input dout_0,
	input dout_1,
	output [7:0] din_0,
	output [7:0] din_1,
	output [7:0] globals
);
	SB_GB_IO #(
		.PIN_TYPE(6'b 1100_00),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b0),
		.IO_STANDARD("SB_LVCMOS")
	) PINS [7:0] (
		.PACKAGE_PIN(pin),
		.LATCH_INPUT_VALUE(latch_in),
		.CLOCK_ENABLE(clk_en),
		.INPUT_CLK(clk_in),
		.OUTPUT_CLK(clk_out),
		.OUTPUT_ENABLE(oen),
		.D_OUT_0(dout_0),
		.D_OUT_1(dout_1),
		.D_IN_0(din_0),
		.D_IN_1(din_1),
		.GLOBAL_BUFFER_OUTPUT(globals)
	);
endmodule
