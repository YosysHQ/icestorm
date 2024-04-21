// From nextpnr:ice40/examples/blinky
// Original file due to Claire Xenia Wolf

module blinky_tb;
    reg clk;
    always #5 clk = (clk === 1'b0);

    wire led1, led2, led3, led4, led5;

    blinky uut (
        .pin_21(clk),
        .pin_95(led1),
        .pin_96(led2),
        .pin_97(led3),
        .pin_98(led4),
        .pin_99(led5)
    );

    reg [4095:0] vcdfile;

    initial begin
        if ($value$plusargs("vcd=%s", vcdfile)) begin
            $dumpfile(vcdfile);
            $dumpvars(0, blinky_tb);
        end
    end

    initial begin
        repeat (10) begin
            repeat (900000) @(posedge clk);
            $display(led1, led2, led3, led4, led5);
        end
        $finish;
    end
endmodule
