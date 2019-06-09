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
from icebox import re_match_cached

GLB_NETWK_EXTERNAL_BLOCKS = [(13, 8, 1), (0, 8, 1), (7, 17, 0), (7, 0, 0),
                             (0, 9, 0), (13, 9, 0), (6, 0, 1), (6, 17, 1)]
GLB_NETWK_INTERNAL_TILES = [(7, 0), (7, 17), (13, 9), (0, 9),
                            (6, 17), (6, 0), (0, 8), (13, 8)]


## Get the global name of a net.
#
# \param x, y    coordinates of the tile to which the net belongs
# \param fw, fh  width and height of the tile fabric (excluding I/O tiles)
# \param net     net name
#
# \return the global name of the net if it is a span wire, otherwise
#         the unmodified net name
#
# There are 46624 span wires on the 1k (not counting dummies):
#
# span4_x[1..12]_g[1..20]_[0..11]
# span4_y[1..16]_g[1..16]_[0..11]
# span12_x[1..12]_g[1..28]_[0..1]
# span12_y[1..16]_g[1..24]_[0..1]
#
# span4_left_g[3..16]_[0..3]
# span4_right_g[5..18]_[0..3]
# span4_bottom_g[3..12]_[0..3]
# span4_top_g[5..14]_[0..3]
#
# span4_topleft[2,4,6,8]_[0..3]
# span4_bottomright[2,4,6,8]_[0..3]
#
# dummy_y[1..16]_g[0..3]_[0..11]
#
# "Dummy" nets are horizontal accesses to non-existing vertical span
# wires on the right edge which are listed by icebox but don't
# actually connect to anything outside the tile itself.

