module top(
  input clk,
  input rstn,
  output LED1,
  output LED2);
  
wire reset = !rstn;
  
wire [15:0] A    = 16'd999;
wire [15:0] B    = 16'd12345;
wire [31:0] RES  = 32'd12332655;

wire [31:0] dsp_out;

SB_MAC16 i_sbmac16
  (
    .A(A),
    .B(B),
    .C(16'b0),
    .D(16'b0),
    .CLK(clk),
    .CE(1'b1),
    .IRSTTOP(reset),
    .IRSTBOT(reset),
    .ORSTTOP(reset),
    .ORSTBOT(reset),
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
    .CO(),
    .CI(1'b0),
    .O(dsp_out)
  );

//16x16 => 32 unsigned pipelined multiply
defparam i_sbmac16. B_SIGNED                  = 1'b0;
defparam i_sbmac16. A_SIGNED                  = 1'b0;
defparam i_sbmac16. MODE_8x8                  = 1'b0;

defparam i_sbmac16. BOTADDSUB_CARRYSELECT     = 2'b00;
defparam i_sbmac16. BOTADDSUB_UPPERINPUT      = 1'b0;
defparam i_sbmac16. BOTADDSUB_LOWERINPUT      = 2'b00;
defparam i_sbmac16. BOTOUTPUT_SELECT          = 2'b11;

defparam i_sbmac16. TOPADDSUB_CARRYSELECT     = 2'b00;
defparam i_sbmac16. TOPADDSUB_UPPERINPUT      = 1'b0;
defparam i_sbmac16. TOPADDSUB_LOWERINPUT      = 2'b00;
defparam i_sbmac16. TOPOUTPUT_SELECT          = 2'b11;

defparam i_sbmac16. PIPELINE_16x16_MULT_REG2  = 1'b1;
defparam i_sbmac16. PIPELINE_16x16_MULT_REG1  = 1'b1;
defparam i_sbmac16. BOT_8x8_MULT_REG          = 1'b1;
defparam i_sbmac16. TOP_8x8_MULT_REG          = 1'b1;
defparam i_sbmac16. D_REG                     = 1'b0;
defparam i_sbmac16. B_REG                     = 1'b1;
defparam i_sbmac16. A_REG                     = 1'b1;
defparam i_sbmac16. C_REG                     = 1'b0;

assign LED1 = (dsp_out == RES) ? 1'b1 : 1'b0;
assign LED2 = 1'b0;



endmodule