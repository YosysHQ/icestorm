// From nextpnr:ice40/examples/blinky
// Original file due to Claire Xenia Wolf

module blinky_tb;
    reg clk;
    always #5 clk = (clk === 1'b0);

    wire led1, led2, led3, led4, led5;

    blinky uut (
        .clki (clk),
        .\led[0] (led1),
        .\led[1] (led2),
        .\led[2] (led3),
        .\led[3] (led4),
        .\led[4] (led5)
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
