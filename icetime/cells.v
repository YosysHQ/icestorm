module AND2(A, B, O);
  input A;
  input B;
  output O;
endmodule

module CEMux(I, O);
  input I;
  output O;
endmodule

module CascadeBuf(I, O);
  input I;
  output O;
endmodule

module CascadeMux(I, O);
  input I;
  output O;
endmodule

module ClkMux(I, O);
  input I;
  output O;
endmodule

module ColCtrlBuf(I, O);
  input I;
  output O;
endmodule

module DummyBuf(I, O);
  input I;
  output O;
endmodule

module Glb2LocalMux(I, O);
  input I;
  output O;
endmodule

module GlobalMux(I, O);
  input I;
  output O;
endmodule

module ICE_CARRY_IN_MUX(carryinitout, carryinitin);
  input carryinitin;
  output carryinitout;
endmodule

module ICE_GB(GLOBALBUFFEROUTPUT, USERSIGNALTOGLOBALBUFFER);
  output GLOBALBUFFEROUTPUT;
  input USERSIGNALTOGLOBALBUFFER;
endmodule

module ICE_GB_IO(PACKAGEPIN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0, GLOBALBUFFEROUTPUT);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  output GLOBALBUFFEROUTPUT;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  inout PACKAGEPIN;
endmodule

