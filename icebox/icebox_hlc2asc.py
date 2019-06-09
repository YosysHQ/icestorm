#!/usr/bin/env python3
# Copyright (C) 2017  Roland Lutz
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import getopt, os, re, sys
import icebox
from icebox import re_match_cached, re_sub_cached


## Get the tile-local name of a net.
#
# \param x, y    coordinates of the tile to which the net belongs
# \param fw, fh  width and height of the tile fabric (excluding I/O tiles)
# \param net     global net name
#
# \return the tile-local name of the net if it is a span wire,
#         otherwise the unmodified net name

def untranslate_netname(x, y, fw, fh, net):
    def index(g, i, group_size):
        if g % 2 == 1:
            i = i + 1 - (i % 2) * 2
        return g * group_size + i

    match = re_match_cached(r'span4_y(\d+)_g(\d+)_(\d+)$', net)
    if match is not None:
        my = int(match.group(1))
        mw = int(match.group(2))
        mi = int(match.group(3))
        assert my == y
        assert mi >= 0 and mi < 12

        mg = x - mw + 4
        assert mg >= 0 and mg <= 4

        if x == 0:
            return 'span4_horz_%d' % index(mg, mi, 12)
        if x == fw + 1:
            return 'span4_horz_%d' % index(mg - 1, mi, 12)

        if mg == 4:
            return 'sp4_h_l_%d' % index(mg - 1, mi, 12)
        else:
            return 'sp4_h_r_%d' % index(mg, mi, 12)

    match = re_match_cached(r'span4_x(\d+)_g(\d+)_(\d+)$', net)
    if match is not None:
        mx = int(match.group(1))
        mw = int(match.group(2))
        mi = int(match.group(3))
        assert mi >= 0 and mi < 12
        mg = mw - y
        assert mg >= 0 and mg <= 4

        if y == 0:
            return 'span4_vert_%d' % index(mg - 1, mi, 12)
        if y == fh + 1:
            return 'span4_vert_%d' % index(mg, mi, 12)

        if mx == x + 1:
            assert mg < 4
            return 'sp4_r_v_b_%d' % index(mg, mi, 12)

        assert mx == x
        if mg == 4:
            return 'sp4_v_t_%d' % index(mg - 1, mi, 12)
        else:
            return 'sp4_v_b_%d' % index(mg, mi, 12)

    match = re_match_cached(r'dummy_y(\d+)_g(\d+)_(\d+)$', net)
    if match is not None:
        my = int(match.group(1))
        mw = int(match.group(2))
        mi = int(match.group(3))
        assert my == y

        mg = mw
        assert mg >= 0 and mg < 4

        return 'sp4_r_v_b_%d' % index(mg, mi, 12)

    match = re_match_cached(r'span12_y(\d+)_g(\d+)_(\d+)$', net)
    if match is not None:
        my = int(match.group(1))
        mw = int(match.group(2))
        mi = int(match.group(3))
        assert my == y
        assert mi >= 0 and mi < 2

        mg = x - mw + 12
        assert mg >= 0 and mg <= 12

        if x == 0:
            return 'span12_horz_%d' % index(mg, mi, 2)
        if x == fw + 1:
            return 'span12_horz_%d' % index(mg - 1, mi, 2)

        if mg == 12:
            return 'sp12_h_l_%d' % index(mg - 1, mi, 2)
        else:
            return 'sp12_h_r_%d' % index(mg, mi, 2)

    match = re_match_cached(r'span12_x(\d+)_g(\d+)_(\d+)$', net)
    if match is not None:
        mx = int(match.group(1))
        mw = int(match.group(2))
        mi = int(match.group(3))
        assert mx == x
        assert mi >= 0 and mi < 2

        mg = mw - y
        assert mg >= 0 and mg <= 12

        if y == 0:
            return 'span12_vert_%d' % index(mg - 1, mi, 2)
        if y == fh + 1:
            return 'span12_vert_%d' % index(mg, mi, 2)

        if mg == 12:
            return 'sp12_v_t_%d' % index(mg - 1, mi, 2)
        else:
            return 'sp12_v_b_%d' % index(mg, mi, 2)

    match = re_match_cached(r'span4_bottom_g(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mi >= 0 and mi < 4

        if x == 0:
            assert y != 0
            mg = -y + 5 - mw
            assert y + mg - 3 < 0
            return 'span4_vert_b_%d' % (mg * 4 + mi)
        else:
            assert y == 0
            mg = x + 4 - mw
            assert x - mg + 1 >= 0

            if mg == 4:
                return 'span4_horz_l_%d' % (mg * 4 + mi - 4)
            else:
                assert fw - x + mg - 4 >= 0
                return 'span4_horz_r_%d' % (mg * 4 + mi)

    match = re_match_cached(r'span4_left_g(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mi >= 0 and mi < 4

        if y == 0:
            assert x != 0
            mg = mw + x - 1
            assert x - mg + 1 < 0

            if mg == 4:
                return 'span4_horz_l_%d' % (mg * 4 + mi - 4)
            else:
                assert fw - x + mg - 4 >= 0
                return 'span4_horz_r_%d' % (mg * 4 + mi)

        else:
            assert x == 0
            mg = mw - y
            assert fh - y - mg >= 0

            if mg == 4:
                return 'span4_vert_t_%d' % (mg * 4 + mi - 4)
            else:
                assert y + mg - 3 >= 0
                return 'span4_vert_b_%d' % (mg * 4 + mi)

    match = re_match_cached(r'span4_right_g(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mi >= 0 and mi < 4

        if y == fh + 1:
            mg = mw - fh - fw + x - 1
            assert x - mg - 1 >= 0
            assert x - mg + 1 >= fw
            return 'span4_horz_r_%d' % (mg * 4 + mi)

        assert x == fw + 1
        mg = mw - y

        if mg == 4:
            assert y + mg - 1 < fh + 2
            return 'span4_vert_t_%d' % (mg * 4 + mi - 4)
        else:
            assert y + mg - 5 >= 0
            assert y + mg < fh + 3
            return 'span4_vert_b_%d' % (mg * 4 + mi)

    match = re_match_cached(r'span4_top_g(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mi >= 0 and mi < 4

        if x == fw + 1:
            assert y != 0
            mg = fw + fh + 5 - y - mw
            assert y + mg >= fh + 3

            if mg == 4:
                return 'span4_vert_t_%d' % (mg * 4 + mi - 4)
            else:
                assert y + mg - 5 >= 0
                return 'span4_vert_b_%d' % (mg * 4 + mi)

        assert y != 0
        mg = x + 4 - mw
        assert x - mg - 1 >= 0

        if mg == 4:
            return 'span4_horz_l_%d' % (mg * 4 + mi - 4)
        else:
            assert x - mg + 1 < fw
            return 'span4_horz_r_%d' % (mg * 4 + mi)

    match = re_match_cached(r'span4_bottomright(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mw % 2 == 0
        assert mi >= 0 and mi < 4

        if y == 0:
            assert x != 0
            mg = mw // 2 - fw + x - 1
            assert fw - x + mg - 4 < 0
            return 'span4_horz_r_%d' % (mg * 4 + mi)
        else:
            assert x == fw + 1
            mg = mw // 2 - y
            assert y + mg - 5 < 0
            return 'span4_vert_b_%d' % (mg * 4 + mi)

    match = re_match_cached(r'span4_topleft(\d+)_(\d+)$', net)
    if match is not None:
        mw = int(match.group(1))
        mi = int(match.group(2))
        assert mw % 2 == 0
        assert mi >= 0 and mi < 4

        if x == 0:
            assert y != 0
            mg = fh + 5 - y - mw // 2
            assert fh - y - mg < 0

            if mg == 4:
                return 'span4_vert_t_%d' % (mg * 4 + mi - 4)
            else:
                return 'span4_vert_b_%d' % (mg * 4 + mi)
        else:
            assert y == fh + 1
            mg = x + 4 - mw // 2
            assert x - mg - 1 < 0

            if mg == 4:
                return 'span4_horz_l_%d' % (mg * 4 + mi - 4)
            else:
                return 'span4_horz_r_%d' % (mg * 4 + mi)

    return net

## Check if the name of a destination net is the human-readable form
## of the \c fabout net of IO tile <tt>(x, y)</tt>.
#
# \return \c 'fabout' if it is the \c fabout net, otherwise the
#         unchanged net name

def revert_to_fabout(ic, x, y, net):
    if net.startswith('glb_netwk_'):
        for gx, gy, gi in ic.gbufin_db():
            if net == 'glb_netwk_%d' % gi and (x, y) == (gx, gy):
                return 'fabout'
        raise ParseError("{} is a global network, but not at an expected location {} {}".format(net, gx, gy))

    return net


EXPR_AND, EXPR_XOR, EXPR_OR, EXPR_TERN, EXPR_NOT, EXPR_ZERO, EXPR_ONE = range(7)

## Evaluate a list representation of a logic expression for given
## input values.
#
# This is a helper function for \ref logic_expression_to_lut.
#
# \param expr  list representation of a logic expression (see below)
# \param args  list of boolean values representing the input values
#
# \result \c False or \c True, depending on the expression and arguments
#
# Expression                             | Result
# ---------------------------------------+----------------------------------
# <tt>i</tt>                             | value of argument \a i
# <tt>(EXPR_AND, [expr, ...])</tt>       | AND operation of all expressions
# <tt>(EXPR_XOR, [expr, ...])</tt>       | XOR operation of all expressions
# <tt>(EXPR_OR, [expr, ...])</tt>        | OR operation of all expressions
# <tt>(EXPR_TERN, ex_a, ex_b, ex_c)</tt> | result of \c ex_b if \c ex_a
#                                        |   evaluates to \c True, otherwise
#                                        |   result of \c ex_c
# <tt>(EXPR_NOT, expr)</tt>              | negated result of \a expr
# <tt>(EXPR_ZERO, )</tt>                 | \c False
# <tt>(EXPR_ONE, )</tt>                  | \c True

def evaluate(expr, args):
    if type(expr) == int:
        return args[expr]

    op = expr[0]

    if op == EXPR_AND:
        assert len(expr) == 2
        for o in expr[1]:
            if not evaluate(o, args):
                return False
        return True

    if op == EXPR_XOR:
        assert len(expr) == 2
        result = False
        for o in expr[1]:
            if evaluate(o, args):
                result = not result
        return result

    if op == EXPR_OR:
        assert len(expr) == 2
        for o in expr[1]:
            if evaluate(o, args):
                return True
        return False

    if op == EXPR_TERN:
        assert len(expr) == 4
        if evaluate(expr[1], args):
            return evaluate(expr[2], args)
        else:
            return evaluate(expr[3], args)

    if op == EXPR_NOT:
        assert len(expr) == 2
        return not evaluate(expr[1], args)

    if op == EXPR_ZERO:
        assert len(expr) == 1
        return False

    if op == EXPR_ONE:
        assert len(expr) == 1
        return True

    assert False  # unknown operator

## Convert a logic expression to a LUT string.
#
# \param lut   string containing a human-readable logic expression
# \param args  list of N strings containing the names of the arguments
#
# \return a string of 2^N `0' or `1' characters representing the logic
#         of an Nx1 look-up table equivalent to the logic expression
#
# Example: logic_expression_to_lut('a & b & !c', ['a', 'b', 'c']) -> '00010000'

def logic_expression_to_lut(s, args):
    # make sure argument names are unique
    assert len(set(args)) == len(args)

    stack = [[None, None, None], [[], None, None]]
    stack[0][2] = l = []; stack[1][0].append((EXPR_OR, l))
    stack[0][1] = l = []; stack[0][2].append((EXPR_XOR, l))
    stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))
    expect_expr = True
    negate_count = 0

    i = 0
    while i < len(s):
        if s[i] == ' ':
            pass
        elif s[i] == '!':
            assert expect_expr
            negate_count += 1
        elif s[i] == '&':
            assert not expect_expr

            expect_expr = True
            negate_count = 0
        elif s[i] == '^':
            assert not expect_expr

            stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))

            expect_expr = True
            negate_count = 0
        elif s[i] == '|':
            assert not expect_expr

            stack[0][1] = l = []; stack[0][2].append((EXPR_XOR, l))
            stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))

            expect_expr = True
            negate_count = 0
        elif s[i] == '?':
            assert not expect_expr
            assert stack[1][0][-1][0] == EXPR_OR
            stack[1][0][-1] = (EXPR_TERN, stack[1][0][-1], (EXPR_OR, []),
                                                           (EXPR_OR, []))
            stack[0][2] = l = stack[1][0][-1][2][1]
            stack[0][1] = l = []; stack[0][2].append((EXPR_XOR, l))
            stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))

            expect_expr = True
            negate_count = 0
        elif s[i] == ':':
            assert not expect_expr
            assert stack[1][0][-1][0] == EXPR_TERN
            stack[0][2] = l = stack[1][0][-1][3][1]
            stack[0][1] = l = []; stack[0][2].append((EXPR_XOR, l))
            stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))

            expect_expr = True
            negate_count = 0
        elif s[i] == '(':
            assert expect_expr

            stack.insert(0, [None, None, None])

            stack[0][2] = l = []
            if negate_count % 2:
                stack[1][0].append((EXPR_NOT, (EXPR_OR, l)))
            else:
                stack[1][0].append((EXPR_OR, l))

            stack[0][1] = l = []; stack[0][2].append((EXPR_XOR, l))
            stack[0][0] = l = []; stack[0][1].append((EXPR_AND, l))

            expect_expr = True
            negate_count = 0

        elif s[i] == ')':
            assert not expect_expr
            stack.pop(0)

        elif s[i] == '0':
            assert expect_expr
            if negate_count % 2:
                stack[0][0].append((EXPR_ONE, ))
            else:
                stack[0][0].append((EXPR_ZERO, ))

            expect_expr = False
            negate_count = None

        elif s[i] == '1':
            assert expect_expr
            if negate_count % 2:
                stack[0][0].append((EXPR_ZERO, ))
            else:
                stack[0][0].append((EXPR_ONE, ))

            expect_expr = False
            negate_count = None

        else:
            assert expect_expr

            found = None
            for j, arg in enumerate(args):
                if s.startswith(arg, i):
                    found = j
                    i += len(arg)
                    break
            assert found is not None

            if negate_count % 2:
                stack[0][0].append((EXPR_NOT, found))
            else:
                stack[0][0].append(found)

            expect_expr = False
            negate_count = None
            continue

        i += 1

    assert len(stack) == 2
    return ''.join('1' if evaluate(stack[1][0][0],
                                   tuple(i & (1 << j) != 0
                                         for j in range(len(args)))) else '0'
                   for i in range(1 << len(args)))

