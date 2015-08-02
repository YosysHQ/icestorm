module top #(
	parameter NUM_BITS = 1
) (
	input [NUM_BITS-1:0] clk,
	output [NUM_BITS-1:0] y
);
	wire [NUM_BITS-1:0] t1, t2, t3;

	genvar i;
	generate for (i = 0; i < NUM_BITS; i = i+1) begin:bitslice
		SB_RAM40_4K #(
			.READ_MODE(0),
			.WRITE_MODE(0)
		) ram40_upper (
			.WADDR(8'b0),
			.RADDR(8'b0),
			.MASK(~16'b0),
			.WDATA(8'b0),
			.RDATA(t1[i]),
			.WE(1'b1),
			.WCLKE(1'b1),
			.WCLK(clk[i]),
			.RE(1'b1),
			.RCLKE(1'b1),
			.RCLK(clk[i])
		);

		SB_RAM40_4K #(
			.READ_MODE(0),
			.WRITE_MODE(0)
		) ram40_lower (
			.WADDR(8'b0),
			.RADDR(8'b0),
			.MASK(~16'b0),
			.WDATA(8'b0),
			.RDATA(t2[i]),
			.WE(1'b1),
			.WCLKE(1'b1),
			.WCLK(clk[i]),
			.RE(1'b1),
			.RCLKE(1'b1),
			.RCLK(clk[i])
		);

		SB_DFF dff (
			.C(clk[i]),
			.D(t1[i] ^ t2[i]),
			.Q(t3[i])
		);

		SB_IO #(
			.PIN_TYPE(6'b 0101_01)
		) out (
			.PACKAGE_PIN(y[i]),
			.OUTPUT_CLK(clk[i]),
			.D_OUT_0(t3[i])
		);
	end endgenerate
endmodule
