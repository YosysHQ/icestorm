module top(
    input r_in,
    input g_in,
    input b_in,
    output r_led,
    output g_led,
    output b_led);
  
  wire curren;
  wire rgbleden;
  
  SB_RGBA_DRV RGBA_DRIVER (
    .CURREN(curren),
    .RGBLEDEN(rgbleden),
    .RGB0PWM(r_in),
    .RGB1PWM(r_in),
    .RGB2PWM(r_in),
    .RGB0(r_led),
    .RGB1(g_led),
    .RGB2(b_led)
  );

defparam RGBA_DRIVER.CURRENT_MODE = "0b0";
defparam RGBA_DRIVER.RGB0_CURRENT = "0b000011";
defparam RGBA_DRIVER.RGB1_CURRENT = "0b001111";
defparam RGBA_DRIVER.RGB2_CURRENT = "0b111111";

assign curren = 1'b1;
assign rgbleden = 1'b1;


endmodule