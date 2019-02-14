// A simple design demonstrating receiving and sending of RS232 signals
//
// With this design loaded, connect with a serial terminal to the USB serial
// port of the icestick (with 9600 BAUD) and use the number keys 1..5 to toggle
// the LEDs.

module top (
	input  clk,
	input  RX,
	output TX,
	output LED1,
	output LED2,
	output LED3,
	output LED4,
	output LED5
);
	parameter integer BAUD_RATE = 9600;
	parameter integer CLOCK_FREQ_HZ = 12000000;
	localparam integer PERIOD = CLOCK_FREQ_HZ / BAUD_RATE;

	rs232_recv #(
		.HALF_PERIOD(PERIOD / 2)
	) recv (
		.clk  (clk ),
		.RX   (RX  ),
		.LED1 (LED1),
		.LED2 (LED2),
		.LED3 (LED3),
		.LED4 (LED4),
		.LED5 (LED5)
	);

	rs232_send #(
		.PERIOD(PERIOD)
	) send (
		.clk  (clk ),
		.TX   (TX  ),
		.LED1 (LED1),
		.LED2 (LED2),
		.LED3 (LED3),
		.LED4 (LED4),
		.LED5 (LED5)
	);
endmodule

module rs232_recv #(
	parameter integer HALF_PERIOD = 5
) (
	input  clk,
	input  RX,
	output reg LED1,
	output reg LED2,
	output reg LED3,
	output reg LED4,
	output reg LED5
);
	reg [7:0] buffer;
	reg buffer_valid;

	reg [$clog2(3*HALF_PERIOD):0] cycle_cnt;
	reg [3:0] bit_cnt = 0;
	reg recv = 0;

	initial begin
		LED1 = 1;
		LED2 = 0;
		LED3 = 1;
		LED4 = 0;
		LED5 = 1;
	end

	always @(posedge clk) begin
		buffer_valid <= 0;
		if (!recv) begin
			if (!RX) begin
				cycle_cnt <= HALF_PERIOD;
				bit_cnt <= 0;
				recv <= 1;
			end
		end else begin
			if (cycle_cnt == 2*HALF_PERIOD) begin
				cycle_cnt <= 0;
				bit_cnt <= bit_cnt + 1;
				if (bit_cnt == 9) begin
					buffer_valid <= 1;
					recv <= 0;
				end else begin
					buffer <= {RX, buffer[7:1]};
				end
			end else begin
				cycle_cnt <= cycle_cnt + 1;
			end
		end
	end

	always @(posedge clk) begin
		if (buffer_valid) begin
			if (buffer == "1") LED1 <= !LED1;
			if (buffer == "2") LED2 <= !LED2;
			if (buffer == "3") LED3 <= !LED3;
			if (buffer == "4") LED4 <= !LED4;
			if (buffer == "5") LED5 <= !LED5;
		end
	end
endmodule

module rs232_send #(
	parameter integer PERIOD = 10
) (
	input  clk,
	output TX,
	input  LED1,
	input  LED2,
	input  LED3,
	input  LED4,
	input  LED5
);
	reg [7:0] buffer;
	reg buffer_valid;

	reg [$clog2(PERIOD):0] cycle_cnt = 0;
	reg [4:0] bit_cnt = 0;
	reg [5:0] byte_cnt = 60;

	always @(posedge clk) begin
		cycle_cnt <= cycle_cnt + 1;
		if (cycle_cnt == PERIOD-1) begin
			cycle_cnt <= 0;
			bit_cnt <= bit_cnt + 1;
			if (bit_cnt == 10) begin
				bit_cnt <= 0;
				byte_cnt <= byte_cnt + 1;
			end
		end
	end

	reg [7:0] data_byte;
	reg data_bit;

	always @* begin
		data_byte = 'bx;
		case (byte_cnt)
			0: data_byte <= "\r";
			1: data_byte <= LED1 ? "*" : "-";
			2: data_byte <= LED2 ? "*" : "-";
			3: data_byte <= LED3 ? "*" : "-";
			4: data_byte <= LED4 ? "*" : "-";
			5: data_byte <= LED5 ? "*" : "-";
		endcase
	end

	always @(posedge clk) begin
		data_bit = 'bx;
		case (bit_cnt)
			0: data_bit <= 0; // start bit
			1: data_bit <= data_byte[0];
			2: data_bit <= data_byte[1];
			3: data_bit <= data_byte[2];
			4: data_bit <= data_byte[3];
			5: data_bit <= data_byte[4];
			6: data_bit <= data_byte[5];
			7: data_bit <= data_byte[6];
			8: data_bit <= data_byte[7];
			9: data_bit <= 1;  // stop bit
			10: data_bit <= 1; // stop bit
		endcase
		if (byte_cnt > 5) begin
			data_bit <= 1;
		end
	end

	assign TX = data_bit;
endmodule
