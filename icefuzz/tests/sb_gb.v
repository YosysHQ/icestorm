module top (
	input [7:0] a,
	output [7:0] y
);
	SB_GB gbufs [7:0] (
		.USER_SIGNAL_TO_GLOBAL_BUFFER(a),
		.GLOBAL_BUFFER_OUTPUT(y)
	);
endmodule
