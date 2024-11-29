UltraPlus Features Documentation
================================

The ice40 UltraPlus devices have a number of new features compared to
the older LP/HX series devices, in particular:

* Internal DSP units, capable of 16-bit multiply and 32-bit accumulate.
* 1Mbit of extra single-ported RAM, in addition to the usual BRAM
* Internal hard IP cores for I2C and SPI
* 2 internal oscillators, 48MHz (with divider) and 10kHz
* 24mA constant current LED ouputs and PWM hard IP

In order to implement these new features, a significant architecural
change has been made: the left and right sides of the device are no
longer IO, but instead DSP and IPConnect tiles.

Currently icestorm and arachne-pnr support the DSPs (except for
cascading), SPRAM , internal oscillators and constant current LED
drivers. Work to support the remaining features is underway.

DSP Tiles
---------

Each MAC16 DSP comprises of 4 DSP tiles, all of which perform part of
the DSP function and have different routing bit configurations.
Structually they are similar to logic tiles, but with the DSP function
wired into where the LUTs and DFFs would be. The four types of DSP tiles
will be referred to as DSP0 through DSP3, with DSP0 at the lowest
y-position. One signal CO, is also routed through the IPConnect tile
above the DSP tile, referred to as IPCON4 in this context. The location
of signals and configuration bits is documented below.

| **Signal Assignments**

+----------+----------+----------+----------+----------+----------+
| SB_MAC16 | DSP0     | DSP1     | DSP2     | DSP3     | IPCON4   |
| port     |          |          |          |          |          |
+==========+==========+==========+==========+==========+==========+
| CLK      | --       | --       | lutff_gl | --       | --       |
|          |          |          | obal/clk |          |          |
+----------+----------+----------+----------+----------+----------+
| CE       | --       | --       | lutff_gl | --       | --       |
|          |          |          | obal/cen |          |          |
+----------+----------+----------+----------+----------+----------+
| C[7:0]   | --       | --       | --       | l        | --       |
|          |          |          |          | utff\_[7 |          |
|          |          |          |          | :0]/in_3 |          |
+----------+----------+----------+----------+----------+----------+
| C[15:8]  | --       | --       | --       | l        | --       |
|          |          |          |          | utff\_[7 |          |
|          |          |          |          | :0]/in_1 |          |
+----------+----------+----------+----------+----------+----------+
| A[7:0]   | --       | --       | l        | --       | --       |
|          |          |          | utff\_[7 |          |          |
|          |          |          | :0]/in_3 |          |          |
+----------+----------+----------+----------+----------+----------+
| A[15:8]  | --       | --       | l        | --       | --       |
|          |          |          | utff\_[7 |          |          |
|          |          |          | :0]/in_1 |          |          |
+----------+----------+----------+----------+----------+----------+
| B[7:0]   | --       | l        | --       | --       | --       |
|          |          | utff\_[7 |          |          |          |
|          |          | :0]/in_3 |          |          |          |
+----------+----------+----------+----------+----------+----------+
| B[15:8]  | --       | l        | --       | --       | --       |
|          |          | utff\_[7 |          |          |          |
|          |          | :0]/in_1 |          |          |          |
+----------+----------+----------+----------+----------+----------+
| D[7:0]   | l        | --       | --       | --       | --       |
|          | utff\_[7 |          |          |          |          |
|          | :0]/in_3 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| D[15:8]  | l        | --       | --       | --       | --       |
|          | utff\_[7 |          |          |          |          |
|          | :0]/in_1 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| IRSTTOP  | --       | lutff_gl | --       | --       | --       |
|          |          | obal/s_r |          |          |          |
+----------+----------+----------+----------+----------+----------+
| IRSTBOT  | lutff_gl | --       | --       | --       | --       |
|          | obal/s_r |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| ORSTTOP  | --       | --       | --       | lutff_gl | --       |
|          |          |          |          | obal/s_r |          |
+----------+----------+----------+----------+----------+----------+
| ORSTBOT  | --       | --       | lutff_gl | --       | --       |
|          |          |          | obal/s_r |          |          |
+----------+----------+----------+----------+----------+----------+
| AHOLD    | --       | --       | lutf     | --       | --       |
|          |          |          | f_0/in_0 |          |          |
+----------+----------+----------+----------+----------+----------+
| BHOLD    | --       | lutf     | --       | --       | --       |
|          |          | f_0/in_0 |          |          |          |
+----------+----------+----------+----------+----------+----------+
| CHOLD    | --       | --       | --       | lutf     | --       |
|          |          |          |          | f_0/in_0 |          |
+----------+----------+----------+----------+----------+----------+
| DHOLD    | lutf     | --       | --       | --       | --       |
|          | f_0/in_0 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| OHOLDTOP | --       | --       | --       | lutf     | --       |
|          |          |          |          | f_1/in_0 |          |
+----------+----------+----------+----------+----------+----------+
| OHOLDBOT | lutf     | --       | --       | --       | --       |
|          | f_1/in_0 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| A        | --       | --       | --       | lutf     | --       |
| DDSUBTOP |          |          |          | f_3/in_0 |          |
+----------+----------+----------+----------+----------+----------+
| A        | lutf     | --       | --       | --       | --       |
| DDSUBBOT | f_3/in_0 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| OLOADTOP | --       | --       | --       | lutf     | --       |
|          |          |          |          | f_2/in_0 |          |
+----------+----------+----------+----------+----------+----------+
| OLOADBOT | lutf     | --       | --       | --       | --       |
|          | f_2/in_0 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| CI       | lutf     | --       | --       | --       | --       |
|          | f_4/in_0 |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
| O[31:0]  | mult/    | mult/O   | mult/O\  | mult/O\  | --       |
|          | O\_[7:0] | \_[15:8] | _[23:16] | _[31:24] |          |
+----------+----------+----------+----------+----------+----------+
| CO       | --       | --       | --       | --       | slf_op_0 |
+----------+----------+----------+----------+----------+----------+