def parse_verilog_bitvector_to_bits(in_str):
    #replace x with 0
    in_str = re_sub_cached('[xX]', '0', in_str)

    m = re_match_cached("([0-9]+)'([hdob])([0-9a-fA-F]+)", in_str)
    if m:
        num_bits = int(m.group(1))
        prefix = m.group(2)
        val_str = m.group(3)

        if prefix == 'h':
            val = eval('0x' + val_str)
        elif prefix == 'd':
            val = eval(val_str.lstrip('0'))
        elif prefix == 'o' or prefix =='b':
            val = eval('0' + prefix + val_str)

        if val.bit_length() > num_bits:
            raise ParseError("Number of bits({}) given don't match expected ({})"
                             .format(val.bit_length(), num_bits))
    else:
        val = eval('0x' + in_str)
        num_bits = len(in_str) * 4

    bit_str = bin(val)[2:]
    # zero pad
    nz = num_bits - len(bit_str)
    bit_vec = nz*['0'] + list(bit_str)
    return bit_vec

def parse_verilog_bitvector_to_hex(in_str):
    if type(in_str) == str:
        bits = parse_verilog_bitvector_to_bits(in_str)
    else:
        bits = in_str
    # pad to 4
    bits = ((4-len(bits)) % 4) * ['0'] + bits
    res = ''.join([hex(eval('0b' + ''.join(bits[ii:ii+4])))[2:] for ii in range(0, len(bits), 4)])
    return res

