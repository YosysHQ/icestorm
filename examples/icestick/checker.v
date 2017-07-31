// A simple circuit that can be used to detect brownouts and other hardware issues

module top (
	input clk,
	output LED1,
	output LED2,
	output LED3,
	output LED4,
	output LED5
);
	reg [7:0] reset_counter = 0;
	reg resetn = 0;

	always @(posedge clk) begin
		reset_counter <= reset_counter + 1;
		resetn <= resetn | &reset_counter;
	end

	reg error, rdmode, rdfin;

	reg [31:0] scratchpad [0:1023];
	reg [31:0] xorshift32_state;
	reg [9:0] index;

	reg [31:0] next_xorshift32_state;

	always @* begin
		next_xorshift32_state =      xorshift32_state ^ (     xorshift32_state << 13);
		next_xorshift32_state = next_xorshift32_state ^ (next_xorshift32_state >> 17);
		next_xorshift32_state = next_xorshift32_state ^ (next_xorshift32_state <<  5);
	end

	always @(posedge clk) begin
		xorshift32_state <= &index ? 123456789 : next_xorshift32_state;
		index <= index + 1;

		if (!resetn) begin
			xorshift32_state <= 123456789;
			index <= 0;
			error <= 0;
			rdmode <= 0;
			rdfin <= 0;
		end else
		if (!rdmode) begin
			scratchpad[index] <= xorshift32_state;
			rdmode <= &index;
		end else begin
			if (scratchpad[index] != xorshift32_state) error <= 1;
			rdfin <= rdfin || &index;
		end
	end

	wire ok = resetn && rdfin && !error;
	assign LED1 = 0, LED2 = error, LED3 = 0, LED4 = error, LED5 = ok;
endmodule
