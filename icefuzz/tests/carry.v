module top (input a, b, ci, output co);
	SB_CARRY carry_cell (
		.I0(a),
		.I1(b),
		.CI(ci),
		.CO(co)
	);
endmodule