class ParseError(Exception):
    pass

def parse_bool(s):
    if s == 'on':
        return True
    if s == 'off':
        return False
    raise ParseError("Unable to parse '{}' as boolean".format(s))

class Main:
    def __init__(self):
        self.ic = None
        self.device = None
        #self.coldboot = None
        self.warmboot = None
        self.tiles = {}

    def read(self, fields):
        if fields[0] == 'device' and len(fields) == 4 \
                and len(fields[1]) >= 2 and fields[1][0] == '"' \
                                        and fields[1][-1] == '"' \
                and self.ic is None and self.device is None:
            self.device = fields[1][1:-1].lower()
            if self.device.startswith('lp') or self.device.startswith('hx'):
                self.device = self.device[2:]
            if self.device.startswith('1k'):
                self.ic = icebox.iceconfig()
                self.ic.setup_empty_1k()
            elif self.device.startswith('5k'):
                self.ic = icebox.iceconfig()
                self.ic.setup_empty_5k()
            elif self.device.startswith('8k'):
                self.ic = icebox.iceconfig()
                self.ic.setup_empty_8k()
            elif self.device.startswith('384'):
                self.ic = icebox.iceconfig()
                self.ic.setup_empty_384()
            else:
                raise ParseError("Unknown device {}".format(self.device))

        #elif fields[0] == 'coldboot' and fields[1] == '=' \
        #        and self.coldboot is None:
        #    # parsed but ignored (can't be represented in IceStorm .asc format)
        #    self.coldboot = parse_bool(fields[2])
        elif fields[0] == 'warmboot' and fields[1] == '=' \
                and self.warmboot is None:
            # parsed but ignored (can't be represented in IceStorm .asc format)
            self.warmboot = parse_bool(fields[2])
        else:
            raise ParseError("Unknown preamble directive {}".format(fields[0]))

    def new_block(self, fields):
        if len(fields) != 3:
            raise ParseError("Expect 3 fields for top block. Received: {}".format(fields))
        x = int(fields[1])
        y = int(fields[2])
        if (x, y) in self.tiles:
            return self.tiles[x, y]
        if fields[0] == 'logic_tile':
            if (x, y) not in self.ic.logic_tiles:
                raise ParseError("{} position({},{}) not in defined list for device".format(fields[0], x, y))
            tile = LogicTile(self.ic, x, y)
        elif fields[0] == 'ramb_tile':
            if (x, y) not in self.ic.ramb_tiles:
                raise ParseError("{} position({},{}) not in defined list for device".format(fields[0], x, y))
            tile = RAMBTile(self.ic, x, y)
        elif fields[0] == 'ramt_tile':
            if (x, y) not in self.ic.ramt_tiles:
                raise ParseError("{} position({},{}) not in defined list for device".format(fields[0], x, y))
            tile = RAMTTile(self.ic, x, y)
        elif fields[0] == 'io_tile':
            if (x, y) not in self.ic.io_tiles:
                raise ParseError("{} position({},{}) not in defined list for device".format(fields[0], x, y))
            tile = IOTile(self.ic, x, y)
        else:
            raise ParseError("Unknown tile type {}".format(fields[0]))
        self.tiles[x, y] = tile
        return tile

    def writeout(self):
        if self.ic is None:
            raise ParseError("iceconfig not set")

        # fix up IE/REN bits
        unused_ieren = set()

        for x in range(1, self.ic.max_x):
            unused_ieren.add((x, 0, 0))
            unused_ieren.add((x, 0, 1))
            unused_ieren.add((x, self.ic.max_y, 0))
            unused_ieren.add((x, self.ic.max_y, 1))

        for y in range(1, self.ic.max_y):
            unused_ieren.add((0, y, 0))
            unused_ieren.add((0, y, 1))
            unused_ieren.add((self.ic.max_x, y, 0))
            unused_ieren.add((self.ic.max_x, y, 1))

        for x0, y0, b0, x1, y1, b1 in self.ic.ieren_db():
            if (x0, y0) in self.tiles:
                io_tile = self.tiles[x0, y0]
            else:
                io_tile = IOTile(self.ic, x0, y0)
                self.tiles[x0, y0] = io_tile
            if io_tile.blocks[b0] is not None:
                io_block = io_tile.blocks[b0]
            else:
                io_block = IOBlock(io_tile, b0)
                io_tile.blocks[b0] = io_block

            if (x1, y1) in self.tiles:
                ieren_tile = self.tiles[x1, y1]
            else:
                ieren_tile = IOTile(self.ic, x1, y1)
                self.tiles[x1, y1] = ieren_tile

            if io_block.enable_input != (self.ic.device == '1k'):
                ieren_tile.apply_directive('IoCtrl', 'IE_%d' % b1)
            if io_block.disable_pull_up:
                ieren_tile.apply_directive('IoCtrl', 'REN_%d' % b1)

            unused_ieren.remove((x1, y1, b1))

        if self.ic.device == '1k':
            for x1, y1, b1 in unused_ieren:
                if (x1, y1) in self.tiles:
                    ieren_tile = self.tiles[x1, y1]
                else:
                    ieren_tile = IOTile(self.ic, x1, y1)
                    self.tiles[x1, y1] = ieren_tile
                ieren_tile.apply_directive('IoCtrl', 'IE_%d' % b1)

        # fix up RAMB power-up bits

        for x, y in self.ic.ramb_tiles:
            if (x, y) in self.tiles:
                tile = self.tiles[x, y]
            else:
                tile = RAMBTile(self.ic, x, y)
                self.tiles[x, y] = tile

            if tile.power_up != (self.ic.device == '1k'):
                tile.apply_directive('RamConfig', 'PowerUp')

        # enable column buffers
        colbuf_db = self.ic.colbuf_db()
        for x, y in list(self.tiles):
            for src, dst in self.tiles[x, y].buffers + \
                            self.tiles[x, y].routings:
                if not src.startswith('glb_netwk_'):
                    continue
                driving_xy = [(src_x, src_y)
                              for src_x, src_y, dst_x, dst_y in colbuf_db
                              if dst_x == x and dst_y == y]
                assert len(driving_xy) == 1
                driving_xy, = driving_xy

                if driving_xy not in self.tiles:
                    if driving_xy in self.ic.logic_tiles:
                        tile = LogicTile(self.ic, *driving_xy)
                    elif driving_xy in self.ic.ramb_tiles:
                        tile = RAMBTile(self.ic, *driving_xy)
                    elif driving_xy in self.ic.ramt_tiles:
                        tile = RAMTTile(self.ic, *driving_xy)
                    elif driving_xy in self.ic.io_tiles:
                        tile = IOTile(self.ic, *driving_xy)
                    else:
                        assert False
                    self.tiles[driving_xy] = tile

                self.tiles[driving_xy].apply_directive('ColBufCtrl', src)

        self.ic.write_file('/dev/stdout')

