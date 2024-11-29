RAM Tile Documentation
======================

Span-4 and Span-12 Wires
------------------------

Regarding the Span-4 and Span-12 Wires a RAM tile behaves exactly like a
LOGIC tile. So for simple applications that do not need the block ram
resources, the RAM tiles can be handled like a LOGIC tiles without logic
cells in them.

Block RAM Resources
-------------------

A pair or RAM tiles (odd and even y-coordinates) provides an interface
to a block ram cell. Like with LOGIC tiles, signals entering the RAM
tile have to be routed over local tracks to the block ram inputs. Tiles
with odd y-coordinates are "bottom" RAM Tiles (RAMB Tiles), and tiles
with even y-coordinates are "top" RAM Tiles (RAMT Tiles). Each pair of
RAMB/RAMT tiles implements a SB_RAM40_4K cell. The cell ports are spread
out over the two tiles as follows:

=========== =========== ===========
SB_RAM40_4K RAMB Tile   RAMT Tile
=========== =========== ===========
RDATA[15:0] RDATA[7:0]  RDATA[15:8]
RADDR[10:0] --          RADDR[10:0]
WADDR[10:0] WADDR[10:0] --
MASK[15:0]  MASK[7:0]   MASK[15:8]
WDATA[15:0] WDATA[7:0]  WDATA[15:8]
RCLKE       --          RCLKE
RCLK        --          RCLK
RE          --          RE
WCLKE       WCLKE       --
WCLK        WCLK        --
WE          WE          --
=========== =========== ===========

The configuration bit RamConfig PowerUp in the RAMB tile enables the
memory. This bit is active-low in 1k chips, i.e. an unused RAM block has
only this bit set. Note that icebox_explain.py will ignore all RAMB
tiles that only have the RamConfig PowerUp bit set.

In 8k chips the RamConfig PowerUp bit is active-high. So an unused RAM
block has all bits cleared in the 8k config bitstream.

The RamConfig CBIT\_\* bits in the RAMT tile configure the read/write
width of the memory. Those bits map to the SB_RAM40_4K cell parameters
as follows:

============= ================
SB_RAM40_4K   RAMT Config Bit
============= ================
WRITE_MODE[0] RamConfig CBIT_0
WRITE_MODE[1] RamConfig CBIT_1
READ_MODE[0]  RamConfig CBIT_2
READ_MODE[1]  RamConfig CBIT_3
============= ================

The read/write mode selects the width of the read/write port:

==== ========== ====================================================
MODE DATA Width Used WDATA/RDATA Bits
==== ========== ====================================================
0    16         15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0
1    8          14, 12, 10, 8, 6, 4, 2, 0
2    4          13, 9, 5, 1
3    2          11, 3
==== ========== ====================================================

The NegClk bit in the RAMB tile (1k die) or RAMT tile (other devices)
negates the polarity of the WCLK port, and the NegClk bit in the RAMT
(1k die) or RAMB tile (other devices) tile negates the polarity of the
RCLK port.

A logic tile sends the output of its eight logic cells to its neighbour
tiles. A RAM tile does the same thing with the RDATA outputs. Each RAMB
tile exports its RDATA[7:0] outputs and each RAMT tile exports its
RDATA[15:8] outputs via this mechanism.
