module testbench;
	localparam integer PERIOD = 12000000 / 9600;

	// reg clk = 0;
	// initial #10 forever #5 clk = ~clk;

	reg clk;
	always #5 clk = (clk === 1'b0);

	reg RX = 1;
	wire TX;
	wire LED1;
	wire LED2;
	wire LED3;
	wire LED4;
	wire LED5;

	top uut (
		.clk (clk ),
		.RX  (RX  ),
		.TX  (TX  ),
		.LED1(LED1),
		.LED2(LED2),
		.LED3(LED3),
		.LED4(LED4),
		.LED5(LED5)
	);

	task send_byte;
		input [7:0] c;
		integer i;
		begin
			RX <= 0;
			repeat (PERIOD) @(posedge clk);

			for (i = 0; i < 8; i = i+1) begin
				RX <= c[i];
				repeat (PERIOD) @(posedge clk);
			end

			RX <= 1;
			repeat (PERIOD) @(posedge clk);
		end
	endtask

	reg [4095:0] vcdfile;

	initial begin
		if ($value$plusargs("vcd=%s", vcdfile)) begin
			$dumpfile(vcdfile);
			$dumpvars(0, testbench);
		end

		repeat (10 * PERIOD) @(posedge clk);

		// turn all LEDs off
		send_byte("1");
		send_byte("3");
		send_byte("5");

		// turn all LEDs on
		send_byte("1");
		send_byte("2");
		send_byte("3");
		send_byte("4");
		send_byte("5");

		// turn all LEDs off
		send_byte("1");
		send_byte("2");
		send_byte("3");
		send_byte("4");
		send_byte("5");

		repeat (10 * PERIOD) @(posedge clk);

		$finish;
	end
endmodule
