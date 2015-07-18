module top(input boot, s0, s1);
	SB_WARMBOOT warmboot (
		.BOOT(boot),
		.S0(s0),
		.S1(s1)
	);
endmodule
