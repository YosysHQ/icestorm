LOGIC Tile Documentation
========================

Span-4 and Span-12 Wires
------------------------

The *span-4* and *span-12* wires are the main interconnect resource in
iCE40 FPGAs. They "span" (have a length of) 4 or 12 cells in horizontal
or vertical direction.

All routing resources in iCE40 are directional tristate buffers. The
bits marked routing use the all-zeros config pattern for tristate, while
the bits marked buffer have a dedicated buffer-enable bit, which is 1 in
all non-tristate configurations.

Span-4 Horizontal
~~~~~~~~~~~~~~~~~

|Span-4 Horizontal|

The image on the right shows the *horizontal span-4* wires of a logic or
ram cell (click to enlarge).

On the left side of the cell there are 48 connections named sp4_h_l_0 to
sp4_h_l_47. The lower 36 of those wires are connected to sp4_h_r_12 to
sp4_h_r_47 on the right side of the cell. (IceStorm normalizes this wire
names to sp4_h_r_0 to sp4_h_r_35. Note: the Lattice tools use a
different normalization scheme for this wire names.) The wires
connecting the left and right horizontal span-4 ports are pairwise
crossed-out.

The wires sp4_h_l_36 to sp4_h_l_47 terminate in the cell as do the wires
sp4_h_r_0 to sp4_h_r_11.

This wires "span" 4 cells, i.e. they connect 5 cells if you count the
cells on both ends of the wire.

For example, the wire sp4_h_r_0 in cell (x, y) has the following names:

================ ===================== =====================
Cell Coordinates sp4_h_l\_\* wire name sp4_h_r\_\* wire name
================ ===================== =====================
x, y             --                    sp4_h_r_0
x+1, y           sp4_h_l_0             sp4_h_r_13
x+2, y           sp4_h_l_13            sp4_h_r_24
x+3, y           sp4_h_l_24            sp4_h_r_37
x+4, y           sp4_h_l_37            --
================ ===================== =====================

Span-4 Vertical
~~~~~~~~~~~~~~~

|Span-4 Vertical|

The image on the right shows the *vertical span-4* wires of a logic or
ram cell (click to enlarge).

Similar to the horizontal span-4 wires there are 48 connections on the
top (sp4_v_t_0 to sp4_v_t_47) and 48 connections on the bottom
(sp4_v_b_0 to sp4_v_b_47). The wires sp4_v_t_0 to sp4_v_t_35 are
connected to sp4_v_b_12 to sp4_v_b_47 (with pairwise crossing out). Wire
names are normalized to sp4_v_b_12 to sp4_v_b_47.

But in addition to that, each cell also has access to sp4_v_b_0 to
sp4_v_b_47 of its right neighbour. This are the wires sp4_r_v_b_0 to
sp4_r_v_b_47. So over all a single vertical span-4 wire connects 9
cells. For example, the wire sp4_v_b_0 in cell (x, y) has the following
names:

+----------------+----------------+----------------+----------------+
| Cell           | sp4_v_t\_\*    | sp4_v_b\_\*    | sp4_r_v_b\_\*  |
| Coordinates    | wire name      | wire name      | wire name      |
+================+================+================+================+
| x, y           | --             | sp4_v_b_0      | --             |
+----------------+----------------+----------------+----------------+
| x, y-1         | sp4_v_t_0      | sp4_v_b_13     | --             |
+----------------+----------------+----------------+----------------+
| x, y-2         | sp4_v_t_13     | sp4_v_b_24     | --             |
+----------------+----------------+----------------+----------------+
| x, y-3         | sp4_v_t_24     | sp4_v_b_37     | --             |
+----------------+----------------+----------------+----------------+
| x, y-4         | sp4_v_t_37     | --             | --             |
+----------------+----------------+----------------+----------------+
| x-1, y         | --             | --             | sp4_r_v_b_0    |
+----------------+----------------+----------------+----------------+
| x-1, y-1       | --             | --             | sp4_r_v_b_13   |
+----------------+----------------+----------------+----------------+
| x-1, y-2       | --             | --             | sp4_r_v_b_24   |
+----------------+----------------+----------------+----------------+
| x-1, y-3       | --             | --             | sp4_r_v_b_37   |
+----------------+----------------+----------------+----------------+

