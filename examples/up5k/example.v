module top (
	input  btn,
	output LED0,
	output LED1,
);

assign LED0 = !btn;
assign LED1 = btn;

endmodule
