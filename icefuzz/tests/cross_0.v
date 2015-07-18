module top (
	input in_left, in_right, in_top, in_bottom,
	output out_left, out_right, out_top, out_bottom
);
	assign out_left = in_right;
	assign out_right = in_left;
	assign out_top = in_bottom;
	assign out_bottom = in_top;
endmodule