| **Configuration Bits**

The DSP configuration bits mostly follow the order stated in the ICE
Technology Library document, where they are described as CBIT[24:0]. For
most DSP tiles, these follow a logical order where CBIT[7:0] maps to
DSP0 CBIT[7:0]; CBIT[15:8] to DSP1 CBIT[7:0], CBIT[23:16] to DSP2
CBIT[7:0] and CBIT[24] to DSP3 CBIT0.

However, there is one location where configuration bits are swapped
between DSP tiles and IPConnect tiles. In DSP1 (0, 16) CBIT[4:1] are
used for IP such as the internal oscillator, and the DSP configuration
bits are then located in IPConnect tile (0, 19) CBIT[6:3].

The full list of configuration bits, including the changes for the DSP
at (0, 15) are described in the table below.

+-----------------------+-----------------------+-----------------------+
| Parameter             | Normal Position       | DSP (0, 15)           |
|                       |                       | Changes               |
+=======================+=======================+=======================+
| C_REG                 | DSP0.CBIT_0           |                       |
+-----------------------+-----------------------+-----------------------+
| A_REG                 | DSP0.CBIT_1           |                       |
+-----------------------+-----------------------+-----------------------+
| B_REG                 | DSP0.CBIT_2           |                       |
+-----------------------+-----------------------+-----------------------+
| D_REG                 | DSP0.CBIT_3           |                       |
+-----------------------+-----------------------+-----------------------+
| TOP_8x8_MULT_REG      | DSP0.CBIT_4           |                       |
+-----------------------+-----------------------+-----------------------+
| BOT_8x8_MULT_REG      | DSP0.CBIT_5           |                       |
+-----------------------+-----------------------+-----------------------+
| PIP                   | DSP0.CBIT_6           |                       |
| ELINE_16x16_MULT_REG1 |                       |                       |
+-----------------------+-----------------------+-----------------------+
| PIP                   | DSP0.CBIT_7           |                       |
| ELINE_16x16_MULT_REG2 |                       |                       |
+-----------------------+-----------------------+-----------------------+
| TOPOUTPUT_SELECT[0]   | DSP1.CBIT_0           |                       |
+-----------------------+-----------------------+-----------------------+
| TOPOUTPUT_SELECT[1]   | DSP1.CBIT_1           | (0, 19).CBIT_3        |
+-----------------------+-----------------------+-----------------------+
| TOPA                  | DSP1.CBIT\_[3:2]      | (0, 19).CBIT\_[5:4]   |
| DDSUB_LOWERINPUT[1:0] |                       |                       |
+-----------------------+-----------------------+-----------------------+
| TOPADDSUB_UPPERINUT   | DSP1.CBIT_4           | (0, 19).CBIT_6        |
+-----------------------+-----------------------+-----------------------+
| TOPAD                 | DSP1.CBIT\_[6:5]      |                       |
| DSUB_CARRYSELECT[1:0] |                       |                       |
+-----------------------+-----------------------+-----------------------+
| BOTOUTPUT_SELECT[0]   | DSP1.CBIT_7           |                       |
+-----------------------+-----------------------+-----------------------+
| BOTOUTPUT_SELECT[1]   | DSP2.CBIT_0           |                       |
+-----------------------+-----------------------+-----------------------+
| BOTA                  | DSP2.CBIT\_[2:1]      |                       |
| DDSUB_LOWERINPUT[1:0] |                       |                       |
+-----------------------+-----------------------+-----------------------+
| BOTADDSUB_UPPERINPUT  | DSP2.CBIT_3           |                       |
+-----------------------+-----------------------+-----------------------+
| BOTAD                 | DSP2.CBIT\_[5:4]      |                       |
| DSUB_CARRYSELECT[1:0] |                       |                       |
+-----------------------+-----------------------+-----------------------+
| MODE_8x8              | DSP2.CBIT_6           |                       |
+-----------------------+-----------------------+-----------------------+
| A_SIGNED              | DSP2.CBIT_7           |                       |
+-----------------------+-----------------------+-----------------------+
| B_SIGNED              | DSP3.CBIT_0           |                       |
+-----------------------+-----------------------+-----------------------+

