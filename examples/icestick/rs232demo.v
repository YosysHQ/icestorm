module top (
	input  clk,
	input  RX,
	output TX,
	output reg LED1,
	output reg LED2,
	output reg LED3,
	output reg LED4,
	output reg LED5
);
	parameter integer BAUD_RATE = 9600;
	parameter integer CLOCK_FREQ_HZ = 12000000;
	localparam integer HALF_PERIOD = CLOCK_FREQ_HZ / (2 * BAUD_RATE);

	reg [9:0] buffer;
	reg buffer_valid;

	reg [$clog2(3*HALF_PERIOD):0] cycle_cnt;
	reg [3:0] bit_cnt = 0;
	reg [0:0] state = 0;

	always @(posedge clk) begin
		buffer_valid <= 0;
		case (state)
			0: begin
				if (!RX) begin
					cycle_cnt <= HALF_PERIOD;
					bit_cnt <= 0;
					state <= 1;
				end
			end
			1: begin
				if (cycle_cnt == 2*HALF_PERIOD) begin
					cycle_cnt <= 0;
					buffer[bit_cnt] <= RX;
					bit_cnt <= bit_cnt + 1;
					if (bit_cnt == 9) begin
						buffer_valid <= 1;
						state <= 0;
					end
				end else begin
					cycle_cnt <= cycle_cnt + 1;
				end
			end
		endcase
	end

	always @(posedge clk) begin
		if (buffer_valid) begin
			if (buffer[8:1] == "1") LED1 <= !LED1;
			if (buffer[8:1] == "2") LED2 <= !LED2;
			if (buffer[8:1] == "3") LED3 <= !LED3;
			if (buffer[8:1] == "4") LED4 <= !LED4;
			if (buffer[8:1] == "5") LED5 <= !LED5;
		end
	end

	assign TX = RX;
endmodule