class Tile:
    def __init__(self, ic, x, y):
        self.ic = ic
        self.x = x
        self.y = y
        self.data = ic.tile(x, y)
        self.db = ic.tile_db(x, y)

        self.bits_lookup = {}
        def add_entry(entry, bits):
            entry = tuple(entry)
            if entry in self.bits_lookup:
                if self.bits_lookup[entry] == bits:
                    logging.warn(
                        "{} {} - {} (adding) != {} (existing)".format(
                            (x, y), entry, bits, self.bits_lookup[entry]))
            self.bits_lookup[entry] = bits

        for bits, *entry in self.db:
            if not ic.tile_has_entry(x, y, (bits, *entry)):
                continue
            add_entry(entry, bits)

        self.symbols = {}
        self.buffers = []
        self.routings = []
        self.bits_set = set()
        self.bits_cleared = set()

    def __str__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.ic.device, self.x, self.y)

    def apply_directive(self, *fields):
        if fields not in self.bits_lookup:
            print("Possible matches:", file=sys.stderr)
            for bits, *entry in self.db:
                if entry[0] in ("routing", "buffer"):
                    if entry[1] == fields[1]:
                        print(" ", entry, bits, file=sys.stderr)
                    elif entry[1] == fields[2]:
                        print(" ", entry, bits, file=sys.stderr)
                    elif entry[2] == fields[2]:
                        print(" ", entry, bits, file=sys.stderr)
                    elif entry[2] == fields[1]:
                        print(" ", entry, bits, file=sys.stderr)
            raise ParseError("No bit pattern for {} in {}".format(fields, self))
        bits = self.bits_lookup[fields]
        self.set_bits(bits)

    def set_bits(self, bits):
        bits_set = set()
        bits_clear = set()

        for bit in bits:
            match = re_match_cached(r'(!?)B(\d+)\[(\d+)\]$', bit)
            if not match:
                raise ValueError("invalid bit description: %s" % bit)
            if match.group(1):
                bits_clear.add((int(match.group(2)), int(match.group(3))))
            else:
                bits_set.add((int(match.group(2)), int(match.group(3))))

        if set.intersection(bits_set, bits_clear):
            raise ValueError(
                "trying to set/clear the same bit(s) at once set:{} clear:{}".format(
                    bits_set, bits_clear))

        if set.intersection(bits_set, self.bits_cleared) or \
           set.intersection(bits_clear, self.bits_set):
               raise ParseError("""\
conflicting bits {}
 setting:{:<30} - current clear:{}
clearing:{:<30} - current set  :{}""".format(
                bits,
                str(bits_set), self.bits_cleared,
                str(bits_clear), self.bits_set))

        self.bits_set.update(bits_set)
        self.bits_cleared.update(bits_clear)

        for row, col in bits_set:
            assert row < len(self.data)
            assert col < len(self.data[row])
            self.data[row] = self.data[row][:col] + '1' + \
                             self.data[row][col + 1:]

    def read(self, fields):
        if len(fields) == 3 and fields[1] == '->':
            src = untranslate_netname(self.x, self.y,
                                      self.ic.max_x - 1,
                                      self.ic.max_y - 1, fields[0])
            dst = untranslate_netname(self.x, self.y,
                                      self.ic.max_x - 1,
                                      self.ic.max_y - 1, fields[2])
            dst = revert_to_fabout(self.ic, self.x, self.y, dst)
            if (src, dst) not in self.buffers:
                self.buffers.append((src, dst))
                self.apply_directive('buffer', src, dst)
        elif len(fields) == 3 and fields[1] == '~>':
            src = untranslate_netname(self.x, self.y,
                                      self.ic.max_x - 1,
                                      self.ic.max_y - 1, fields[0])
            dst = untranslate_netname(self.x, self.y,
                                      self.ic.max_x - 1,
                                      self.ic.max_y - 1, fields[2])
            dst = revert_to_fabout(self.ic, self.x, self.y, dst)
            if (src, dst) not in self.routings:
                self.routings.append((src, dst))
                self.apply_directive('routing', src, dst)
        elif len(fields) >= 5 and (fields[1] == '->' or fields[1] == '~>'):
            self.read(fields[:3])
            self.read(fields[2:])
        elif len(fields) == 3 and fields[1] == '.sym>':
            nn = untranslate_netname(self.x, self.y,
                                      self.ic.max_x - 1,
                                      self.ic.max_y - 1, fields[0])
            net = self.ic.get_net_number( (self.x, self.y, nn) )
            self.ic.symbols.setdefault(net, set()).add(fields[2])
        else:
            raise ParseError("Unknown Tile specification format")

    def new_block(self, fields):
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class LogicTile(Tile):
    def __init__(self, ic, x, y):
        super().__init__(ic, x, y)
        self.cells = [None, None, None, None, None, None, None, None]
        self.neg_clk = False
        self.carry_in_set = False  # not in global bit list?!

    def read(self, fields):
        if fields == ['NegClk'] and not self.neg_clk:
            self.neg_clk = True
            self.apply_directive('NegClk')
        elif fields == ['CarryInSet'] and not self.carry_in_set:
            self.carry_in_set = True
            self.apply_directive('CarryInSet')
        else:
            super().read(fields)

    def new_block(self, fields):
        for i in range(8):
            if fields == ['lutff_%d' % i] and self.cells[i] is None:
                self.cells[i] = LogicCell(self, i)
                return self.cells[i]
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class LogicCell:
    def __init__(self, tile, index):
        self.tile = tile
        self.index = index
        self.lut_bits = ['0'] * 16
        self.seq_bits = ['0'] * 4

    def read(self, fields):
        if fields[0] == 'lut' and len(fields) == 2:
            self.lut_bits = fields[1]
        elif fields[0] == 'out' and len(fields) >= 3 and fields[1] == '=':
            m = re_match_cached("([0-9]+)'b([01]+)", fields[2])
            if m:
                lut_bits = parse_verilog_bitvector_to_bits(fields[2])
                # Verilog 16'bXXXX is MSB first but the bitstream wants LSB.
                self.lut_bits = list(lut_bits[::-1])
            else:
                self.lut_bits = logic_expression_to_lut(
                    ' '.join(fields[2:]), ('in_0', 'in_1', 'in_2', 'in_3'))
        elif fields == ['enable_carry']:
            self.seq_bits[0] = '1'
        elif fields == ['enable_dff']:
            self.seq_bits[1] = '1'
        elif fields == ['set_noreset']:
            self.seq_bits[2] = '1'
        elif fields == ['async_setreset']:
            self.seq_bits[3] = '1'
        elif len(fields) > 3 and (fields[1] == '->' or fields[1] == '~>'):
            self.read(fields[:3])
            self.read(fields[2:])
            return
        elif len(fields) == 3 and (fields[1] == '->' or fields[1] == '~>'):
            prefix = 'lutff_%d/' % self.index

            # Strip prefix if it is given
            if fields[0].startswith(prefix):
                fields[0] = fields[0][len(prefix):]
            if fields[-1].startswith(prefix):
                fields[-1] = fields[-1][len(prefix):]

            if fields[0] == 'out':
                self.tile.read([prefix + fields[0]] + fields[1:])
            elif fields[-1].startswith('in_'):
                self.tile.read(fields[:-1] + [prefix + fields[-1]])
            else:
                self.tile.read(fields)
            return
        elif len(fields) == 3  and fields[1] == '.sym>':
            nn = untranslate_netname(self.tile.x, self.tile.y,
                                      self.tile.ic.max_x - 1,
                                      self.tile.ic.max_y - 1, fields[0])
            net = self.tile.ic.get_net_number( (self.tile.x, self.tile.y, nn) )
            self.tile.ic.symbols.setdefault(net, set()).add(fields[2])


        bits = ''.join([
            self.lut_bits[15], self.lut_bits[12],
            self.lut_bits[11], self.lut_bits[ 8],
            self.lut_bits[ 0], self.lut_bits[ 3],
            self.lut_bits[ 4], self.lut_bits[ 7],
            self.seq_bits[ 0], self.seq_bits[ 1],
            self.lut_bits[14], self.lut_bits[13],
            self.lut_bits[10], self.lut_bits[ 9],
            self.lut_bits[ 1], self.lut_bits[ 2],
            self.lut_bits[ 5], self.lut_bits[ 6],
            self.seq_bits[ 2], self.seq_bits[ 3]
        ])
        self.tile.data[self.index * 2] = \
            self.tile.data[self.index * 2][:36] + bits[:10] + \
            self.tile.data[self.index * 2][46:]
        self.tile.data[self.index * 2 + 1] = \
            self.tile.data[self.index * 2 + 1][:36] + bits[10:] + \
            self.tile.data[self.index * 2 + 1][46:]

    def new_block(self, fields):
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class RAMData:
    def __init__(self, data):
        self.data = data

    def read(self, fields):
        if len(fields) == 1:
            self.data.append(parse_verilog_bitvector_to_hex(fields[0]))
        else:
            raise ParseError("Unexpected format in {}".format(type(self).__name__))

    def new_block(self, fields):
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class RAMBTile(Tile):
    def __init__(self, ic, x, y):
        super().__init__(ic, x, y)
        self.power_up = False

    def read(self, fields):
        if fields == ['power_up'] and not self.power_up:
            self.power_up = True
        else:
            super().read(fields)

    def new_block(self, fields):
        if fields == ['data'] and (self.x, self.y) not in self.ic.ram_data:
            self.ic.ram_data[self.x, self.y] = data = []
            return RAMData(data)
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class RAMTTile(Tile):
    def __init__(self, ic, x, y):
        super().__init__(ic, x, y)

    def read(self, fields):
        if fields == ['NegClk'] or fields[0] == 'RamConfig':
            self.apply_directive(*fields)  # TODO
        else:
            super().read(fields)