Span-12 Horizontal and Vertical
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to the span-4 wires there are also longer horizontal and
vertical span-12 wires.

There are 24 connections sp12_v_t_0 to sp12_v_t_23 on the top of the
cell and 24 connections sp12_v_b_0 to sp12_v_b_23 on the bottom of the
cell. The wires sp12_v_t_0 to sp12_v_t_21 are connected to sp12_v_b_2 to
sp12_v_b_23 (with pairwise crossing out). The connections sp12_v_b_0,
sp12_v_b_1, sp12_v_t_22, and sp12_v_t_23 terminate in the cell. Wire
names are normalized to sp12_v_b_2 to sp12_v_b_23.

There are also 24 connections sp12_h_l_0 to sp12_h_l_23 on the left of
the cell and 24 connections sp12_h_r_0 to sp12_h_r_23 on the right of
the cell. The wires sp12_h_l_0 to sp12_h_l_21 are connected to
sp12_h_r_2 to sp12_h_r_23 (with pairwise crossing out). The connections
sp12_h_r_0, sp12_h_r_1, sp12_h_l_22, and sp12_h_l_23 terminate in the
cell. Wire names are normalized to sp12_v_r_2 to sp12_h_r_23.

Local Tracks
------------

The *local tracks* are the gateway to the logic cell inputs. Signals
from the span-wires and the logic cell outputs of the eight neighbour
cells can be routed to the local tracks and signals from the local
tracks can be routed to the logic cell inputs.

Each logic tile has 32 local tracks. They are organized in 4 groups of 8
wires each: local_g0_0 to local_g3_7.

The span wires, global signals, and neighbour outputs can be routed to
the local tracks. But not all of those signals can be routed to all of
the local tracks. Instead there is a different mix of 16 signals for
each local track.

The buffer driving the local track has 5 configuration bits. One enable
bit and 4 bits that select the input wire. For example for local_g0_0
(copy&paste from the bitstream doku):

+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| B0[14] | B1[14] | B1[15] | B1[16] | B1[17] | Function | Source-Net     | Destination-Net |
+========+========+========+========+========+==========+================+=================+
| 0      | 0      | 0      | 0      | 1      | buffer   | sp4_r_v_b_24   | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 0      | 0      | 1      | 1      | buffer   | sp12_h_r_8     | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 0      | 1      | 0      | 1      | buffer   | neigh_op_bot_0 | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 0      | 1      | 1      | 1      | buffer   | sp4_v_b_16     | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 1      | 0      | 0      | 1      | buffer   | sp4_r_v_b_35   | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 1      | 0      | 1      | 1      | buffer   | sp12_h_r_16    | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 1      | 1      | 0      | 1      | buffer   | neigh_op_top_0 | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 0      | 1      | 1      | 1      | 1      | buffer   | sp4_h_r_0      | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 0      | 0      | 0      | 1      | buffer   | lutff_0/out    | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 0      | 0      | 1      | 1      | buffer   | sp4_v_b_0      | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 0      | 1      | 0      | 1      | buffer   | neigh_op_lft_0 | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 0      | 1      | 1      | 1      | buffer   | sp4_h_r_8      | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 1      | 0      | 0      | 1      | buffer   | neigh_op_bnr_0 | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 1      | 0      | 1      | 1      | buffer   | sp4_v_b_8      | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 1      | 1      | 0      | 1      | buffer   | sp12_h_r_0     | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+
| 1      | 1      | 1      | 1      | 1      | buffer   | sp4_h_r_16     | local_g0_0      |
+--------+--------+--------+--------+--------+----------+----------------+-----------------+

Then the signals on the local tracks can be routed to the input pins of
the logic cells. Like before, not every local track can be routed to
every logic cell input pin. Instead there is a different mix of 16 local
track for each logic cell input. For example for lutff_0/in_0:

