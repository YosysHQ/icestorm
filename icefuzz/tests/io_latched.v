module top (
	inout pin,
	input latch_in,
	output data_out
);
	SB_IO #(
		.PIN_TYPE(6'b0000_11),
		.PULLUP(1'b0),
		.NEG_TRIGGER(1'b0),
		.IO_STANDARD("SB_LVCMOS")
	) pin_ibuf (
		.PACKAGE_PIN(pin),
		.LATCH_INPUT_VALUE(latch_in),
		.CLOCK_ENABLE(),
		.INPUT_CLK(),
		.OUTPUT_CLK(),
		.OUTPUT_ENABLE(),
		.D_OUT_0(),
		.D_OUT_1(),
		.D_IN_0(data_out),
		.D_IN_1()
	);
endmodule
