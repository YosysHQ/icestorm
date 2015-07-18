module testbench;
	reg  pin_reg;
	reg  latch_in;
	reg  clk_en;
	reg  clk_in;
	reg  clk_out;
	reg  oen;
	reg  dout_0;
	reg  dout_1;

	wire gold_pin;
	wire gold_global;
	wire gold_din_0;
	wire gold_din_1;

	wire gate_pin;
	wire gate_global;
	wire gate_din_0;
	wire gate_din_1;

	top gold (
		.pin     (gold_pin   ),
		.global  (gold_global),
		.latch_in(latch_in   ),
		.clk_en  (clk_en     ),
		.clk_in  (clk_in     ),
		.clk_out (clk_out    ),
		.oen     (oen        ),
		.dout_0  (dout_0     ),
		.dout_1  (dout_1     ),
		.din_0   (gold_din_0 ),
		.din_1   (gold_din_1 )
	);

	chip gate (
		.pin     (gate_pin   ),
		.global  (gate_global),
		.latch_in(latch_in   ),
		.clk_en  (clk_en     ),
		.clk_in  (clk_in     ),
		.clk_out (clk_out    ),
		.oen     (oen        ),
		.dout_0  (dout_0     ),
		.dout_1  (dout_1     ),
		.din_0   (gate_din_0 ),
		.din_1   (gate_din_1 )
	);

	assign gold_pin = pin_reg;
	assign gate_pin = pin_reg;

	reg [63:0] xorshift64_state = 64'd88172645463325252;

	task xorshift64_next;
		begin
			// see page 4 of Marsaglia, George (July 2003). "Xorshift RNGs". Journal of Statistical Software 8 (14).
			xorshift64_state = xorshift64_state ^ (xorshift64_state << 13);
			xorshift64_state = xorshift64_state ^ (xorshift64_state >>  7);
			xorshift64_state = xorshift64_state ^ (xorshift64_state << 17);
		end
	endtask

	reg error = 0;
	integer rndval;

	initial begin
	`ifdef VCDFILE
		$dumpfile(`VCDFILE);
		$dumpvars(0, testbench);
	`endif

		pin_reg  <= 0;
		latch_in <= 0;
		clk_en   <= 1;
		clk_in   <= 0;
		clk_out  <= 0;
		oen      <= 0;
		dout_0   <= 0;
		dout_1   <= 0;

		pin_reg  <= 0;
		repeat (5) #10 clk_in  <= ~clk_in;
		repeat (5) #10 clk_out <= ~clk_out;

		pin_reg  <= 1;
		repeat (5) #10 clk_in  <= ~clk_in;
		repeat (5) #10 clk_out <= ~clk_out;

		pin_reg  <= 'bz;
		repeat (5) #10 clk_in  <= ~clk_in;
		repeat (5) #10 clk_out <= ~clk_out;

		repeat (1000) begin
			if ('b `INTYPE == 0) begin
				error = {gold_pin, gold_global, gold_din_0, gate_din_1} !== {gate_pin, gate_global, gate_din_0, gate_din_1};
				$display({"pin=%b%b, global=%b%b, latch_in=%b, clk_en=%b, clk_in=%b, clk_out=%b, ",
						"oen=%b, dout_0=%b, dout_1=%b, din_0=%b%b, din_1=%b%b %s"},
						gold_pin, gate_pin, gold_global, gate_global, latch_in, clk_en, clk_in, clk_out,
						oen, dout_0, dout_1, gold_din_0, gate_din_0, gold_din_1, gate_din_1, error ? "ERROR" : "OK");
			end else begin
				error = {gold_pin, gold_global, gold_din_0} !== {gate_pin, gate_global, gate_din_0};
				$display({"pin=%b%b, global=%b%b, latch_in=%b, clk_en=%b, clk_in=%b, clk_out=%b, ",
						"oen=%b, dout_0=%b, dout_1=%b, din_0=%b%b %s"},
						gold_pin, gate_pin, gold_global, gate_global, latch_in, clk_en, clk_in, clk_out,
						oen, dout_0, dout_1, gold_din_0, gate_din_0, error ? "ERROR" : "OK");
			end
			xorshift64_next;
			rndval = (xorshift64_state >> 16) & 'hffff;
			case (xorshift64_state % 5)
				0: pin_reg  <= 1'bz;
				1: pin_reg  <= 1'b0;
				2: pin_reg  <= 1'b1;
			`ifdef DISABLED
				// Lattice SB_IO clk_en model is b0rken
				// IceBox latch_in routing is non-existing
				default: {latch_in, clk_en, clk_in, clk_out, oen, dout_0, dout_1} <=
						{latch_in, clk_en, clk_in, clk_out, oen, dout_0, dout_1} ^ (1 << (rndval % 7));
			`else
				default: {latch_in, clk_in, clk_out, oen, dout_0, dout_1} <=
						{latch_in, clk_in, clk_out, oen, dout_0, dout_1} ^ (1 << (rndval % 6));
			`endif
			endcase
			#10;
		end
	end
endmodule