====== ====== ====== ====== ====== ======== ========== ===============
B0[26] B1[26] B1[27] B1[28] B1[29] Function Source-Net Destination-Net
====== ====== ====== ====== ====== ======== ========== ===============
0      0      0      0      1      buffer   local_g0_0 lutff_0/in_0
0      0      0      1      1      buffer   local_g2_0 lutff_0/in_0
0      0      1      0      1      buffer   local_g1_1 lutff_0/in_0
0      0      1      1      1      buffer   local_g3_1 lutff_0/in_0
0      1      0      0      1      buffer   local_g0_2 lutff_0/in_0
0      1      0      1      1      buffer   local_g2_2 lutff_0/in_0
0      1      1      0      1      buffer   local_g1_3 lutff_0/in_0
0      1      1      1      1      buffer   local_g3_3 lutff_0/in_0
1      0      0      0      1      buffer   local_g0_4 lutff_0/in_0
1      0      0      1      1      buffer   local_g2_4 lutff_0/in_0
1      0      1      0      1      buffer   local_g1_5 lutff_0/in_0
1      0      1      1      1      buffer   local_g3_5 lutff_0/in_0
1      1      0      0      1      buffer   local_g0_6 lutff_0/in_0
1      1      0      1      1      buffer   local_g2_6 lutff_0/in_0
1      1      1      0      1      buffer   local_g1_7 lutff_0/in_0
1      1      1      1      1      buffer   local_g3_7 lutff_0/in_0
====== ====== ====== ====== ====== ======== ========== ===============

The 8 global nets on the iCE40 can be routed to the local track via the
glb2local_0 to glb2local_3 nets using a similar two-stage process. The
logic block clock-enable and set-reset inputs can be driven directly
from one of 4 global nets or from one of 4 local tracks. The logic block
clock input can be driven from any of the global nets and from a few
local tracks. See the bitstream documentation for details.

Logic Block
-----------

Each logic tile has a logic block containing 8 logic cells. Each logic
cell contains a 4-input LUT, a carry unit and a flip-flop. Clock, clock
enable, and set/reset inputs are shared along the 8 logic cells. So is
the bit that configures positive/negative edge for the flip flops. But
the three configuration bits that specify if the flip flop should be
used, if it is set or reset by the set/reset input, and if the set/reset
is synchronous or asynchronous exist for each logic cell individually.

Each LUT *i* has four input wires lutff\_\ i/in_0 to lutff\_\ i/in_3.
Input lutff\_\ i/in_3 can be configured to be driven by the carry output
of the previous logic cell, or by carry_in_mux in case of *i*\ =0. Input
lutff\_\ i/in_2 can be configured to be driven by the output of the
previous LUT for *i*>0 (LUT cascade). The LUT uses its 4 input signals
to calculate lutff\_\ i/lout. The signal is then passed through the
built-in FF and becomes lutff\_\ i/out. With the exception of LUT
cascades, only the signal after the FF is visible from outside the logic
block.

The carry unit calculates lutff\_\ i/cout = lutff\_\ i/in_1 +
lutff\_\ i/in_2 + lutff\_\ (i-1)/cout > 1. In case of *i*\ =0,
carry_in_mux is used as third input. carry_in_mux can be configured to
be constant 0, 1 or the lutff_7/cout signal from the logic tile below.

Part of the functionality described above is documented as part of the
routing bitstream documentation (see the buffers for lutff\_ inputs).
The NegClk bit switches all 8 FFs in the tile to negative edge mode. The
CarryInSet bit drives the carry_in_mux high (it defaults to low when not
driven via the buffer from carry_in).

The remaining functions of the logic cell are configured via the LC\_\ i
bits. This are 20 bit per logic cell. We have arbitrarily labeled those
bits as follows:

