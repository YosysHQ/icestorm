module top (
    input clkhfpu,
    input clkhfen,
    output clkhf
);
SB_HFOSC #(

  .CLKHF_DIV("0b10")
) hfosc (
  .CLKHFPU(clkhfpu),
  .CLKHFEN(clkhfen),
  .CLKHF(clkhf)
); 
endmodule
