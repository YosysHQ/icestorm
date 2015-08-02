module top #(
	parameter NUM_BITS = 8
) (
	input [NUM_BITS-1:0] clk,
	output reg [NUM_BITS-1:0] y
);
	wire [NUM_BITS-1:0] t1;
	reg [NUM_BITS-1:0] t2;

	genvar i;
	generate for (i = 0; i < NUM_BITS; i = i+1) begin:bitslice
		SB_RAM40_4K #(
			.READ_MODE(0),
			.WRITE_MODE(0)
		) ram40 (
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

		always @(posedge clk[i]) begin
			t2[i] <= t1[i];
			y[i] <= t2[i];
		end
	end endgenerate
endmodule
