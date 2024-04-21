// From nextpnr:ice40/examples/blinky
// Original file due to Claire Xenia Wolf

module blinky (
    input  clki,
    output [4:0] led
);

    assign clk = clki;

    localparam BITS = 5;
    localparam LOG2DELAY = 21;

    reg [BITS+LOG2DELAY-1:0] counter = 0;
    reg [BITS-1:0] outcnt;

    always @(posedge clk) begin
        counter <= counter + 1;
        outcnt <= counter >> LOG2DELAY;
    end

    assign led = outcnt ^ (outcnt >> 1);
endmodule
