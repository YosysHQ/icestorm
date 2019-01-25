module testbench;
	reg clk;
	always #5 clk = (clk === 1'b0);

	wire ok;

	top uut (
		.clk(clk),
		.LED5(ok)
	);

	reg [4095:0] vcdfile;

	initial begin
		if ($value$plusargs("vcd=%s", vcdfile)) begin
			$dumpfile(vcdfile);
			$dumpvars(0, testbench);
		end
	end

	initial begin
		@(posedge ok);
		@(negedge ok);
		$display("ERROR: detected falling edge on OK pin!");
		$stop;
	end

	initial begin
		repeat (3000) @(posedge clk);

		if (!ok) begin
			$display("ERROR: OK pin not asserted after 3000 cycles!");
			$stop;
		end

		repeat (10000) @(posedge clk);
		$display("SUCCESS: OK pin still asserted after 10000 cycles.");
		$finish;
	end
endmodule
