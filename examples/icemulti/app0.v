module top (
	input  clk,
	output LED1, LED2, LED3, LED4, LED5
);
	localparam LOG2DELAY = 22;

	reg [LOG2DELAY-1:0] counter = 0;
	reg [3:0] counter2 = 0;
	reg state = 0;

	always @(posedge clk) begin
		counter <= counter + 1;
		counter2 <= counter2 + !counter;
		state <= state ^ !counter;
	end

	assign LED1 = state;
	assign LED2 = 0;
	assign LED3 = 0;
	assign LED4 = 0;
	assign LED5 = 1;

	SB_WARMBOOT WB (
		.BOOT(&counter2),
		.S1(1'b 0),
		.S0(1'b 1)
	);
endmodule
