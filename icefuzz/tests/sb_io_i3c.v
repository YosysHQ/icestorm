
module top (
	inout pin_23,
	inout pin_25,
	input pin_23_puen,
	input pin_23_wkpuen,
	input pin_25_puen,
	input pin_25_wkpuen);
	
	(* PULLUP_RESISTOR = "3P3K" *)
	SB_IO_I3C #(
		.PIN_TYPE(6'b000001),
		.PULLUP(1'b1),
		.WEAK_PULLUP(1'b1),

		.NEG_TRIGGER(1'b0)
	) IO_PIN_0 (
		.PACKAGE_PIN(pin_23),
		.PU_ENB(pin_23_puen),
		.WEAK_PU_ENB(pin_23_wkpuen)
	) ;
	
	(* PULLUP_RESISTOR = "3P3K" *)
	SB_IO_I3C #(
		.PIN_TYPE(6'b000001),
		.PULLUP(1'b1),
		.WEAK_PULLUP(1'b1),

		.NEG_TRIGGER(1'b0)
	) IO_PIN_1 (
		.PACKAGE_PIN(pin_25),
		.PU_ENB(pin_25_puen),
		.WEAK_PU_ENB(pin_25_wkpuen)
	);
endmodule
