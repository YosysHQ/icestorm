// From nextpnr:ice40/examples/blinky
// Original file due to Claire Xenia Wolf

module blinky_tb;
    reg clk;
    always #5 clk = (clk === 1'b0);

    wire led1, led2, led3, led4, led5;

    blinky uut (
        .io_0_8_1(clk),
        .io_13_12_1(led1),
        .io_13_12_0(led2),
        .io_13_11_1(led3),
        .io_13_11_0(led4),
        .io_13_9_1(led5)
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
