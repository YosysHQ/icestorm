module top (input C, D, R, output Q);
	SB_DFFSR ff (.C(C), .D(D), .R(R), .Q(Q));
endmodule