class IOTile(Tile):
    def __init__(self, ic, x, y):
        super().__init__(ic, x, y)
        self.blocks = [None, None]

    def read(self, fields):
        if len(fields) == 2 and fields[0] == 'PLL':
            self.apply_directive(*fields)  # TODO
        else:
            super().read(fields)

    def new_block(self, fields):
        if fields == ['io_0'] and self.blocks[0] is None:
            self.blocks[0] = IOBlock(self, 0)
            return self.blocks[0]
        if fields == ['io_1'] and self.blocks[1] is None:
            self.blocks[1] = IOBlock(self, 1)
            return self.blocks[1]
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

class IOBlock:
    def __init__(self, tile, index):
        self.tile = tile
        self.index = index
        self.input_pin_type = None
        self.output_pin_type = None
        self.enable_input = False
        self.disable_pull_up = False

    def read(self, fields):
        if fields[0] == 'input_pin_type' and fields[1] == '=' \
                and len(fields) == 3 and self.input_pin_type is None:
            self.input_pin_type = [
                'registered_pin',
                'simple_input_pin',
                'latched_registered_pin',
                'latched_pin'].index(fields[2])
            for i in range(2):
                if self.input_pin_type & 1 << i:
                    self.tile.apply_directive('IOB_%d' % self.index,
                                              'PINTYPE_%d' % i)
        elif fields[0] == 'output_pin_type' and fields[1] == '=' \
                and len(fields) == 3 and self.output_pin_type is None:
            self.output_pin_type = [
                'no_output',
                '1',
                '2',
                '3',
                'DDR',
                'REGISTERED',
                'simple_output_pin',
                'REGISTERED_INVERTED',
                'DDR_ENABLE',
                'REGISTERED_ENABLE',
                'OUTPUT_TRISTATE',
                'REGISTERED_ENABLE_INVERTED',
                'DDR_ENABLE_REGISTERED',
                'REGISTERED_ENABLE_REGISTERED',
                'ENABLE_REGISTERED',
                'REGISTERED_ENABLE_REGISTERED_INVERTED'].index(fields[2])
            for i in range(4):
                if self.output_pin_type & 1 << i:
                    self.tile.apply_directive('IOB_%d' % self.index,
                                              'PINTYPE_%d' % (i + 2))
        elif fields == ['enable_input'] and not self.enable_input:
            self.enable_input = True
        elif fields == ['disable_pull_up'] and not self.disable_pull_up:
            self.disable_pull_up = True
        elif fields[0] in ('GLOBAL_BUFFER_OUTPUT',
                           'io_%d/GLOBAL_BUFFER_OUTPUT' % self.index) \
                and fields[1] == '->' \
                and fields[2].startswith('glb_netwk_'):

            glb_net = int(fields[2][10:])
            padin_loc = self.tile.ic.padin_pio_db()[glb_net]

            if padin_loc != (self.tile.x, self.tile.y, self.index):
                raise ParseError("""\
GLOBAL_BUFFER_OUTPUT not valid for glb_netwk_{}
   Driver at io_tile {},{} io{}
Should be at io_tile {},{} io{}
""".format(glb_net, self.tile.x, self.tile.y, self.index, *padin_loc))
            bit = [bit for bit in self.tile.ic.extra_bits_db()
                   if self.tile.ic.extra_bits_db()[bit]
                          == ("padin_glb_netwk", fields[2][10:])]
            assert len(bit) == 1
            self.tile.ic.extra_bits.add(bit[0])
        elif len(fields) > 3 and (fields[1] == '->' or fields[1] == '~>'):
            self.read(fields[:3])
            self.read(fields[2:])
        elif len(fields) == 3 and (fields[1] == '->' or fields[1] == '~>'):
            prefix = 'io_%d/' % self.index

            # Strip prefix if it is given
            if fields[0].startswith(prefix):
                fields[0] = fields[0][len(prefix):]
            if fields[-1].startswith(prefix):
                fields[-1] = fields[-1][len(prefix):]

            if fields[0] in ('D_IN_0', 'D_IN_1'):
                self.tile.read([prefix + fields[0]] + fields[1:])
            elif fields[-1] in ('cen',
                                'D_OUT_0',
                                'D_OUT_1',
                                'inclk',
                                #'LATCH_INPUT_VALUE',
                                'outclk',
                                'OUT_ENB'):
                self.tile.read(fields[:-1] + [prefix + fields[-1]])
            else:
                self.tile.read(fields)
        elif len(fields) == 3  and fields[1] == '.sym>':
            nn = untranslate_netname(self.tile.x, self.tile.y,
                                      self.tile.ic.max_x - 1,
                                      self.tile.ic.max_y - 1, fields[0])
            net = self.tile.ic.get_net_number( (self.tile.x, self.tile.y, nn) )
            self.tile.ic.symbols.setdefault(net, set()).add(fields[2])
        else:
            raise ParseError("Unknown IOBlock specification format: {}".format(fields))


    def new_block(self, fields):
        raise ParseError("Unexpected new block in {}".format(type(self).__name__))