module ICE_IO(PACKAGEPIN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  inout PACKAGEPIN;
endmodule

module ICE_IO_DLY(PACKAGEPIN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0, SCLK, SDI, CRSEL, SDO);
  input CLOCKENABLE;
  input CRSEL;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  inout PACKAGEPIN;
  input SCLK;
  input SDI;
  output SDO;
endmodule

module ICE_IO_DS(PACKAGEPIN, PACKAGEPINB, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  inout PACKAGEPIN;
  inout PACKAGEPINB;
endmodule

module ICE_IO_OD(PACKAGEPIN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  inout PACKAGEPIN;
endmodule

module ICE_IR500_DRV(IRLEDEN, IRPWM, CURREN, IRLEDEN2, IRPWM2, IRLED1, IRLED2);
  input CURREN;
  output IRLED1;
  output IRLED2;
  input IRLEDEN;
  input IRLEDEN2;
  input IRPWM;
  input IRPWM2;
endmodule

module INV(I, O);
  input I;
  output O;
endmodule

module IO_PAD(PACKAGEPIN, DOUT, DIN, OE);
  input DIN;
  output DOUT;
  input OE;
  inout PACKAGEPIN;
endmodule

module InMux(I, O);
  input I;
  output O;
endmodule

module IoInMux(I, O);
  input I;
  output O;
endmodule

module IoSpan4Mux(I, O);
  input I;
  output O;
endmodule

module IpInMux(I, O);
  input I;
  output O;
endmodule

module IpOutMux(I, O);
  input I;
  output O;
endmodule

module LocalMux(I, O);
  input I;
  output O;
endmodule

module LogicCell(carryout, lcout, carryin, clk, clkb, in0, in1, in2, in3, sr);
  input carryin;
  output carryout;
  input clk;
  input clkb;
  input in0;
  input in1;
  input in2;
  input in3;
  output lcout;
  input sr;
endmodule

module LogicCell2(carryout, lcout, carryin, clk, in0, in1, in2, in3, sr, ce);
  input carryin;
  output carryout;
  input ce;
  input clk;
  input in0;
  input in1;
  input in2;
  input in3;
  output lcout;
  input sr;
endmodule

module LogicCell40(carryout, lcout, ltout, carryin, clk, in0, in1, in2, in3, sr, ce);
  input carryin;
  output carryout;
  input ce;
  input clk;
  input in0;
  input in1;
  input in2;
  input in3;
  output lcout;
  output ltout;
  input sr;
endmodule

module Odrv12(I, O);
  input I;
  output O;
endmodule

module Odrv4(I, O);
  input I;
  output O;
endmodule

module PAD_BANK0(PAD, PADIN, PADOUT, PADOEN);
  inout PAD;
  output PADIN;
  input PADOEN;
  input PADOUT;
endmodule

module PAD_BANK1(PAD, PADIN, PADOUT, PADOEN);
  inout PAD;
  output PADIN;
  input PADOEN;
  input PADOUT;
endmodule

module PAD_BANK2(PAD, PADIN, PADOUT, PADOEN);
  inout PAD;
  output PADIN;
  input PADOEN;
  input PADOUT;
endmodule

module PAD_BANK3(PAD, PADIN, PADOUT, PADOEN);
  inout PAD;
  output PADIN;
  input PADOEN;
  input PADOUT;
endmodule

module PLL40(PLLIN, PLLOUTCORE, PLLOUTGLOBAL, EXTFEEDBACK, DYNAMICDELAY, LOCK, BYPASS, RESETB, SDI, SDO, SCLK, LATCHINPUTVALUE);
  input BYPASS;
  input [7:0] DYNAMICDELAY;
  input EXTFEEDBACK;
  input LATCHINPUTVALUE;
  output LOCK;
  input PLLIN;
  output PLLOUTCORE;
  output PLLOUTGLOBAL;
  input RESETB;
  input SCLK;
  input SDI;
  output SDO;
endmodule

module PLL40_2(PLLIN, PLLOUTCOREA, PLLOUTGLOBALA, PLLOUTCOREB, PLLOUTGLOBALB, EXTFEEDBACK, DYNAMICDELAY, LOCK, BYPASS, RESETB, SDI, SDO, SCLK, LATCHINPUTVALUE);
  input BYPASS;
  input [7:0] DYNAMICDELAY;
  input EXTFEEDBACK;
  input LATCHINPUTVALUE;
  output LOCK;
  input PLLIN;
  output PLLOUTCOREA;
  output PLLOUTCOREB;
  output PLLOUTGLOBALA;
  output PLLOUTGLOBALB;
  input RESETB;
  input SCLK;
  input SDI;
  output SDO;
endmodule

module PLL40_2F(PLLIN, PLLOUTCOREA, PLLOUTGLOBALA, PLLOUTCOREB, PLLOUTGLOBALB, EXTFEEDBACK, DYNAMICDELAY, LOCK, BYPASS, RESETB, SDI, SDO, SCLK, LATCHINPUTVALUE);
  input BYPASS;
  input [7:0] DYNAMICDELAY;
  input EXTFEEDBACK;
  input LATCHINPUTVALUE;
  output LOCK;
  input PLLIN;
  output PLLOUTCOREA;
  output PLLOUTCOREB;
  output PLLOUTGLOBALA;
  output PLLOUTGLOBALB;
  input RESETB;
  input SCLK;
  input SDI;
  output SDO;
endmodule

module PREIO(PADIN, PADOUT, PADOEN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  input PADIN;
  output PADOEN;
  output PADOUT;
endmodule

module PRE_IO(PADIN, PADOUT, PADOEN, LATCHINPUTVALUE, CLOCKENABLE, INPUTCLK, OUTPUTCLK, OUTPUTENABLE, DOUT1, DOUT0, DIN1, DIN0);
  input CLOCKENABLE;
  output DIN0;
  output DIN1;
  input DOUT0;
  input DOUT1;
  input INPUTCLK;
  input LATCHINPUTVALUE;
  input OUTPUTCLK;
  input OUTPUTENABLE;
  input PADIN;
  output PADOEN;
  output PADOUT;
endmodule

module PRE_IO_GBUF(GLOBALBUFFEROUTPUT, PADSIGNALTOGLOBALBUFFER);
  output GLOBALBUFFEROUTPUT;
  input PADSIGNALTOGLOBALBUFFER;
endmodule

module QuadClkMux(I, O);
  input I;
  output O;
endmodule

module SB_G2TBuf(I, O);
  input I;
  output O;
endmodule

module SMCCLK(CLK);
  output CLK;
endmodule

module SRMux(I, O);
  input I;
  output O;
endmodule

module Sp12to4(I, O);
  input I;
  output O;
endmodule

module Span12Mux(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s0_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s0_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s10_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s10_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s11_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s11_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s1_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s1_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s2_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s2_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s3_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s3_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s4_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s4_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s5_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s5_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s6_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s6_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s7_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s7_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s8_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s8_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s9_h(I, O);
  input I;
  output O;
endmodule

module Span12Mux_s9_v(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v(I, O);
  input I;
  output O;
endmodule

module Span4Mux(I, O);
  input I;
  output O;
endmodule

module Span4Mux_h(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s0_h(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s0_v(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s1_h(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s1_v(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s2_h(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s2_v(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s3_h(I, O);
  input I;
  output O;
endmodule

module Span4Mux_s3_v(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v(I, O);
  input I;
  output O;
endmodule

module carry_logic(cout, carry_in, a, a_bar, b, b_bar, vg_en);
  input a;
  input a_bar;
  input b;
  input b_bar;
  input carry_in;
  output cout;
  input vg_en;
endmodule

module clut4(lut4, in0, in1, in2, in3, in0b, in1b, in2b, in3b, cbit);
  input [15:0] cbit;
  input in0;
  input in0b;
  input in1;
  input in1b;
  input in2;
  input in2b;
  input in3;
  input in3b;
  output lut4;
endmodule

module coredffr(q, d, purst, S_R, cbit, clk, clkb);
  input S_R;
  input [1:0] cbit;
  input clk;
  input clkb;
  input d;
  input purst;
  output q;
endmodule

module coredffr2(q, d, purst, S_R, cbit, clk, clkb, ce);
  input S_R;
  input [1:0] cbit;
  input ce;
  input clk;
  input clkb;
  input d;
  input purst;
  output q;
endmodule

module gio2CtrlBuf(I, O);
  input I;
  output O;
endmodule

module inv_hvt(Y, A);
  input A;
  output Y;
endmodule

module logic_cell(carry_out, lc_out, carry_in, cbit, clk, clkb, in0, in1, in2, in3, prog, purst, s_r);
  input carry_in;
  output carry_out;
  input [20:0] cbit;
  input clk;
  input clkb;
  input in0;
  input in1;
  input in2;
  input in3;
  output lc_out;
  input prog;
  input purst;
  input s_r;
endmodule

module logic_cell2(carry_out, lc_out, carry_in, cbit, clk, clkb, in0, in1, in2, in3, prog, purst, s_r, ce);
  input carry_in;
  output carry_out;
  input [20:0] cbit;
  input ce;
  input clk;
  input clkb;
  input in0;
  input in1;
  input in2;
  input in3;
  output lc_out;
  input prog;
  input purst;
  input s_r;
endmodule

module logic_cell40(carry_out, lc_out, lt_out, carry_in, cbit, clk, clkb, in0, in1, in2, in3, prog, purst, s_r, ce);
  input carry_in;
  output carry_out;
  input [20:0] cbit;
  input ce;
  input clk;
  input clkb;
  input in0;
  input in1;
  input in2;
  input in3;
  output lc_out;
  output lt_out;
  input prog;
  input purst;
  input s_r;
endmodule

module o_mux(O, in0, in1, cbit, prog);
  output O;
  input cbit;
  input in0;
  input in1;
  input prog;
endmodule

module sync_clk_enable(D, NC, Q);
  input D;
  input NC;
  output Q;
endmodule

module Span4Mux_h0(I, O);
  input I;
  output O;
endmodule

module Span4Mux_h1(I, O);
  input I;
  output O;
endmodule

module Span4Mux_h2(I, O);
  input I;
  output O;
endmodule

module Span4Mux_h3(I, O);
  input I;
  output O;
endmodule

module Span4Mux_h4(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v0(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v1(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v2(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v3(I, O);
  input I;
  output O;
endmodule

module Span4Mux_v4(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h0(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h1(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h2(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h3(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h4(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h5(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h6(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h7(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h8(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h9(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h10(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h11(I, O);
  input I;
  output O;
endmodule

module Span12Mux_h12(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v0(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v1(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v2(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v3(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v4(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v5(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v6(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v7(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v8(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v9(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v10(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v11(I, O);
  input I;
  output O;
endmodule

module Span12Mux_v12(I, O);
  input I;
  output O;
endmodule

module GND(Y);
  output Y;
endmodule

module VCC(Y);
  output Y;
endmodule

module INTERCONN(I, O);
  input I;
  output O;
endmodule

module SB_RAM40_4K(RDATA, RCLK, RCLKE, RE, RADDR, WCLK, WCLKE, WE, WADDR, MASK, WDATA);
  output [15:0] RDATA;
  input RCLK, RCLKE, RE;
  input [10:0] RADDR;
  input WCLK, WCLKE, WE;
  input [10:0] WADDR;
  input [15:0] MASK, WDATA;
endmodule
