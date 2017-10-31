module top(
  input clk,
  input [13:0] addr,
  input [7:0] din,
  input wren,
  input cs,
  output [7:0] dout
);

SB_SPRAM256KA spram_i
  (
    .ADDRESS(addr),
    .DATAIN(din),
    .MASKWREN(4'b1111),
    .WREN(wren),
    .CHIPSELECT(cs),
    .CLOCK(clk),
    .STANDBY(1'b0),
    .SLEEP(1'b0),
    .POWEROFF(1'b0),
    .DATAOUT(dout)
  );
  

endmodule