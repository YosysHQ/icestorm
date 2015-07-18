module top (input C, D, S, output Q);
	SB_DFFSS ff (.C(C), .D(D), .S(S), .Q(Q));
endmodule
