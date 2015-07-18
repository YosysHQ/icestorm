module top (
    inout pin,
    input latch_in,
    output din_0,
    output global
);
    SB_GB_IO #(
        .PIN_TYPE(6'b 0000_11),
        .PULLUP(1'b 0),
        .NEG_TRIGGER(1'b 0),
        .IO_STANDARD("SB_LVCMOS")
    ) \pin_gb_io (
        .PACKAGE_PIN(pin),
        .LATCH_INPUT_VALUE(latch_in),
        .D_IN_0(din_0),
        .GLOBAL_BUFFER_OUTPUT(globals)
    );
endmodule
