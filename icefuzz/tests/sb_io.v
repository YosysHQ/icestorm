`define CONN_INTERNAL_BITS

`define PINTYPE 6'b010000
// `define IOSTANDARD "SB_LVCMOS"
`define IOSTANDARD "SB_LVDS_INPUT"

// The following IO standards are just aliases for SB_LVCMOS
// `define IOSTANDARD "SB_LVCMOS25_16"
// `define IOSTANDARD "SB_LVCMOS25_12"
// `define IOSTANDARD "SB_LVCMOS25_8"
// `define IOSTANDARD "SB_LVCMOS25_4"
// `define IOSTANDARD "SB_LVCMOS18_10"
// `define IOSTANDARD "SB_LVCMOS18_8"
// `define IOSTANDARD "SB_LVCMOS18_4"
// `define IOSTANDARD "SB_LVCMOS18_2"
// `define IOSTANDARD "SB_LVCMOS15_4"
// `define IOSTANDARD "SB_LVCMOS15_2"
// `define IOSTANDARD "SB_MDDR10"
// `define IOSTANDARD "SB_MDDR8"
// `define IOSTANDARD "SB_MDDR4"
// `define IOSTANDARD "SB_MDDR2"

`ifdef CONN_INTERNAL_BITS
module top (
	inout pin,
	input latch_in,
	input clk_in,
	input clk_out,
	input oen,
	input dout_0,
	input dout_1,
	output din_0,
	output din_1
);
`else
module top(pin);
	inout pin;
	wire latch_in = 0;
	wire clk_in = 0;
	wire clk_out = 0;
	wire oen = 0;
	wire dout_0 = 0;
	wire dout_1 = 0;
	wire din_0;
	wire din_1;
`endif
	SB_IO #(
		.PIN_TYPE(`PINTYPE),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b0),
		.IO_STANDARD(`IOSTANDARD)
	) IO_PIN_I (
		.PACKAGE_PIN(pin),
		.LATCH_INPUT_VALUE(latch_in),
		.CLOCK_ENABLE(clk_en),
		.INPUT_CLK(clk_in),
		.OUTPUT_CLK(clk_out),
		.OUTPUT_ENABLE(oen),
		.D_OUT_0(dout_0),
		.D_OUT_1(dout_1),
		.D_IN_0(din_0),
		.D_IN_1(din_1)
	);
endmodule
