module top (
	input  clk,
	output LED1,
	output LED2,
	output LED3,
	output LED4,
	output LED5
);

	localparam BITS = 5;
	localparam LOG2DELAY = 22;

	function [BITS-1:0] bin2gray(input [BITS-1:0] in);
		integer i;
		reg [BITS:0] temp;
		begin
			temp = in;
			for (i=0; i<BITS; i=i+1)
				bin2gray[i] = ^temp[i +: 2];
		end
	endfunction

	reg [BITS+LOG2DELAY-1:0] counter = 0;

	always@(posedge clk)
		counter <= counter + 1;

	assign {LED1, LED2, LED3, LED4, LED5} = bin2gray(counter >> LOG2DELAY);
endmodule
