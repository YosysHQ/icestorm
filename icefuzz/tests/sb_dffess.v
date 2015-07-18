module top (input C, D, E, S, output Q);
	SB_DFFESS ff (.C(C), .D(D), .E(E), .S(S), .Q(Q));
endmodule
