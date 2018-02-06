module top (
	input  CLK,

	output LED1,
	output LED2,
	output LED3,
	output LED4,
	output LED5,

	input BTN_N,
	input BTN1,
	input BTN2,
	input BTN3,

	output LEDR_N,
	output LEDG_N,

	output P1A1, P1A2, P1A3, P1A4, P1A7, P1A8, P1A9, P1A10,
	output P1B1, P1B2, P1B3, P1B4, P1B7, P1B8, P1B9, P1B10
);

	localparam BITS = 5;
	localparam LOG2DELAY = 22;

	reg [BITS+LOG2DELAY-1:0] counter = 0;
	reg [BITS-1:0] outcnt;

	always @(posedge CLK) begin
		counter <= counter + 1;
		outcnt <= counter >> LOG2DELAY;
	end

	assign {LED1, LED2, LED3, LED4, LED5} = outcnt ^ (outcnt >> 1);

	assign {LEDR_N, LEDG_N} = ~(!BTN_N + BTN1 + BTN2 + BTN3);

	assign {P1A1, P1A2, P1A3, P1A4, P1A7, P1A8, P1A9, P1A10,
			P1B1, P1B2, P1B3, P1B4, P1B7, P1B8, P1B9, P1B10} = 1 << (outcnt & 15);
endmodule
