module top(input clk,
           output [4:0] led,
           input [7:0] pmod,
           //spi interface
           output spi_miso,
           input spi_mosi,
           input spi_clk,
           input spi_cs_n);
 
   //parameter SPI_MODE = 1; // CPOL = 0, CPHA = 1

   reg [8:0] fifo = 8'd0;
   reg [2:0] counter = 0;

   always @ (negedge spi_clk)
   begin
      fifo <= {fifo[7:0],spi_mosi}; // loopback fifo
      if(counter < 4'd7) begin
            counter <= counter + 1;
      end
      else begin
          counter <= 0;
          led <={fifo[3:0],spi_mosi};
      end
   end

   always @ (posedge spi_clk)
   begin
      spi_miso<=fifo[7]; // loopback
      //spi_miso<=pmod[counter]; //logic analyzer
   end

endmodule // top
