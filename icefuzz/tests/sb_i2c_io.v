module top (
    input sbclki, sbrwi, sbstbi,
    input sbadri0, sbadri1, sbadri7,
    input sbdati0, sbdati1, sbdati7,
    output sbdato0, sbdato1, sbdato7,
    output sbacko, i2cirq, i2cwkup,
    inout scl, sda
);

wire scli, sclo, scloe, sdai, sdao, sdaoe;

SB_I2C #(
  .I2C_SLAVE_INIT_ADDR("0b1111100010"),
  .BUS_ADDR74("0b0011")
) i2c_ip (
  .SBCLKI(sbclki),
  .SBRWI(sbrwi),
  .SBSTBI(sbstbi),
  
  .SBADRI0(sbadri0),
  .SBADRI1(sbadri1),
  .SBADRI7(sbadri7),
  
  .SBDATI0(sbdati0),
  .SBDATI1(sbdati1),
  .SBDATI7(sbdati7),
  
  .SBDATO0(sbdato0),
  .SBDATO1(sbdato1),
  .SBDATO7(sbdato7),
  
  .SBACKO(sbacko),
  .I2CIRQ(i2cirq),
  .I2CWKUP(i2cwkup),
  
  .SCLI(scli),
  .SCLO(sclo),
  .SCLOE(scloe),
  
  .SDAI(sdai),
  .SDAO(sdao),
  .SDAOE(sdaoe)
) /* synthesis SCL_INPUT_FILTERED=1 */;

SB_IO #(
  .PIN_TYPE(6'b101001),
  .PULLUP(1'b1)
) scl_io (
  .PACKAGE_PIN(scl),
  .OUTPUT_ENABLE(scloe),
  .D_OUT_0(sclo),
  .D_IN_0(scli)
);


SB_IO #(
  .PIN_TYPE(6'b101001),
  .PULLUP(1'b1)
) sda_io (
  .PACKAGE_PIN(sda),
  .OUTPUT_ENABLE(sdaoe),
  .D_OUT_0(sdao),
  .D_IN_0(sdai)
);

endmodule
