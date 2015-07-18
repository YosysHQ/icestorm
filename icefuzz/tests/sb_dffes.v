module top (input C, D, E, S, output Q);
	SB_DFFES ff (.C(C), .D(D), .E(E), .S(S), .Q(Q));
endmodule
