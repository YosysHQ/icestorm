module top (input C, D, R, output Q);
	SB_DFFR ff (.C(C), .D(D), .R(R), .Q(Q));
endmodule