+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| Label           | LC_0   | LC_1   | LC_2   | LC_3   | LC_4   | LC_5    | LC_6    | LC_7    |
+=================+========+========+========+========+========+=========+=========+=========+
| LC\_\ *i*\ [0]  | B0[36] | B2[36] | B4[36] | B6[36] | B8[36] | B10[36] | B12[36] | B14[36] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [1]  | B0[37] | B2[37] | B4[37] | B6[37] | B8[37] | B10[37] | B12[37] | B14[37] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [2]  | B0[38] | B2[38] | B4[38] | B6[38] | B8[38] | B10[38] | B12[38] | B14[38] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [3]  | B0[39] | B2[39] | B4[39] | B6[39] | B8[39] | B10[39] | B12[39] | B14[39] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [4]  | B0[40] | B2[40] | B4[40] | B6[40] | B8[40] | B10[40] | B12[40] | B14[40] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [5]  | B0[41] | B2[41] | B4[41] | B6[41] | B8[41] | B10[41] | B12[41] | B14[41] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [6]  | B0[42] | B2[42] | B4[42] | B6[42] | B8[42] | B10[42] | B12[42] | B14[42] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [7]  | B0[43] | B2[43] | B4[43] | B6[43] | B8[43] | B10[43] | B12[43] | B14[43] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [8]  | B0[44] | B2[44] | B4[44] | B6[44] | B8[44] | B10[44] | B12[44] | B14[44] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [9]  | B0[45] | B2[45] | B4[45] | B6[45] | B8[45] | B10[45] | B12[45] | B14[45] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [10] | B1[36] | B3[36] | B5[36] | B7[36] | B9[36] | B11[36] | B13[36] | B15[36] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [11] | B1[37] | B3[37] | B5[37] | B7[37] | B9[37] | B11[37] | B13[37] | B15[37] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [12] | B1[38] | B3[38] | B5[38] | B7[38] | B9[38] | B11[38] | B13[38] | B15[38] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [13] | B1[39] | B3[39] | B5[39] | B7[39] | B9[39] | B11[39] | B13[39] | B15[39] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [14] | B1[40] | B3[40] | B5[40] | B7[40] | B9[40] | B11[40] | B13[40] | B15[40] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [15] | B1[41] | B3[41] | B5[41] | B7[41] | B9[41] | B11[41] | B13[41] | B15[41] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [16] | B1[42] | B3[42] | B5[42] | B7[42] | B9[42] | B11[42] | B13[42] | B15[42] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [17] | B1[43] | B3[43] | B5[43] | B7[43] | B9[43] | B11[43] | B13[43] | B15[43] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [18] | B1[44] | B3[44] | B5[44] | B7[44] | B9[44] | B11[44] | B13[44] | B15[44] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+
| LC\_\ *i*\ [19] | B1[45] | B3[45] | B5[45] | B7[45] | B9[45] | B11[45] | B13[45] | B15[45] |
+-----------------+--------+--------+--------+--------+--------+---------+---------+---------+

LC\_\ i\ [8] is the CarryEnable bit. This bit must be set if the carry
logic is used.

LC\_\ i\ [9] is the DffEnable bit. It enables the output flip-flop for
the LUT.

LC\_\ i\ [18] is the Set_NoReset bit. When this bit is set then the
set/reset signal will set, not reset the flip-flop.

LC\_\ i\ [19] is the AsyncSetReset bit. When this bit is set then the
set/reset signal is asynchronous to the clock.

The LUT implements the following truth table:

==== ==== ==== ==== =============
in_3 in_2 in_1 in_0 lout
==== ==== ==== ==== =============
0    0    0    0    LC\_\ i\ [4]
0    0    0    1    LC\_\ i\ [14]
0    0    1    0    LC\_\ i\ [15]
0    0    1    1    LC\_\ i\ [5]
0    1    0    0    LC\_\ i\ [6]
0    1    0    1    LC\_\ i\ [16]
0    1    1    0    LC\_\ i\ [17]
0    1    1    1    LC\_\ i\ [7]
1    0    0    0    LC\_\ i\ [3]
1    0    0    1    LC\_\ i\ [13]
1    0    1    0    LC\_\ i\ [12]
1    0    1    1    LC\_\ i\ [2]
1    1    0    0    LC\_\ i\ [1]
1    1    0    1    LC\_\ i\ [11]
1    1    1    0    LC\_\ i\ [10]
1    1    1    1    LC\_\ i\ [0]
==== ==== ==== ==== =============

LUT inputs that are not connected to anything are driven low. The
set/reset signal is also driven low if not connected to any other
driver, and the clock enable signal is driven high when left
unconnected.

.. |Span-4 Horizontal| image:: _static/images/sp4h.svg
   :height: 200px
   :target: _static/images/sp4h.svg
.. |Span-4 Vertical| image:: _static/images/sp4v.svg
   :height: 200px
   :target: _static/images/sp4v.svg