def translate_netname(x, y, fw, fh, net):
    def group_and_index(s, group_size):
        n = int(s)
        g = n // group_size
        i = n % group_size
        if g % 2 == 1:
            i = i + 1 - (i % 2) * 2
        return g, i

    # logic and RAM tiles

    match = re_match_cached(r'sp4_h_r_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        return 'span4_y%d_g%d_%d' % (y, x - g + 4, i)
    match = re_match_cached(r'sp4_h_l_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        return 'span4_y%d_g%d_%d' % (y, x - g + 3, i)

    match = re_match_cached(r'sp4_v_b_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        return 'span4_x%d_g%d_%d' % (x, y + g, i)
    match = re_match_cached(r'sp4_v_t_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        return 'span4_x%d_g%d_%d' % (x, y + g + 1, i)
    match = re_match_cached(r'sp4_r_v_b_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        if x == fw:
            # this net doesn't connect anywhere
            return 'dummy_y%d_g%d_%d' % (y, g, i)
        else:
            return 'span4_x%d_g%d_%d' % (x + 1, y + g, i)

    match = re_match_cached(r'sp12_h_r_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        return 'span12_y%d_g%d_%d' % (y, x - g + 12, i)
    match = re_match_cached(r'sp12_h_l_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        return 'span12_y%d_g%d_%d' % (y, x - g + 11, i)

    match = re_match_cached(r'sp12_v_b_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        return 'span12_x%d_g%d_%d' % (x, y + g, i)
    match = re_match_cached(r'sp12_v_t_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        return 'span12_x%d_g%d_%d' % (x, y + g + 1, i)

    # I/O tiles

    match = re_match_cached(r'span4_horz_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        if x == 0:
            return 'span4_y%d_g%d_%d' % (y, x - g + 4, i)
        else:
            return 'span4_y%d_g%d_%d' % (y, x - g + 3, i)

    match = re_match_cached(r'span4_vert_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 12)
        if y == 0:
            return 'span4_x%d_g%d_%d' % (x, y + g + 1, i)
        else:
            return 'span4_x%d_g%d_%d' % (x, y + g, i)

    match = re_match_cached(r'span12_horz_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        if x == 0:
            return 'span12_y%d_g%d_%d' % (y, x - g + 12, i)
        else:
            return 'span12_y%d_g%d_%d' % (y, x - g + 11, i)

    match = re_match_cached(r'span12_vert_(\d+)$', net)
    if match is not None:
        g, i = group_and_index(match.group(1), 2)
        if y == 0:
            return 'span12_x%d_g%d_%d' % (x, y + g + 1, i)
        else:
            return 'span12_x%d_g%d_%d' % (x, y + g, i)

    # I/O tiles - peripheral wires

    match = re_match_cached(r'span4_horz_r_(\d+)$', net)
    if match is not None:
        n = int(match.group(1)); g = n // 4; i = n % 4
        if y == 0:
            if fw - x + g - 4 < 0:
                return 'span4_bottomright%d_%d' % ((fw - x + 1 + g) * 2, i)
            elif x - g + 1 < 0:
                return 'span4_left_g%d_%d' % (-x + 1 + g, i)
            else:
                return 'span4_bottom_g%d_%d' % (x + 4 - g, i)
        else:
            if x - g - 1 < 0:
                return 'span4_topleft%d_%d' % ((x + 4 - g) * 2, i)
            elif x - g + 1 >= fw:
                return 'span4_right_g%d_%d' % (fh + fw - x + 1 + g, i)
            else:
                return 'span4_top_g%d_%d' % (x + 4 - g, i)

    match = re_match_cached(r'span4_horz_l_(\d+)$', net)
    if match is not None:
        n = int(match.group(1)); g = n // 4; i = n % 4
        if y == 0:
            if x - g < 0:
                return 'span4_left_g%d_%d' % (-x + 2 + g, i)
            else:
                return 'span4_bottom_g%d_%d' % (x + 3 - g, i)
        else:
            if x - g - 2 < 0:
                return 'span4_topleft%d_%d' % ((x + 3 - g) * 2, i)
            else:
                return 'span4_top_g%d_%d' % (x + 3 - g, i)

    match = re_match_cached(r'span4_vert_b_(\d+)$', net)
    if match is not None:
        n = int(match.group(1)); g = n // 4; i = n % 4
        if x == 0:
            if y + g - 3 < 0:
                return 'span4_bottom_g%d_%d' % (-y + 5 - g, i)
            if fh - y - g < 0:
                return 'span4_topleft%d_%d' % ((fh + 5 - y - g) * 2, i)
            else:
                return 'span4_left_g%d_%d' % (y + g, i)
        else:
            if y + g - 5 < 0:
                return 'span4_bottomright%d_%d' % ((y + g) * 2, i)
            elif y + g >= fh + 3:
                return 'span4_top_g%d_%d' % (fw + fh + 5 - y - g, i)
            else:
                return 'span4_right_g%d_%d' % (y + g, i)

    match = re_match_cached(r'span4_vert_t_(\d+)$', net)
    if match is not None:
        n = int(match.group(1)); g = n // 4; i = n % 4
        if x == 0:
            if fh - y - g - 1 < 0:
                return 'span4_topleft%d_%d' % ((fh + 4 - y - g) * 2, i)
            else:
                return 'span4_left_g%d_%d' % (y + g + 1, i)
        else:
            if y + g >= fh + 2:
                return 'span4_top_g%d_%d' % (fw + fh + 4 - y - g, i)
            else:
                return 'span4_right_g%d_%d' % (y + g + 1, i)

    return net

## Return the human-readable name of the \c fabout net of IO tile
## <tt>(x, y)</tt>.

def lookup_fabout(x, y):
    if (x, y) in GLB_NETWK_INTERNAL_TILES:
        return 'glb_netwk_%d' % GLB_NETWK_INTERNAL_TILES.index((x, y))

    return 'fabout'


## Remove an argument from a LUT string and an associated list of
## argument names.
#
# This is a helper function for \ref lut_to_logic_expression.
#
# \param lut   string of 2^N `0' or `1' characters representing the
#              logic of an Nx1 look-up table
# \param args  list of N strings containing the human-readable names
#              of the arguments
# \param i     index of the argument to remove
# \param keep  boolean value indicating which value of the removed
#              argument is to be assumed in the resulting LUT
#
# \return a new pair <tt>(lut, args)</tt> with the argument removed

def discard_argument(lut, args, i, keep):
    assert len(lut) == 1 << len(args)
    assert i >= 0 and i < len(args)
    return ''.join(bit for j, bit in enumerate(lut)
                   if (j & (1 << i) != 0) == keep), \
           args[:i] + args[i + 1:]

## Negate a tuple representation of a logic expression.
#
# This is a helper function for \ref lut_to_logic_expression.

def negate_expr(expr):
    if len(expr) == 2:
        op, a = expr
        assert op == 'not'
        return a
    if len(expr) != 3:
        return 'not', expr
    a, op, b = expr
    if op == 'and':
        return negate_expr(a), 'or', negate_expr(b)
    if op == 'or':
        return negate_expr(a), 'and', negate_expr(b)
    assert op == 'xor'
    if len(a) == 2 and a[0] == 'not':
        return a[1], op, b
    if len(b) == 2 and b[0] == 'not':
        return a, op, b[1]
    return negate_expr(a), op, b

## Convert a tuple representation of a logic expression into a string.
#
# This is a helper function for \ref lut_to_logic_expression.
#
# \param expr        the expression to convert
# \param parenthize  whether a compound expression should be
#                    surrounded by parentheses

def stringify(expr, parenthize):
    if type(expr) == str:
        return expr
    assert type(expr) == tuple

    if len(expr) == 2:
        op, a = expr
        assert op == 'not'
        assert type(a) == str
        return "!" + a

    if len(expr) == 5:
        a, op0, b, op1, c = expr
        assert op0 == '?' and op1 == ':'
        s = '%s ? %s : %s' % (stringify(a, False), stringify(b, False),
                                                   stringify(c, False))
        if parenthize:
            return '(%s)' % s
        return s

    assert len(expr) == 3

    a, op, b = expr
    l = [a, b]
    i = 0
    while i < len(l):
        if type(l[i]) == tuple and len(l[i]) == 3 and l[i][1] == op:
            l = l[:i] + [l[i][0], l[i][2]] + l[i + 1:]
        else:
            i += 1

    if op == 'and':
        op = '&'
    elif op == 'xor':
        op = '^'
    elif op == 'or':
        op = '|'

    s = (' %s ' % op).join(stringify(x, True) for x in l)
    if parenthize:
        return '(%s)' % s
    return s

## Remove arguments which don't affect the result from a LUT string
## and an associated list of argument names.
#
# This is a helper function for \ref lut_to_logic_expression.
#
# \param lut   string of 2^N `0' or `1' characters representing the
#              logic of an Nx1 look-up table
# \param args  list of N strings containing the human-readable names
#              of the arguments
#
# \return a new pair <tt>(lut, args)</tt> with all unused arguments
#         removed

def discard_unused_arguments(lut, args):
    assert len(lut) == 1 << len(args)
    i = 0
    while i < len(args):
        diff = False
        for j in range(len(lut)):
            if j & (1 << i) == 0 and lut[j] != lut[j | (1 << i)]:
                diff = True
        if not diff:
            lut, args = discard_argument(lut, args, i, False)
        else:
            i += 1
    return lut, args

## Convert a LUT string to a logic expression.
#
# \param lut   string of 2^N `0' or `1' characters representing the
#              logic of an Nx1 look-up table
# \param args  list of N strings containing the human-readable names
#              of the arguments
#
# \return a string containing a human-readable logic expression
#         equivalent to the look-up table
#
# Example: lut_to_logic_expression('00010000', ['a', 'b', 'c']) -> 'a & b & !c'

def lut_to_logic_expression(lut, args):
    lut, args = discard_unused_arguments(lut, args)

    # filter out independent top-level arguments
    toplevel_args = []
    i = 0
    while i < len(args) and len(args) >= 2:
        ai_0 = set(bit for j, bit in enumerate(lut) if j & (1 << i) == 0)
        ai_1 = set(bit for j, bit in enumerate(lut) if j & (1 << i) != 0)
        assert len(ai_0) == 2 or len(ai_1) == 2

        if len(ai_0) == 1:
            # expression is constant if this argument is 0
            # e = (...) & arg  or  e = (...) | !arg
            if tuple(ai_0)[0] == '0':
                toplevel_args.append(('and', args[i]))
            else:
                toplevel_args.append(('or', ('not', args[i])))
            lut, args = discard_argument(lut, args, i, True)
            i = 0
            continue

        if len(ai_1) == 1:
            # expression is constant if this argument is 1
            # e = (...) & !arg  or  e = (...) | arg
            if tuple(ai_1)[0] == '0':
                toplevel_args.append(('and', ('not', args[i])))
            else:
                toplevel_args.append(('or', args[i]))
            lut, args = discard_argument(lut, args, i, False)
            i = 0
            continue

        i += 1

    i = 0
    while i < len(args) and len(args) >= 2:
        is_xor = True
        for j in range(len(lut)):
            if j & (1 << i) == 0 and lut[j] == lut[j | (1 << i)]:
                is_xor = False
                break

        if is_xor:
            toplevel_args.append(('xor', args[i]))
            lut, args = discard_argument(lut, args, i, False)
            continue

        i += 1

    # detect simple top-level ternary conditions
    i = 0
    while i < len(args) and len(args) >= 3:
        j = i + 1
        while j < len(args):
            ai_0_aj_0 = set(bit for k, bit in enumerate(lut)
                            if k & (1 << i) == 0 and k & (1 << j) == 0)
            ai_0_aj_1 = set(bit for k, bit in enumerate(lut)
                            if k & (1 << i) == 0 and k & (1 << j) != 0)
            ai_1_aj_0 = set(bit for k, bit in enumerate(lut)
                            if k & (1 << i) != 0 and k & (1 << j) == 0)
            ai_1_aj_1 = set(bit for k, bit in enumerate(lut)
                            if k & (1 << i) != 0 and k & (1 << j) != 0)
            assert len(ai_0_aj_0) == 2 or len(ai_0_aj_1) == 2 or \
                   len(ai_1_aj_0) == 2 or len(ai_1_aj_1) == 2

            if (len(ai_0_aj_0) == 2 or len(ai_0_aj_1) == 2) and \
               (len(ai_1_aj_0) == 2 or len(ai_1_aj_1) == 2) and \
               (len(ai_0_aj_0) == 2 or len(ai_1_aj_0) == 2) and \
               (len(ai_0_aj_1) == 2 or len(ai_1_aj_1) == 2):
                j += 1
                continue

            ai_doesnt_matter_for_aj_0 = True
            ai_doesnt_matter_for_aj_1 = True
            aj_doesnt_matter_for_ai_0 = True
            aj_doesnt_matter_for_ai_1 = True

            for k in range(len(lut)):
                if k & (1 << i) != 0 or k & (1 << j) != 0:
                    continue
                if lut[k] != lut[k | (1 << i)]:
                    ai_doesnt_matter_for_aj_0 = False
                if lut[k | (1 << j)] != lut[k | (1 << i) | (1 << j)]:
                    ai_doesnt_matter_for_aj_1 = False
                if lut[k] != lut[k | (1 << j)]:
                    aj_doesnt_matter_for_ai_0 = False
                if lut[k | (1 << i)] != lut[k | (1 << i) | (1 << j)]:
                    aj_doesnt_matter_for_ai_1 = False

            if len(ai_0_aj_0) == 1 and len(ai_0_aj_1) == 1 and \
                   aj_doesnt_matter_for_ai_1:
                assert tuple(ai_0_aj_0)[0] != tuple(ai_0_aj_1)[0]
                if tuple(ai_0_aj_0)[0] == '0':
                    toplevel_args.append((args[i], '?', ':', args[j]))
                else:
                    toplevel_args.append((args[i], '?', ':', ('not', args[j])))
                lut, args = discard_argument(lut, args, i, True)

                # break loops
                i = len(args)
                j = len(args)
                break

            if len(ai_1_aj_0) == 1 and len(ai_1_aj_1) == 1 and \
                   aj_doesnt_matter_for_ai_0:
                assert tuple(ai_1_aj_0)[0] != tuple(ai_1_aj_1)[0]
                if tuple(ai_1_aj_0)[0] == '0':
                    toplevel_args.append((args[i], '?', args[j], ':'))
                else:
                    toplevel_args.append((args[i], '?', ('not', args[j]), ':'))
                lut, args = discard_argument(lut, args, i, False)

                # break loops
                i = len(args)
                j = len(args)
                break

            if len(ai_0_aj_0) == 1 and len(ai_1_aj_0) == 1 and \
                   ai_doesnt_matter_for_aj_1:
                assert tuple(ai_0_aj_0)[0] != tuple(ai_1_aj_0)[0]
                if tuple(ai_0_aj_0)[0] == '0':
                    toplevel_args.append((args[j], '?', ':', args[i]))
                else:
                    toplevel_args.append((args[j], '?', ':', ('not', args[i])))
                lut, args = discard_argument(lut, args, j, True)

                # break loops
                i = len(args)
                j = len(args)
                break

            if len(ai_0_aj_1) == 1 and len(ai_1_aj_1) == 1 and \
                   ai_doesnt_matter_for_aj_0:
                assert tuple(ai_0_aj_1)[0] != tuple(ai_1_aj_1)[0]
                if tuple(ai_0_aj_1)[0] == '0':
                    toplevel_args.append((args[j], '?', args[i], ':'))
                else:
                    toplevel_args.append((args[j], '?', ('not', args[i]), ':'))
                lut, args = discard_argument(lut, args, j, False)

                # break loops
                i = len(args)
                j = len(args)
                break

            j += 1
        i += 1

    lut, args = discard_unused_arguments(lut, args)

    # group pairwise isolated arguments
    i = 0
    while i < len(args):
        j = i + 1
        while j < len(args):
            ai_doesnt_matter_for_aj_0 = True
            ai_doesnt_matter_for_aj_1 = True
            aj_doesnt_matter_for_ai_0 = True
            aj_doesnt_matter_for_ai_1 = True
            both_dont_matter_if_equal = True
            both_dont_matter_if_unequal = True

            for k in range(len(lut)):
                if k & (1 << i) != 0 or k & (1 << j) != 0:
                    continue
                if lut[k] != lut[k | (1 << i)]:
                    ai_doesnt_matter_for_aj_0 = False
                if lut[k | (1 << j)] != lut[k | (1 << i) | (1 << j)]:
                    ai_doesnt_matter_for_aj_1 = False
                if lut[k] != lut[k | (1 << j)]:
                    aj_doesnt_matter_for_ai_0 = False
                if lut[k | (1 << i)] != lut[k | (1 << i) | (1 << j)]:
                    aj_doesnt_matter_for_ai_1 = False
                if lut[k] != lut[k | (1 << i) | (1 << j)]:
                    both_dont_matter_if_equal = False
                if lut[k | (1 << i)] != lut[k | (1 << j)]:
                    both_dont_matter_if_unequal = False

            # There are five possibilities of coupled arguments: one
            # of the four combinations differs from the other three,
            # or they are xor'ed

            if ai_doesnt_matter_for_aj_1 and \
               aj_doesnt_matter_for_ai_1 and \
               both_dont_matter_if_unequal:
                # special case is ai=0 aj=0
                args = args[:i] + ((args[i], 'or', args[j]), ) + args[i + 1:]
                lut, args = discard_argument(lut, args, j, False)
                j = i + 1
            elif ai_doesnt_matter_for_aj_1 and \
                 aj_doesnt_matter_for_ai_0 and \
                 both_dont_matter_if_equal:
                # special case is ai=1 aj=0
                args = args[:i] + ((args[i], 'and', negate_expr(args[j])), ) + \
                       args[i + 1:]
                lut, args = discard_argument(lut, args, j, False)
                j = i + 1
            elif ai_doesnt_matter_for_aj_0 and \
                 aj_doesnt_matter_for_ai_1 and \
                 both_dont_matter_if_equal:
                # special case is ai=0 aj=1
                args = args[:i] + ((args[i], 'or', negate_expr(args[j])), ) + \
                       args[i + 1:]
                lut, args = discard_argument(lut, args, j, True)
                j = i + 1
            elif ai_doesnt_matter_for_aj_0 and \
                 aj_doesnt_matter_for_ai_0 and \
                 both_dont_matter_if_unequal:
                # special case is ai=1 aj=1
                args = args[:i] + ((args[i], 'and', args[j]), ) + args[i + 1:]
                lut, args = discard_argument(lut, args, j, True)
                j = i + 1

            elif both_dont_matter_if_equal and \
                 both_dont_matter_if_unequal:
                args = args[:i] + ((args[i], 'xor', args[j]), ) + args[i + 1:]
                lut, args = discard_argument(lut, args, j, False)
                j = i + 1
            else:
                j += 1
        i += 1

    # collect the result

    if not args:
        # constant expression
        assert len(lut) == 1
        return lut

    negate_result = lut.count('1') > lut.count('0')
    if negate_result:
        lut = ''.join('1' if bit == '0' else '0' for bit in lut)

    result = None
    for i, bit in enumerate(lut):
        if bit == '0':
            continue
        expr = None
        for j, arg in enumerate(args):
            if i & (1 << j) == 0:
                arg = negate_expr(arg)
            if expr is None:
                expr = arg
            else:
                expr = (expr, 'and', arg)
        if result is None:
            result = expr
        else:
            result = (result, 'or', expr)

    if negate_result:
        result = negate_expr(result)

    for toplevel_arg in reversed(toplevel_args):
        if len(toplevel_arg) != 4:
            result = tuple(reversed(toplevel_arg)) + (result, )
        elif toplevel_arg[2] == ':':
            result = toplevel_arg[0:2] + (result, ) + toplevel_arg[2:4]
        else:
            assert toplevel_arg[3] == ':'
            result = toplevel_arg + (result, )

    return stringify(result, False)


class Fabric:
    def __init__(self, ic):
        self.ic = ic
        self.tiles = {}
        #self.colbuf = set()

        io_blocks = {}
        ieren_blocks = {}

        for x0, y0, b0, x1, y1, b1 in self.ic.ieren_db():
            i = IOBlock()
            assert (x0, y0, b0) not in io_blocks
            io_blocks[x0, y0, b0] = i
            assert (x1, y1, b1) not in ieren_blocks
            ieren_blocks[x1, y1, b1] = i

        for xy in ic.io_tiles:
            assert xy not in self.tiles
            self.tiles[xy] = IOTile(self, xy,
                                    (io_blocks.pop((xy[0], xy[1], 0), None),
                                     io_blocks.pop((xy[0], xy[1], 1), None)),
                                    (ieren_blocks.pop((xy[0], xy[1], 0), None),
                                     ieren_blocks.pop((xy[0], xy[1], 1), None)))
        assert not io_blocks
        assert not ieren_blocks

        for xy in ic.logic_tiles:
            assert xy not in self.tiles
            self.tiles[xy] = LogicTile(self, xy)

        for xy in ic.ramb_tiles:
            assert xy not in self.tiles
            self.tiles[xy] = RAMBTile(self, xy)

        for xy in ic.ramt_tiles:
            assert xy not in self.tiles
            self.tiles[xy] = RAMTTile(self, xy)

        for x, y in self.tiles:
            assert x >= 0 and x <= self.ic.max_x
            assert y >= 0 and y <= self.ic.max_y
        for x in range(self.ic.max_x + 1):
            for y in range(self.ic.max_y + 1):
                should_exist = (x > 0 and x < self.ic.max_x) or \
                               (y > 0 and y < self.ic.max_y)
                assert ((x, y) in self.tiles) == should_exist

        for xy in ic.ram_data:
            assert type(self.tiles.get(xy, None)) == RAMBTile

        #colbuf_db = ic.colbuf_db()
        #for x, y, i in self.colbuf:
        #    exists = False
        #    for src_x, src_y, dst_x, dst_y in colbuf_db:
        #        if src_x != x or src_y != y:
        #            continue
        #        assert (dst_x, dst_y) in self.tiles
        #        assert not self.tiles[dst_x, dst_y].colbuf[i]
        #        self.tiles[dst_x, dst_y].colbuf[i] = True
        #        exists = True
        #    assert exists
        #
        #for xy in self.tiles:
        #    for br in self.tiles[xy].buffer_and_routing:
        #        if br[0].startswith('glb_netwk_'):
        #            assert self.tiles[xy].colbuf[int(br[0][10:])]

        for bit in self.ic.extra_bits:
            directive, arg = self.ic.lookup_extra_bit(bit)
            assert directive == 'padin_glb_netwk'
            x, y, n = GLB_NETWK_EXTERNAL_BLOCKS[int(arg)]
            assert type(self.tiles.get((x, y), None)) == IOTile
            block = self.tiles[x, y].io_blocks[n]
            assert block is not None
            block.padin_glb_netwk = True

    def printout(self, options):
        print('device "%s" %d %d' % (self.ic.device, self.ic.max_x - 1,
                                                     self.ic.max_y - 1))

        print('')
        # internal_configuration_oscillator_frequency = low | medium | high
        #print('coldboot = off')
        print('warmboot = on')  # IceStorm assumes this to be always on

        for xy in sorted(self.tiles.keys(), key = lambda xy: (xy[1], xy[0])):
            self.tiles[xy].printout(options)

class Tile:
    def __init__(self, fabric, xy, data, is_logic_block):
        self.fabric = fabric
        self.ic = fabric.ic
        self.xy = xy
        self.data = data

        self.buffer_and_routing = set()
        self.used_buffer_and_routing = set()
        self.text = set()
        self.bitinfo = list()
        self.unknown_bits = False

        x, y = xy
        db = self.ic.tile_db(x, y)
        mapped_bits = set()

        # 'data' is a list of strings containing a series of zeroes and
        # ones.  'bits' is a set of strings containing an entry
        # "B<row>[<col>]" or "!B<row>[<col>]" for each bit.

        bits = set()
        for k, line in enumerate(data):
            for i in range(len(line)):
                if line[i] == '1':
                    bits.add('B%d[%d]' % (k, i))
                else:
                    bits.add('!B%d[%d]' % (k, i))

        for entry in db:
            # LC bits don't have a useful entry in the database; skip them
            # for now
            if re_match_cached(r'LC_', entry[1]):
                continue

            # some nets have different names depending on the tile; filter
            # out non-applicable net names
            if entry[1] in ('routing', 'buffer') and (
                    not self.ic.tile_has_net(x, y, entry[2]) or
                    not self.ic.tile_has_net(x, y, entry[3])):
                continue

            # are all required bits set/unset?
            match = True
            for bit in entry[0]:
                if not bit in bits:
                    match = False
            if match:
                for bit in entry[0]:
                    mapped_bits.add(bit)

            if entry[1:] == ['IoCtrl', 'IE_0']:
                if match != (self.ic.device == '1k'):
                    self.ieren_blocks[0].enable_input = True
                continue
            if entry[1:] == ['IoCtrl', 'REN_0']:
                if match:
                    self.ieren_blocks[0].disable_pull_up = True
                continue
            if entry[1:] == ['IoCtrl', 'IE_1']:
                if match != (self.ic.device == '1k'):
                    self.ieren_blocks[1].enable_input = True
                continue
            if entry[1:] == ['IoCtrl', 'REN_1']:
                if match:
                    self.ieren_blocks[1].disable_pull_up = True
                continue

            if entry[1].startswith('IOB_') and entry[2].startswith('PINTYPE_'):
                if match:
                    self.io_blocks[int(entry[1][4:])].pintype \
                        |= 1 << int(entry[2][8:])
                continue

            if entry[1:] == ['RamConfig', 'PowerUp']:
                if match != (self.ic.device == '1k'):
                    self.text.add('power_up')
                continue

            if entry[1] == 'routing':
                if match:
                    src = translate_netname(self.xy[0], self.xy[1],
                                            self.ic.max_x - 1,
                                            self.ic.max_y - 1, entry[2])
                    dst = translate_netname(self.xy[0], self.xy[1],
                                            self.ic.max_x - 1,
                                            self.ic.max_y - 1, entry[3])
                    if dst == 'fabout':
                        dst = lookup_fabout(*self.xy)
                    self.buffer_and_routing.add((src, '~>', dst))
                continue
            if entry[1] == 'buffer':
                if match:
                    src = translate_netname(self.xy[0], self.xy[1],
                                            self.ic.max_x - 1,
                                            self.ic.max_y - 1, entry[2])
                    dst = translate_netname(self.xy[0], self.xy[1],
                                            self.ic.max_x - 1,
                                            self.ic.max_y - 1, entry[3])
                    if dst == 'fabout':
                        dst = lookup_fabout(*self.xy)
                    self.buffer_and_routing.add((src, '->', dst))
                continue

            if entry[1] == 'ColBufCtrl':
                assert entry[2].startswith('glb_netwk_')
                #if match:
                #    fabric.colbuf.add(self.xy + (int(entry[2][10:]), ))
                continue

            if match:
                self.text.add(' '.join(entry[1:]))

        for prefix in ('local_', 'glb2local_'):
            for fst in [fst for fst in self.buffer_and_routing
                        if fst[-1].startswith(prefix)]:
                used = False
                for snd in [snd for snd in self.buffer_and_routing
                            if snd[0] == fst[-1]]:
                    self.buffer_and_routing.remove(snd)
                    self.buffer_and_routing.add(fst[:-1] + snd)
                    used = True
                if used:
                    self.buffer_and_routing.remove(fst)

        for k, line in enumerate(data):
            self.bitinfo.append('')
            extra_text = ''
            for i in range(len(line)):
                if 36 <= i <= 45 and is_logic_block:
                    self.bitinfo[-1] += '*' if line[i] == '1' else '-'
                elif line[i] == '1' and 'B%d[%d]' % (k, i) not in mapped_bits:
                    self.unknown_bits = True
                    extra_text += ' B%d[%d]' % (k, i)
                    self.bitinfo[-1] += '?'
                else:
                    self.bitinfo[-1] += '+' if line[i] == '1' else '-'
            self.bitinfo[-1] += extra_text

    def get_hlc(self):
        return sorted(set.union(self.text,
                                set(' '.join(t)
                                    for t in set.difference(
                                            self.buffer_and_routing,
                                            self.used_buffer_and_routing))))

    def printout(self, stmt, options):
        text = self.get_hlc()
        if text or self.unknown_bits or options.print_all:
            if self.unknown_bits or options.print_map:
                print()
                if self.unknown_bits:
                    print("; Warning: No DB entries for some bits:")
                for k, line in enumerate(self.bitinfo):
                    print("; %4s %s" % ('B%d' % k, line))
            print()
            print("%s %d %d {" % (stmt, self.xy[0], self.xy[1]))
            for line in text:
                print("    " + line)
            print("}")

class LogicCell:
    def __init__(self, tile, lcidx):
        self.lut = ''.join(icebox.get_lutff_lut_bits(tile.data, lcidx))
        self.expr = lut_to_logic_expression(
            self.lut, ('in_0', 'in_1', 'in_2', 'in_3'))

        self.options = []
        lutff_option_bits = ''.join(icebox.get_lutff_seq_bits(tile.data, lcidx))
        if lutff_option_bits[0] == '1': self.options.append('enable_carry')
        if lutff_option_bits[1] == '1': self.options.append('enable_dff')
        if lutff_option_bits[2] == '1': self.options.append('set_noreset')
        if lutff_option_bits[3] == '1': self.options.append('async_setreset')

        self.buffer_and_routing0 = set()
        self.buffer_and_routing1 = set()
        for br in tuple(tile.buffer_and_routing):
            if br[0] == 'lutff_%d/out' % lcidx:
                self.buffer_and_routing1.add((br[0][8:], ) + br[1:])
                tile.used_buffer_and_routing.add(br)
            elif br[-1].startswith('lutff_%d/' % lcidx):
                self.buffer_and_routing0.add(br[:-1] + (br[-1][8:], ))
                tile.used_buffer_and_routing.add(br)

    def get_hlc(self):
        if self.lut == '0000000000000000' and not self.options:
            t = []
        elif len(self.expr) > 64:
            t = ['lut ' + self.lut]
        else:
            t = ['out = ' + self.expr]
        return [' '.join(t) for t in sorted(self.buffer_and_routing0,
                                            key = lambda x: x[-1])] + \
               t + self.options + \
               [' '.join(t) for t in sorted(self.buffer_and_routing1,
                                            key = lambda x: x[-1])]

class LogicTile(Tile):
    def __init__(self, fabric, xy):
        super().__init__(fabric, xy, fabric.ic.logic_tiles[xy], True)
        self.cells = tuple(LogicCell(self, lcidx) for lcidx in range(8))

    def get_hlc(self):
        text = super().get_hlc()

        for i, cell in reversed(tuple(enumerate(self.cells))):
            t = cell.get_hlc()
            if t:
                text = ['lutff_%d {' % i] + \
                       ['    %s' % s for s in t] + \
                       ['}'] + \
                       text

        return text

    def printout(self, options):
        super().printout('logic_tile', options)

class IOBlock:
    def __init__(self):
        # stored in the I/O tile where this block is located
        self.pintype = 0

        # stored in the I/O tile where this is an IE/REN block
        self.enable_input = False
        self.disable_pull_up = False

        # stored as an extra bit
        self.padin_glb_netwk = False

class IOTile(Tile):
    def __init__(self, fabric, xy, io_blocks, ieren_blocks):
        self.io_blocks = io_blocks
        self.ieren_blocks = ieren_blocks
        super().__init__(fabric, xy, fabric.ic.io_tiles[xy], False)
        #self.cells = tuple(IOCell() for i in range(2))

        for i, block in enumerate(io_blocks):
            if block is None:
                continue
            block.buffer_and_routing0 = set()
            block.buffer_and_routing1 = set()
            for br in tuple(self.buffer_and_routing):
                if br[0].startswith('io_%d/D_IN_' % i):
                    block.buffer_and_routing1.add((br[0][5:], ) + br[1:])
                    self.used_buffer_and_routing.add(br)
                elif br[-1].startswith('io_%d/' % i):
                    block.buffer_and_routing0.add(br[:-1] + (br[-1][5:], ))
                    self.used_buffer_and_routing.add(br)

    def get_hlc(self):
        # if io_blocks[N] is None, this means there's no I/O pin there

        text = super().get_hlc()
        for n in (1, 0):
            block = self.io_blocks[n]
            if block is None:
                continue

            t = []
            input_pt = block.pintype & 3
            output_pt = block.pintype >> 2 & 15
            unknown_pt = block.pintype >> 6
            if input_pt != 0:
                t.append('input_pin_type = %s' % (
                    'registered_pin',
                    'simple_input_pin',
                    'latched_registered_pin',
                    'latched_pin')[input_pt])
            if output_pt != 0:
                t.append('output_pin_type = %s' % (
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
                    'REGISTERED_ENABLE_REGISTERED_INVERTED')[output_pt])
            if unknown_pt != 0:
                t.append('unknown_pin_type = %d' % unknown_pt)
            if block.enable_input:
                t.append('enable_input')
            if block.disable_pull_up:
                t.append('disable_pull_up')

            t += [' '.join(t) for t in sorted(block.buffer_and_routing0,
                                              key = lambda x: x[-1])]
            t += [' '.join(t) for t in sorted(block.buffer_and_routing1,
                                              key = lambda x: x[0])]
            if block.padin_glb_netwk:
                t += ['GLOBAL_BUFFER_OUTPUT -> glb_netwk_%d'
                        % GLB_NETWK_EXTERNAL_BLOCKS.index(self.xy + (n, ))]

            if t:
                text = ['io_%d {' % n] + \
                       ['    %s' % s for s in t] + \
                       ['}'] + \
                       text

        return text

    def printout(self, options):
        super().printout('io_tile', options)

class IOCell:
    pass

class RAMBTile(Tile):
    def __init__(self, fabric, xy):
        super().__init__(fabric, xy, fabric.ic.ramb_tiles[xy], False)
        if xy in fabric.ic.ram_data:
            self.data = fabric.ic.ram_data[xy]
        else:
            self.data = None

    def get_hlc(self):
        text = super().get_hlc()
        if self.data is not None:
            text.append('')
            text.append('data {')
            for line in self.data:
                text.append('    ' + line)
            text.append('}')
        return text

    def printout(self, options):
        super().printout('ramb_tile', options)

class RAMTTile(Tile):
    def __init__(self, fabric, xy):
        super().__init__(fabric, xy, fabric.ic.ramt_tiles[xy], False)

    def printout(self, options):
        super().printout('ramt_tile', options)


class Options:
    def __init__(self):
        self.print_map = False
        self.print_all = False

def main():
    program_short_name = os.path.basename(sys.argv[0])
    options = Options()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'mA', ['help', 'version'])
    except getopt.GetoptError as e:
        sys.stderr.write("%s: %s\n" % (program_short_name, e.msg))
        sys.stderr.write("Try `%s --help' for more information.\n"
                         % sys.argv[0])
        sys.exit(1)

    for opt, arg in opts:
        if opt == '--help':
            sys.stderr.write("""\
Create a high-level representation from an ASCII bitstream.
Usage: %s [OPTION]... FILE

  -m                    print tile config bitmaps
  -A                    don't skip uninteresting tiles

      --help            display this help and exit
      --version         output version information and exit

If you have a bug report, please file an issue on github:
  https://github.com/rlutz/icestorm/issues
""" % sys.argv[0])
            sys.exit(0)

        if opt == '--version':
            sys.stderr.write("""\
icebox_asc2hlc - create a high-level representation from an ASCII bitstream
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

        if opt == '-m':
            options.print_map = True
        elif opt == '-A':
            options.print_all = True

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

    ic = icebox.iceconfig()
    if args[0] == '-':
        ic.read_file('/dev/stdin')
    else:
        ic.read_file(args[0])

    fabric = Fabric(ic)
    fabric.printout(options)

if __name__ == '__main__':
    main()
