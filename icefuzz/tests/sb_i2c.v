module top (
    input sbclki, sbrwi, sbstbi,
    input sbadri0, sbadri1, sbadri7,
    input sbdati0, sbdati1, sbdati7,
    output sbdato0, sbdato1, sbdato7,
    output sbacko, i2cirq, i2cwkup,
    input scli, sdai, scli2,
    output sclo, scloe, sdao, sdaoe
);

SB_I2C #(
  .I2C_SLAVE_INIT_ADDR("0b1111100001"),
  .BUS_ADDR74("0b0001")
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
  
  .SBACKO(sbacko),
  .I2CIRQ(i2cirq),
  .I2CWKUP(i2cwkup),
  
  .SCLI(scli),
  .SCLO(sclo),
  .SCLOE(scloe),
  
  .SDAI(sdai),
  .SDAO(sdao),
  .SDAOE(sdaoe)
)
/* synthesis SDA_INPUT_DELAYED=0 */
/* synthesis SDA_OUTPUT_DELAYED=0 */
/* synthesis SCL_INPUT_FILTERED=1 */
;



SB_I2C #(
  .I2C_SLAVE_INIT_ADDR("0b1111100010"),
  .BUS_ADDR74("0b0011")
) i2c_ip2 (
  .SBCLKI(sbclki),
  .SBRWI(sbrwi),
  .SBSTBI(sbstbi),
  
  .SBADRI0(sbadri0),
  .SBADRI1(sbadri1),
  .SBADRI7(sbadri7),
  
  .SBDATI0(sbdati0),
  .SBDATI1(sbdati1),
  .SBDATI7(sbdati7),
  
  .SBDATO7(sbdato7),
  
  .SCLI(scli2)

)
/* synthesis SDA_INPUT_DELAYED=0 */
/* synthesis SDA_OUTPUT_DELAYED=0 */
/* synthesis SCL_INPUT_FILTERED=1 */
;
endmodule