def main1(path):
    f = open(path, 'r')
    stack = [Main()]
    for i, line in enumerate(f):
        fields = line.split('#')[0].split()
        try:
            if not fields:
                pass  # empty line
            elif fields == ['}']:
                stack.pop()
                if not stack:
                    raise ParseError("Parsing stack empty before expected")
            elif fields[-1] == '{':
                stack.append(stack[-1].new_block(fields[:-1]))
            else:
                stack[-1].read(fields)
        except ParseError as e:
            sys.stderr.write("Parse error in line %d:\n" % (i + 1))
            sys.stderr.write(line)
            if e.args:
                sys.stderr.write("\n")
                print(*e.args, file=sys.stderr)
            sys.exit(1)
    if len(stack) != 1:
        sys.stderr.write("Parse error: unexpected end of file")
        sys.exit(1)
    f.close()

    stack[0].writeout()

def main():
    program_short_name = os.path.basename(sys.argv[0])

    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'version'])
    except getopt.GetoptError as e:
        sys.stderr.write("%s: %s\n" % (program_short_name, e.msg))
        sys.stderr.write("Try `%s --help' for more information.\n"
                         % sys.argv[0])
        sys.exit(1)

    for opt, arg in opts:
        if opt == '--help':
            sys.stderr.write("""\
Create an ASCII bitstream from a high-level bitstream representation.
Usage: %s [OPTION]... FILE

      --help            display this help and exit
      --version         output version information and exit

If you have a bug report, please file an issue on github:
  https://github.com/rlutz/icestorm/issues
""" % sys.argv[0])
            sys.exit(0)

        if opt == '--version':
            sys.stderr.write("""\
icebox_hlc2asc - create an ASCII bitstream from a high-level representation
Copyright (C) 2017 Roland Lutz

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
""")
            sys.exit(0)

    if not args:
        sys.stderr.write("%s: missing argument\n" % (program_short_name))
        sys.stderr.write("Try `%s --help' for more information.\n"
                         % sys.argv[0])
        sys.exit(1)

    if len(args) != 1:
        sys.stderr.write("%s: too many arguments\n" % (program_short_name))
        sys.stderr.write("Try `%s --help' for more information.\n"
                         % sys.argv[0])
        sys.exit(1)

    if args[0] == '-':
        main1('/dev/stdin')
    else:
        main1(args[0])

if __name__ == '__main__':
    main()
