module top
(
 input  en,
 input  rgbleden,
 input  r_in,
 input  g_in,
 input  b_in,
 output r_led,
 output g_led,
 output b_led);

   wire ledpu;

SB_LED_DRV_CUR
LED_DRV_CUR(.EN(en),
            .LEDPU(ledpu));

   wire rgbpu;

SB_RGB_DRV
  RGB_DRV(.RGBLEDEN(rgbleden),
          .RGBPU(rgbpu),
          .RGB0PWM(r_in),
          .RGB1PWM(g_in),
          .RGB2PWM(b_in),
          .RGB0(r_led),
          .RGB1(g_led),
          .RGB2(b_led));

defparam RGB_DRV.RGB0_CURRENT = "0b000011";
defparam RGB_DRV.RGB1_CURRENT = "0b001111";
defparam RGB_DRV.RGB2_CURRENT = "0b111111";

assign rgbpu = ledpu;

endmodule
