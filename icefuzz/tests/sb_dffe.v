module top (input C, D, E, output Q);
	SB_DFFE ff (.C(C), .D(D), .E(E), .Q(Q));
endmodule
