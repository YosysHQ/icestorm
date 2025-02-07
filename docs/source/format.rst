Bitstream File Format Documentation
===================================

General Description of the File Format
--------------------------------------

The bitstream file starts with the bytes 0xFF 0x00, followed by a
sequence of zero-terminated comment strings, followed by 0x00 0xFF.
However, there seems to be a bug in the Lattice "bitstream" tool that
moves the terminating 0x00 0xFF a few bytes into the comment string in
some cases.

After the comment sections the token 0x7EAA997E (MSB first) starts the
actual bit stream. The bitstream consists of one-byte commands, followed
by a payload word, followed by an optional block of data. The MSB nibble
of the command byte is the command opcode, the LSB nibble is the length
of the command payload in bytes. The commands that do not require a
payload are using the opcode 0, with the command encoded in the payload
field. Note that this "payload" in this context refers to a single
integer argument, not the blocks of data that follows the command in
case of the CRAM and BRAM commands.

The following commands are known:

+-----------------------------------+-----------------------------------+
| Opcode                            | Description                       |
+===================================+===================================+
| 0                                 | payload=1: Write CRAM Data        |
|                                   +-----------------------------------+
|                                   | payload=2: Read BRAM Data         |
|                                   +-----------------------------------+
|                                   | payload=3: Write BRAM Data        |
|                                   +-----------------------------------+
|                                   | payload=4: Read BRAM Data         |
|                                   +-----------------------------------+
|                                   | payload=5: Reset CRC              |
|                                   +-----------------------------------+
|                                   | payload=6: Wakeup                 |
|                                   +-----------------------------------+
|                                   | payload=8: Reboot                 |
+-----------------------------------+-----------------------------------+
| 1                                 | Set bank number                   |
+-----------------------------------+-----------------------------------+
| 2                                 | CRC check                         |
+-----------------------------------+-----------------------------------+
| 4                                 | Set boot address                  |
+-----------------------------------+-----------------------------------+
| 5                                 | Set internal oscillator frequency |
|                                   | range                             |
|                                   +-----------------------------------+
|                                   | payload=0: low                    |
|                                   +-----------------------------------+
|                                   | payload=1: medium                 |
|                                   +-----------------------------------+
|                                   | payload=2: high                   |
+-----------------------------------+-----------------------------------+
| 6                                 | Set bank width (16-bits, MSB      |
|                                   | first)                            |
+-----------------------------------+-----------------------------------+
| 7                                 | Set bank height (16-bits, MSB     |
|                                   | first)                            |
+-----------------------------------+-----------------------------------+
| 8                                 | Set bank offset (16-bits, MSB     |
|                                   | first)                            |
+-----------------------------------+-----------------------------------+
| 9                                 | payload=0: Disable warm boot      |
|                                   +-----------------------------------+
|                                   | payload=16: Enable cold boot      |
|                                   +-----------------------------------+
|                                   | payload=32: Enable warm boot      |
+-----------------------------------+-----------------------------------+

Use iceunpack -vv to display the commands as they are interpreted by the
tool.

Note: The format itself seems to be very flexible. At the moment it is
unclear what the FPGA devices will do when presented with a bitstream
that use the commands in a different way than the bitstreams generated
by the lattice tools.

Writing SRAM content
--------------------

Most bytes in the bitstream are SRAM data bytes that should be written
to the various SRAM banks in the FPGA. The following sequence is used to
program an SRAM cell:

-  Set bank width (opcode 6)
-  Set bank height (opcode 7)
-  Set bank offset (opcode 8)
-  Set bank number (opcode 1)
-  CRAM or BRAM Data Command
-  (width \* height / 8) data bytes
-  two zero bytes

The bank width and height parameters reflect the width and height of the
SRAM bank. A large SRAM can be written in smaller chunks. In this case
height parameter may be smaller and the offset parameter reflects the
vertical start position.

There are four CRAM and four BRAM banks in an iCE40 FPGA. The different
devices from the family use different widths and heights, but the same
number of banks.

The CRAM banks hold the configuration bits for the FPGA fabric and hard
IP blocks, the BRAM corresponds to the contents of the block ram
resources.

The ordering of the data bits is in MSB first row-major order.

Organization of the CRAM
------------------------

|Mapping of tile config bits to 2D CRAM|

The chip is organized into four quadrants. Each CRAM memory bank
contains the configuration bits for one quadrant. The address 0 is
always the corner of the quadrant, i.e. in one quadrant the bit
addresses increase with the tile x/y coordinates, in another they
increase with the tile x coordinate but decrease with the tile y
coordinate, and so on.

For an iCE40 1k device, that has 12 x 16 tiles (not counting the io
tiles), the CRAM bank 0 is the one containing the corner tile (1 1), the
CRAM bank 1 contains the corner tile (1 16), the CRAM bank 2 contains
the corner tile (12 1) and the CRAM bank 3 contains the corner tile (12
16). The entire CRAM of such a device is depicted on the right (bank 0
is in the lower left corner in blue/green).

The checkerboard pattern in the picture visualizes which bits are
associated with which tile. The height of the configuration block is 16
for all tile types, but the width is different for each tile type. IO
tiles have configurations that are 18 bits wide, LOGIC tiles are 54 bits
wide, and RAM tiles are 42 bits wide. (Notice the two slightly smaller
columns for the RAM tiles.)

The IO tiles on the top and bottom of the chip use a strange permutation
pattern for their bits. It can be seen in the picture that their columns
are spread out horizontally. What cannot be seen in the picture is the
columns also are not in order and the bit positions are vertically
permuted as well. The CramIndexConverter class in icepack.cc
encapsulates the calculations that are necessary to convert between
tile-relative bit addresses and CRAM bank-relative bit addresses.

The black pixels in the image correspond to CRAM bits that are not
associated with any IO, LOGIC or RAM tile. Some of them are unused,
others are used by hard IPs or other global resources. The iceunpack
tool reports such bits, when set, with the ".extra_bit bank x y"
statement in the ASCII output format.

Organization of the BRAM
------------------------

This part of the documentation has not been written yet.

CRC Check
---------

The CRC is a 16 bit CRC. The (truncated) polynomial is 0x1021
(CRC-16-CCITT). The "Reset CRC" command sets the CRC to 0xFFFF. No zero
padding is performed.

.. |Mapping of tile config bits to 2D CRAM| image:: _static/images/checkerboard.png
   :height: 200px
   :target: _static/images/checkerboard.png
