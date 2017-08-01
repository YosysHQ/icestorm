// ICEDEV=hx8k-ct256 bash ../icecube.sh sb_ram40.v
// ../../icebox/icebox_vlog.py -P sb_ram40.psb sb_ram40.txt
// ../../icebox/icebox_explain.py -t '7 21' sb_ram40.txt

module top (
	input  [10:0] WADDR,
	input  [10:0] RADDR,
	input  [15:0] MASK,
	input  [15:0] WDATA,
	output [15:0] RDATA_0,
	output [ 7:0] RDATA_1,
	output [ 1:0] RDATA_3,
	input         WE, WCLKE, WCLK,
	input         RE, RCLKE, RCLK,
	output        X
);
	// Write Mode 0:  8 Bit ADDR, 16 Bit DATA, MASK
	// Write Mode 1:  9 Bit ADDR,  8 Bit DATA, NO MASK
	// Write Mode 2: 10 Bit ADDR,  4 Bit DATA, NO MASK
	// Write Mode 3: 11 Bit ADDR,  2 Bit DATA, NO MASK

	SB_RAM40_4K #(
		.READ_MODE(0),
		.WRITE_MODE(0)
	) ram40_00 (
		.WADDR(WADDR[7:0]),
		.RADDR(RADDR[7:0]),
		.MASK(MASK),
		.WDATA(WDATA),
		.RDATA(RDATA_0),
		.WE(WE),
		.WCLKE(WCLKE),
		.WCLK(WCLK),
		.RE(RE),
		.RCLKE(RCLKE),
		.RCLK(RCLK)
	);

	SB_RAM40_4K #(
		.READ_MODE(1),
		.WRITE_MODE(2)
	) ram40_12 (
		.WADDR(WADDR[9:0]),
		.RADDR(RADDR[8:0]),
		.WDATA(WDATA[3:0]),
		.RDATA(RDATA_1),
		.WE(WE),
		.WCLKE(WCLKE),
		.WCLK(WCLK),
		.RE(RE),
		.RCLKE(RCLKE),
		.RCLK(RCLK)
	);

	SB_RAM40_4K #(
		.READ_MODE(3),
		.WRITE_MODE(3)
	) ram40_33 (
		.WADDR(WADDR),
		.RADDR(RADDR),
		.WDATA(WDATA[1:0]),
		.RDATA(RDATA_3),
		.WE(WE),
		.WCLKE(WCLKE),
		.WCLK(WCLK),
		.RE(RE),
		.RCLKE(RCLKE),
		.RCLK(RCLK)
	);

	SB_LUT4 #(
		.LUT_INIT(16'b 1000_0000_0000_0000)
	) lut (
		.O(X),
		.I0(RDATA_0[0]),
		.I1(RDATA_0[6]),
		.I2(RDATA_0[8]),
		.I3(RDATA_0[14])
	);
endmodule
