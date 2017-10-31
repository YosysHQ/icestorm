module top(
  input clk,
  input rst,
  input [7:0] a,
  input [7:0] b,
  output [15:0] y);
  wire co;
  wire [31:0] out;
  SB_MAC16 i_sbmac16
    (
        .A(a),
        .B(b),
        .C(8'd0),
        .D(8'd0),
        .O(out),
        .CLK(clk),
        .IRSTTOP(rst),
        .IRSTBOT(rst),
        .ORSTTOP(rst),
        .ORSTBOT(rst),
        .AHOLD(1'b0),
        .BHOLD(1'b0),
        .CHOLD(1'b0),
        .DHOLD(1'b0),
        .OHOLDTOP(1'b0),
        .OHOLDBOT(1'b0),
        .OLOADTOP(1'b0),
        .OLOADBOT(1'b0),
        .ADDSUBTOP(1'b0),
        .ADDSUBBOT(1'b0),
        .CO(co),
        .CI(1'b0),
        .ACCUMCI(),
        .ACCUMCO(),
        .SIGNEXTIN(),
        .SIGNEXTOUT()
      );

//Config: mult_8x8_pipeline_unsigned

defparam i_sbmac16. B_SIGNED                  = 1'b0;
defparam i_sbmac16. A_SIGNED                  = 1'b0;
defparam i_sbmac16. MODE_8x8                  = 1'b1;

defparam i_sbmac16. BOTADDSUB_CARRYSELECT     = 2'b00;
defparam i_sbmac16. BOTADDSUB_UPPERINPUT      = 1'b0;
defparam i_sbmac16. BOTADDSUB_LOWERINPUT      = 2'b00;
defparam i_sbmac16. BOTOUTPUT_SELECT          = 2'b10;

defparam i_sbmac16. TOPADDSUB_CARRYSELECT     = 2'b00;
defparam i_sbmac16. TOPADDSUB_UPPERINPUT      = 1'b0;
defparam i_sbmac16. TOPADDSUB_LOWERINPUT      = 2'b00;
defparam i_sbmac16. TOPOUTPUT_SELECT          = 2'b10;

defparam i_sbmac16. PIPELINE_16x16_MULT_REG2  = 1'b0;
defparam i_sbmac16. PIPELINE_16x16_MULT_REG1  = 1'b1;
defparam i_sbmac16. BOT_8x8_MULT_REG          = 1'b1;
defparam i_sbmac16. TOP_8x8_MULT_REG          = 1'b1;
defparam i_sbmac16. D_REG                     = 1'b0;
defparam i_sbmac16. B_REG                     = 1'b1;
defparam i_sbmac16. A_REG                     = 1'b1;
defparam i_sbmac16. C_REG                     = 1'b0;

assign y = out[15:0];
endmodule