module top(input clk, inout pin1, inout pin2);
	wire w;

	SB_IO #(
		.PIN_TYPE(6'b 0101_00),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b1),
		.IO_STANDARD("SB_LVCMOS")
	) IO_PIN_1 (
		.PACKAGE_PIN(pin1),
		.LATCH_INPUT_VALUE(),
		.CLOCK_ENABLE(),
		.INPUT_CLK(clk),
		.OUTPUT_CLK(clk),
		.OUTPUT_ENABLE(),
		.D_OUT_0(1'b0),
		.D_OUT_1(1'b0),
		.D_IN_0(w),
		.D_IN_1()
	);

	SB_IO #(
		.PIN_TYPE(6'b 0101_00),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b1),
		.IO_STANDARD("SB_LVCMOS")
	) IO_PIN_2 (
		.PACKAGE_PIN(pin2),
		.LATCH_INPUT_VALUE(),
		.CLOCK_ENABLE(),
		.INPUT_CLK(clk),
		.OUTPUT_CLK(clk),
		.OUTPUT_ENABLE(),
		.D_OUT_0(w),
		.D_OUT_1(1'b0),
		.D_IN_0(),
		.D_IN_1()
	);
endmodule