Lattice document a limited number of supported configurations in the ICE
Technology Library document, and Lattice's EDIF parser will reject
designs not following a supported configuration. It is not yet known
whether unsupported configurations (such as mixed signed and unsigned)
function correctly or not.

| **Other Implementation Notes**

| All active DSP tiles, and all IPConnect tiles whether used or not,
  have some bits set which reflect their logic tile heritage. The
  LC\_\ x bits which would be used to configure the logic cell, are set
  to the below pattern for each "logic cell" (interpreting them like a
  logic tile):
| 0000111100001111 0000
| Coincidentally or not, this corresponds to a buffer passing through
  input 2 to the output. For each "cell" the cascade bit
  LC0\ x\ \_inmux02_5 is also set, effectively creating one large chain,
  as this connects input 2 to the output of the previous LUT. The DSPs
  at least will not function unless these bits are set correctly, so
  they

have some purpose and presumably indicate that the remains of a LUT are
still present. There does not seem to be any case under which iCEcube
generates a pattern other than this though.

IPConnect Tiles
---------------

IPConnect tiles are used for connections to all of the other UltraPlus
features, such as I2C/SPI, SPRAM, RGB and oscillators. Like DSP tiles,
they are structually similar to logic tiles. The outputs of IP functions
are connected to nets named slf_op_0 through slf_op_7, and the inputs
use the LUT/FF inputs in the same way as DSP tiles.

Internal Oscillators
--------------------

Both of the internal oscillators are connected through IPConnect tiles,
with their outputs optionally connected to the global networks, by
setting the "padin" extra bit (the used global networks 4 and 5 don't
have physical pins on UltraPlus devices).

SB_HFOSC
~~~~~~~~

| The CLKHFPU input connects through IPConnect tile (0, 29) input
  lutff_0/in_1; and the CLKHFEN input connects through input
  lutff_7/in_3 of the same tile.
| The CLKHF output of SB_HFOSC is connected to both IPConnect tile (0,
  28) output slf_op_7 and to the padin of glb_netwk_4.

Configuration bit CLKHF_DIV[1] maps to DSP1 tile (0, 16) config bit
CBIT_4, and CLKHF_DIV[0] maps to DSP1 tile (0, 16) config bit CBIT_3.

There is also an undocumented trimming function of the HFOSC, using the
ports TRIM0 through TRIM9. This can only be accessed directly in iCECUBE
if you modify the standard cell library. However if you set the
attribute VPP_2V5_TO_1P8V (which itself is not that well documented
either) to 1 on the top level module, then the configuration bit CBIT_5
of (0, 16) is set; and TRIM8 and TRIM4 are connected to the same net as
CLKHFPU.

TRIM[3:0] connect to (25, 28, lutff\_[7:4]/in_0) and TRIM[9:4] connect
to (25, 29, lutff\_[5:0]/in_3). CBIT_5 of (0, 16) must be set to enable
trimming. The trim range on the device used for testing was from 30.1 to
75.9 MHz. TRIM9 seemed to have no effect, the other inputs could broadly
be considered to form a binary word, however it appeared neither linear
nor even monotonic.

SB_LFOSC
~~~~~~~~

| The CLKLFPU input connects through IPConnect tile (25, 29) input
  lutff_0/in_1; and the CLKLFEN input connects through input
  lutff_7/in_3 of the same tile.
| The CLKLF output of SB_LFOSC is connected to both IPConnect tile (25,
  29) output slf_op_0 and to the padin of glb_netwk_5.

SB_LFOSC has no configuration bits.

SPRAM
-----

The UltraPlus devices have 1Mbit of extra single-ported RAM, split into
4 256kbit blocks. The full list of connections for each SPRAM block in
the 5k device is shown below, as well as the location of the 1
configuration bit which is set to enable use of that SPRAM block.

+-------------+-------------+-------------+-------------+-------------+
| Signal      | SPRAM (0,   | SPRAM (0,   | SPRAM (25,  | SPRAM (25,  |
|             | 0, 1)       | 0, 2)       | 0, 3)       | 0, 4)       |
+=============+=============+=============+=============+=============+
| A           | (0, 2,      | (0, 2,      | (25, 2,     | (25, 2,     |
| DDRESS[1:0] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [1:0]/in_1) | [7:6]/in_0) | [1:0]/in_1) | [7:6]/in_0) |
+-------------+-------------+-------------+-------------+-------------+
| A           | (0, 2,      | (0, 3,      | (25, 2,     | (25, 3,     |
| DDRESS[7:2] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [7:2]/in_1) | [5:0]/in_3) | [7:2]/in_1) | [5:0]/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| A           | (0, 2,      | (0, 3,      | (25, 2,     | (25, 3,     |
| DDRESS[9:8] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [1:0]/in_0) | [7:6]/in_3) | [1:0]/in_0) | [7:6]/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| ADD         | (0, 2,      | (0, 3,      | (25, 2,     | (25, 3,     |
| RESS[13:10] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [5:2]/in_0) | [3:0]/in_1) | [5:2]/in_0) | [3:0]/in_1) |
+-------------+-------------+-------------+-------------+-------------+
| DATAIN[7:0] | (0, 1,      | (0, 1,      | (25, 1,     | (25, 1,     |
|             | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [7:0]/in_3) | [7:0]/in_0) | [7:0]/in_3) | [7:0]/in_0) |
+-------------+-------------+-------------+-------------+-------------+
| D           | (0, 1,      | (0, 2,      | (25, 1,     | (25, 2,     |
| ATAIN[15:8] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [7:0]/in_1) | [7:0]/in_3) | [7:0]/in_1) | [7:0]/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| MA          | (0, 3,      | (0, 3,      | (25, 3,     | (25, 3,     |
| SKWREN[3:0] | lutff\_     | lutff\_     | lutff\_     | lutff\_     |
|             | [3:0]/in_0) | [7:4]/in_0) | [3:0]/in_0) | [7:4]/in_0) |
+-------------+-------------+-------------+-------------+-------------+
| WREN        | (0, 3,      | (0, 3,      | (25, 3,     | (25, 3,     |
|             | lu          | lu          | lu          | lu          |
|             | tff_4/in_1) | tff_5/in_1) | tff_4/in_1) | tff_5/in_1) |
+-------------+-------------+-------------+-------------+-------------+
| CHIPSELECT  | (0, 3,      | (0, 3,      | (25, 3,     | (25, 3,     |
|             | lu          | lu          | lu          | lu          |
|             | tff_6/in_1) | tff_7/in_1) | tff_6/in_1) | tff_7/in_1) |
+-------------+-------------+-------------+-------------+-------------+
| CLOCK       | (0, 1, clk) | (0, 2, clk) | (25, 1,     | (25, 2,     |
|             |             |             | clk)        | clk)        |
+-------------+-------------+-------------+-------------+-------------+
| STANDBY     | (0, 4,      | (0, 4,      | (25, 4,     | (25, 4,     |
|             | lu          | lu          | lu          | lu          |
|             | tff_0/in_3) | tff_1/in_3) | tff_0/in_3) | tff_1/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| SLEEP       | (0, 4,      | (0, 4,      | (25, 4,     | (25, 4,     |
|             | lu          | lu          | lu          | lu          |
|             | tff_2/in_3) | tff_3/in_3) | tff_2/in_3) | tff_3/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| POWEROFF    | (0, 4,      | (0, 4,      | (25, 4,     | (25, 4,     |
|             | lu          | lu          | lu          | lu          |
|             | tff_4/in_3) | tff_5/in_3) | tff_4/in_3) | tff_5/in_3) |
+-------------+-------------+-------------+-------------+-------------+
| D           | (0, 1,      | (0, 3,      | (25, 1,     | (25, 3,     |
| ATAOUT[7:0] | slf         | slf         | slf         | slf         |
|             | _op\_[7:0]) | _op\_[7:0]) | _op\_[7:0]) | _op\_[7:0]) |
+-------------+-------------+-------------+-------------+-------------+
| DA          | (0, 2,      | (0, 4,      | (25, 2,     | (25, 4,     |
| TAOUT[15:8] | slf         | slf         | slf         | slf         |
|             | _op\_[7:0]) | _op\_[7:0]) | _op\_[7:0]) | _op\_[7:0]) |
+-------------+-------------+-------------+-------------+-------------+
| *SP         | *(0, 1,     | *(0, 1,     | *(25, 1,    | *(25, 1,    |
| RAM_ENABLE* | CBIT_0)*    | CBIT_1)*    | CBIT_0)*    | CBIT_1)*    |
+-------------+-------------+-------------+-------------+-------------+

RGB LED Driver
--------------

The UltraPlus devices contain an internal 3-channel 2-24mA
constant-current driver intended for RGB led driving (SB_RGBA_DRV). It
is broken out onto 3 pins: 39, 40 and 41 on the QFN48 package. The LED
driver is implemented using the IPConnect tiles and is entirely seperate
to the IO cells, if the LED driver is ignored or disabled on a pin then
the pin can be used as an open-drain IO using the standard IO cell.

Note that the UltraPlus devices also have a seperate PWM generator IP
core, which would often be connected to this one to create LED effects
such as "breathing" without involving FPGA resources.

The LED driver connections are shown in the label below.

======== ======================
Signal   Net
======== ======================
CURREN   (25, 29, lutff_6/in_3)
RGBLEDEN (0, 30, lutff_1/in_1)
RGB0PWM  (0, 30, lutff_2/in_1)
RGB1PWM  (0, 30, lutff_3/in_1)
RGB2PWM  (0, 30, lutff_4/in_1)
======== ======================

The configuration bits are as follows. As well as the documented bits,
another bit RGBA_DRV_EN is set if any of the channels are enabled.

================= ====================
Parameter         Bit
================= ====================
RGBA_DRV_EN       (0, 28, CBIT_5)
RGB0_CURRENT[1:0] (0, 28, CBIT\_[7:6])
RGB0_CURRENT[5:2] (0, 29, CBIT\_[3:0])
RGB1_CURRENT[3:0] (0, 29, CBIT\_[7:4])
RGB1_CURRENT[5:4] (0, 30, CBIT\_[1:0])
RGB2_CURRENT[5:0] (0, 30, CBIT\_[7:2])
CURRENT_MODE      (0, 28, CBIT_4)
================= ====================

IO Changes
----------

The IO tiles contain a few new bits compared to earlier ice40 devices.
The bits padeb_test_0 and padeb_test_1 are set for all pins, even unused
ones, unless set as an output.

There are also some new bits used to control the pullup strength:

+-----------------------+-----------------------+-----------------------+
| Strength              | Cell 0                | Cell 1                |
+=======================+=======================+=======================+
| 3.3kΩ                 | cf_bit_32             | cf_bit_36             |
|                       | B7[10]                | B13[10]               |
+-----------------------+-----------------------+-----------------------+
| 6.8kΩ                 | cf_bit_33             | cf_bit_37             |
|                       | B6[10]                | B12[10]               |
+-----------------------+-----------------------+-----------------------+
| 10kΩ                  | cf_bit_34             | cf_bit_38             |
|                       | B7[15]                | B13[15]               |
+-----------------------+-----------------------+-----------------------+
| 100kΩ                 | !cf_bit_35            | !cf_bit_39            |
| (default)             | !B6[15]               | !B12[15]              |
+-----------------------+-----------------------+-----------------------+

I\ :sup:`3`\ C capable IO
~~~~~~~~~~~~~~~~~~~~~~~~~

The UltraPlus devices have two IO pins designed for the new MIPI
I\ :sup:`3`\ C standard (pins 23 and 25 in the SG48 package), compared
to normal IO pins they have two switchable pullups each. One of these
pullups, the weak pullup, is fixed at 100k and the other can be set to
3.3k, 6.8k or 10k using the mechanism above. The pullup control signals
do not connect directly to the IO tile, but instead connect through an
IPConnect tile.

The connections are listed below:

+-----------------------+-----------------------+-----------------------+
| Signal                | Pin 23                | Pin 25                |
|                       | (19, 31, 0)           | (19, 31, 1)           |
+=======================+=======================+=======================+
| PU_ENB                | (25, 27,              | (25, 27,              |
|                       | lutff_6/in_0)         | lutff_7/in_0)         |
+-----------------------+-----------------------+-----------------------+
| WEAK_PU_ENB           | (25, 27,              | (25, 27,              |
|                       | lutff_4/in_0)         | lutff_5/in_0)         |
+-----------------------+-----------------------+-----------------------+

Hard IP
-------

The UltraPlus devices contain three types of Hard IP: I\ :sup:`2`\ C
(SB_I2C), SPI (SB_SPI), and LED PWM generation (SB_LEDDA_IP). The
connections and configurations for each of these blocks are documented
below. Names in italics are parameters rather than actual bits, where
multiple bits are used to enable an IP they are labeled as \_ENABLE_0,
\_ENABLE_1, etc.

+-----------------------+-----------------------+-----------------------+
| Signal                | I2C                   | I2C                   |
|                       | (0, 31, 0)            | (25, 31, 0)           |
+=======================+=======================+=======================+
| SBACKO                | (0, 30, slf_op_6)     | (25, 30, slf_op_6)    |
+-----------------------+-----------------------+-----------------------+
| SBADRI0               | (0, 30, lutff_1/in_0) | (25, 30,              |
|                       |                       | lutff_1/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI1               | (0, 30, lutff_2/in_0) | (25, 30,              |
|                       |                       | lutff_2/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI2               | (0, 30, lutff_3/in_0) | (25, 30,              |
|                       |                       | lutff_3/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI3               | (0, 30, lutff_4/in_0) | (25, 30,              |
|                       |                       | lutff_4/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI4               | (0, 30, lutff_5/in_0) | (25, 30,              |
|                       |                       | lutff_5/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI5               | (0, 30, lutff_6/in_0) | (25, 30,              |
|                       |                       | lutff_6/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI6               | (0, 30, lutff_7/in_0) | (25, 30,              |
|                       |                       | lutff_7/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI7               | (0, 29, lutff_2/in_0) | (25, 29,              |
|                       |                       | lutff_2/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBCLKI                | (0, 30, clk)          | (25, 30, clk)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI0               | (0, 29, lutff_5/in_0) | (25, 29,              |
|                       |                       | lutff_5/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI1               | (0, 29, lutff_6/in_0) | (25, 29,              |
|                       |                       | lutff_6/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI2               | (0, 29, lutff_7/in_0) | (25, 29,              |
|                       |                       | lutff_7/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI3               | (0, 30, lutff_0/in_3) | (25, 30,              |
|                       |                       | lutff_0/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI4               | (0, 30, lutff_5/in_1) | (25, 30,              |
|                       |                       | lutff_5/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI5               | (0, 30, lutff_6/in_1) | (25, 30,              |
|                       |                       | lutff_6/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI6               | (0, 30, lutff_7/in_1) | (25, 30,              |
|                       |                       | lutff_7/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI7               | (0, 30, lutff_0/in_0) | (25, 30,              |
|                       |                       | lutff_0/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBDATO0               | (0, 29, slf_op_6)     | (25, 29, slf_op_6)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO1               | (0, 29, slf_op_7)     | (25, 29, slf_op_7)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO2               | (0, 30, slf_op_0)     | (25, 30, slf_op_0)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO3               | (0, 30, slf_op_1)     | (25, 30, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO4               | (0, 30, slf_op_2)     | (25, 30, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO5               | (0, 30, slf_op_3)     | (25, 30, slf_op_3)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO6               | (0, 30, slf_op_4)     | (25, 30, slf_op_4)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO7               | (0, 30, slf_op_5)     | (25, 30, slf_op_5)    |
+-----------------------+-----------------------+-----------------------+
| SBRWI                 | (0, 29, lutff_4/in_0) | (25, 29,              |
|                       |                       | lutff_4/in_0)         |
+-----------------------+-----------------------+-----------------------+
| SBSTBI                | (0, 29, lutff_3/in_0) | (25, 29,              |
|                       |                       | lutff_3/in_0)         |
+-----------------------+-----------------------+-----------------------+
| I2CIRQ                | (0, 30, slf_op_7)     | (25, 30, slf_op_7)    |
+-----------------------+-----------------------+-----------------------+
| I2CWKUP               | (0, 29, slf_op_5)     | (25, 29, slf_op_5)    |
+-----------------------+-----------------------+-----------------------+
| SCLI                  | (0, 29, lutff_2/in_1) | (25, 29,              |
|                       |                       | lutff_2/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SCLO                  | (0, 29, slf_op_3)     | (25, 29, slf_op_3)    |
+-----------------------+-----------------------+-----------------------+
| SCLOE                 | (0, 29, slf_op_4)     | (25, 29, slf_op_4)    |
+-----------------------+-----------------------+-----------------------+
| SDAI                  | (0, 29, lutff_1/in_1) | (25, 29,              |
|                       |                       | lutff_1/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SDAO                  | (0, 29, slf_op_1)     | (25, 29, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| SDAOE                 | (0, 29, slf_op_2)     | (25, 29, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| *I2C_ENABLE_0*        | *(13, 31,             | *(19, 31,             |
|                       | cbit2usealt_in_0)*    | cbit2usealt_in_0)*    |
+-----------------------+-----------------------+-----------------------+
| *I2C_ENABLE_1*        | *(12, 31,             | *(19, 31,             |
|                       | cbit2usealt_in_1)*    | cbit2usealt_in_1)*    |
+-----------------------+-----------------------+-----------------------+
| *SDA_INPUT_DELAYED*   | *(12, 31,             | *(19, 31,             |
|                       | SDA_input_delay)*     | SDA_input_delay)*     |
+-----------------------+-----------------------+-----------------------+
| *SDA_OUTPUT_DELAYED*  | *(12, 31,             | *(19, 31,             |
|                       | SDA_output_delay)*    | SDA_output_delay)*    |
+-----------------------+-----------------------+-----------------------+

+-----------------------+-----------------------+-----------------------+
| Signal                | SPI                   | SPI                   |
|                       | (0, 0, 0)             | (25, 0, 1)            |
+=======================+=======================+=======================+
| SBACKO                | (0, 20, slf_op_1)     | (25, 20, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| SBADRI0               | (0, 19, lutff_1/in_1) | (25, 19,              |
|                       |                       | lutff_1/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI1               | (0, 19, lutff_2/in_1) | (25, 19,              |
|                       |                       | lutff_2/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI2               | (0, 20, lutff_0/in_3) | (25, 20,              |
|                       |                       | lutff_0/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI3               | (0, 20, lutff_1/in_3) | (25, 20,              |
|                       |                       | lutff_1/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI4               | (0, 20, lutff_2/in_3) | (25, 20,              |
|                       |                       | lutff_2/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI5               | (0, 20, lutff_3/in_3) | (25, 20,              |
|                       |                       | lutff_3/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI6               | (0, 20, lutff_4/in_3) | (25, 20,              |
|                       |                       | lutff_4/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBADRI7               | (0, 20, lutff_5/in_3) | (25, 20,              |
|                       |                       | lutff_5/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBCLKI                | (0, 20, clk)          | (25, 20, clk)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI0               | (0, 19, lutff_1/in_3) | (25, 19,              |
|                       |                       | lutff_1/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI1               | (0, 19, lutff_2/in_3) | (25, 19,              |
|                       |                       | lutff_2/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI2               | (0, 19, lutff_3/in_3) | (25, 19,              |
|                       |                       | lutff_3/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI3               | (0, 19, lutff_4/in_3) | (25, 19,              |
|                       |                       | lutff_4/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI4               | (0, 19, lutff_5/in_3) | (25, 19,              |
|                       |                       | lutff_5/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI5               | (0, 19, lutff_6/in_3) | (25, 19,              |
|                       |                       | lutff_6/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI6               | (0, 19, lutff_7/in_3) | (25, 19,              |
|                       |                       | lutff_7/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBDATI7               | (0, 19, lutff_0/in_1) | (25, 19,              |
|                       |                       | lutff_0/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SBDATO0               | (0, 19, slf_op_1)     | (25, 19, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO1               | (0, 19, slf_op_2)     | (25, 19, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO2               | (0, 19, slf_op_3)     | (25, 19, slf_op_3)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO3               | (0, 19, slf_op_4)     | (25, 19, slf_op_4)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO4               | (0, 19, slf_op_5)     | (25, 19, slf_op_5)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO5               | (0, 19, slf_op_6)     | (25, 19, slf_op_6)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO6               | (0, 19, slf_op_7)     | (25, 19, slf_op_7)    |
+-----------------------+-----------------------+-----------------------+
| SBDATO7               | (0, 20, slf_op_0)     | (25, 20, slf_op_0)    |
+-----------------------+-----------------------+-----------------------+
| SBRWI                 | (0, 19, lutff_0/in_3) | (25, 19,              |
|                       |                       | lutff_0/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SBSTBI                | (0, 20, lutff_6/in_3) | (25, 20,              |
|                       |                       | lutff_6/in_3)         |
+-----------------------+-----------------------+-----------------------+
| MCSNO0                | (0, 21, slf_op_2)     | (25, 21, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| MCSNO1                | (0, 21, slf_op_4)     | (25, 21, slf_op_4)    |
+-----------------------+-----------------------+-----------------------+
| MCSNO2                | (0, 21, slf_op_7)     | (25, 21, slf_op_7)    |
+-----------------------+-----------------------+-----------------------+
| MCSNO3                | (0, 22, slf_op_1)     | (25, 22, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| MCSNOE0               | (0, 21, slf_op_3)     | (25, 21, slf_op_3)    |
+-----------------------+-----------------------+-----------------------+
| MCSNOE1               | (0, 21, slf_op_5)     | (25, 21, slf_op_5)    |
+-----------------------+-----------------------+-----------------------+
| MCSNOE2               | (0, 22, slf_op_0)     | (25, 22, slf_op_0)    |
+-----------------------+-----------------------+-----------------------+
| MCSNOE3               | (0, 22, slf_op_2)     | (25, 22, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| MI                    | (0, 22, lutff_0/in_1) | (25, 22,              |
|                       |                       | lutff_0/in_1)         |
+-----------------------+-----------------------+-----------------------+
| MO                    | (0, 20, slf_op_6)     | (25, 20, slf_op_6)    |
+-----------------------+-----------------------+-----------------------+
| MOE                   | (0, 20, slf_op_7)     | (25, 20, slf_op_7)    |
+-----------------------+-----------------------+-----------------------+
| SCKI                  | (0, 22, lutff_1/in_1) | (25, 22,              |
|                       |                       | lutff_1/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SCKO                  | (0, 21, slf_op_0)     | (25, 21, slf_op_0)    |
+-----------------------+-----------------------+-----------------------+
| SCKOE                 | (0, 21, slf_op_1)     | (25, 21, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| SCSNI                 | (0, 22, lutff_2/in_1) | (25, 22,              |
|                       |                       | lutff_2/in_1)         |
+-----------------------+-----------------------+-----------------------+
| SI                    | (0, 22, lutff_7/in_3) | (25, 22,              |
|                       |                       | lutff_7/in_3)         |
+-----------------------+-----------------------+-----------------------+
| SO                    | (0, 20, slf_op_4)     | (25, 20, slf_op_4)    |
+-----------------------+-----------------------+-----------------------+
| SOE                   | (0, 20, slf_op_5)     | (25, 20, slf_op_5)    |
+-----------------------+-----------------------+-----------------------+
| SPIIRQ                | (0, 20, slf_op_2)     | (25, 20, slf_op_2)    |
+-----------------------+-----------------------+-----------------------+
| SPIWKUP               | (0, 20, slf_op_3)     | (25, 20, slf_op_3)    |
+-----------------------+-----------------------+-----------------------+
| *SPI_ENABLE_0*        | *(7, 0,               | *(23, 0,              |
|                       | cbit2usealt_in_0)*    | cbit2usealt_in_0)*    |
+-----------------------+-----------------------+-----------------------+
| *SPI_ENABLE_1*        | *(7, 0,               | *(24, 0,              |
|                       | cbit2usealt_in_1)*    | cbit2usealt_in_0)*    |
+-----------------------+-----------------------+-----------------------+
| *SPI_ENABLE_2*        | *(6, 0,               | *(23, 0,              |
|                       | cbit2usealt_in_0)*    | cbit2usealt_in_1)*    |
+-----------------------+-----------------------+-----------------------+
| *SPI_ENABLE_3*        | *(6, 0,               | *(24, 0,              |
|                       | cbit2usealt_in_1)*    | cbit2usealt_in_1)*    |
+-----------------------+-----------------------+-----------------------+

+-----------------------------------+-----------------------------------+
| Signal                            | LEDDA_IP                          |
|                                   | (0, 31, 2)                        |
+===================================+===================================+
| LEDDADDR0                         | (0, 28, lutff_4/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDADDR1                         | (0, 28, lutff_5/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDADDR2                         | (0, 28, lutff_6/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDADDR3                         | (0, 28, lutff_7/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDCLK                           | (0, 29, clk)                      |
+-----------------------------------+-----------------------------------+
| LEDDCS                            | (0, 28, lutff_2/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT0                          | (0, 28, lutff_2/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT1                          | (0, 28, lutff_3/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT2                          | (0, 28, lutff_4/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT3                          | (0, 28, lutff_5/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT4                          | (0, 28, lutff_6/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT5                          | (0, 28, lutff_7/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT6                          | (0, 28, lutff_0/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDDAT7                          | (0, 28, lutff_1/in_0)             |
+-----------------------------------+-----------------------------------+
| LEDDDEN                           | (0, 28, lutff_1/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDEXE                           | (0, 28, lutff_0/in_1)             |
+-----------------------------------+-----------------------------------+
| LEDDON                            | (0, 29, slf_op_0)                 |
+-----------------------------------+-----------------------------------+
| PWMOUT0                           | (0, 28, slf_op_4)                 |
+-----------------------------------+-----------------------------------+
| PWMOUT1                           | (0, 28, slf_op_5)                 |
+-----------------------------------+-----------------------------------+
| PWMOUT2                           | (0, 28, slf_op_6)                 |
+-----------------------------------+-----------------------------------+

The I\ :sup:`2`\ C "glitch filter" (referred to as SB_FILTER_50NS) is a
seperate module from the I\ :sup:`2`\ C interface IP, with connections
as shown below:

+-----------------------+-----------------------+-----------------------+
| Signal                | SB_FILTER_50NS        | SB_FILTER_50NS        |
|                       | (25, 31, 2)           | (25, 31, 3)           |
+=======================+=======================+=======================+
| FILTERIN              | (25, 27,              | (25, 27,              |
|                       | lutff_1/in_0)         | lutff_0/in_0)         |
+-----------------------+-----------------------+-----------------------+
| FILTEROUT             | (25, 27, slf_op_2)    | (25, 27, slf_op_1)    |
+-----------------------+-----------------------+-----------------------+
| ENABLE_0              | (25, 30, CBIT_2)      | (25, 30, CBIT_5)      |
+-----------------------+-----------------------+-----------------------+
| ENABLE_1              | (25, 30, CBIT_3)      | (25, 30, CBIT_6)      |
+-----------------------+-----------------------+-----------------------+
| ENABLE_2              | (25, 30, CBIT_4)      | (25, 30, CBIT_7)      |
+-----------------------+-----------------------+-----------------------+
