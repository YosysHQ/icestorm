#!/usr/bin/python
#
#  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from __future__ import division
from __future__ import print_function

import icebox
import getopt, sys, re

strip_comments = False
strip_interconn = False
lookup_pins = False
pcf_data = dict()
portnames = set()
unmatched_ports = set()
auto_clk = False
auto_en = False

def usage():
    print("""
Usage: icebox_vlog [options] <bitmap.txt>

    -s
        strip comments from output

    -S
        strip comments about interconn wires from output

    -a
        auto-detect global clock and enable signals
        (require ports "clk" and "en" in pcf file)

    -l
        convert io tile port names to chip pin numbers

    -p <pcf-file>
        use the set_io command from the specified pcf file

    -P <pcf-file>
        like -p, enable some hacks for pcf files created
        by the iCEcube2 placer.
""")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "sSlap:P:")
except:
    usage()

for o, a in opts:
    if o == "-s":
        strip_comments = True
    elif o == "-S":
        strip_interconn = True
    elif o == "-l":
        lookup_pins = True
    elif o == "-a":
        auto_clk = True
        auto_en = True
    elif o in ("-p", "-P"):
        with open(a, "r") as f:
            for line in f:
                line = re.sub(r"#.*", "", line.strip()).split()
                if len(line) and line[0] == "set_io":
                    p = line[1]
                    if o == "-P":
                        p = p.lower()
                        p = p.replace("_ibuf", "")
                        p = p.replace("_obuf", "")
                        p = p.replace("_gb_io", "")
                    portnames.add(p)
                    if not re.match(r"[a-zA-Z_][a-zA-Z0-9_]*$", p):
                        p = "\\%s " % p
                    unmatched_ports.add(p)
                    pinloc = tuple([int(s) for s in line[2:]])
                    pcf_data[pinloc] = p
    else:
        usage()

if not strip_comments:
    print("// Reading file '%s'.." % args[0])
ic = icebox.iceconfig()
ic.read_file(args[0])
print()

text_wires = list()
text_ports = list()

luts_queue = set()
text_func = list()

netidx = [0]
nets = dict()
seg2net = dict()

auto_clk_nets = set()
auto_en_nets = set()

def is_interconn(netname):
    if netname.startswith("sp4_"): return True
    if netname.startswith("sp12_"): return True
    if netname.startswith("span4_"): return True
    if netname.startswith("span12_"): return True
    if netname.startswith("logic_op_"): return True
    if netname.startswith("neigh_op_"): return True
    if netname.startswith("local_"): return True
    return False

for segs in sorted(ic.group_segments()):
    while True:
        netidx[0] += 1
        n = "n%d" % netidx[0]
        if n not in portnames: break

    net_segs = set()
    renamed_net_to_port = False

    for s in segs:
        match =  re.match("io_(\d+)/D_(IN|OUT)_(\d+)$", s[2])
        if match:
            if match.group(2) == "IN":
                p = "io_%d_%d_%s_din_%s" % (s[0], s[1], match.group(1), match.group(3))
                net_segs.add(p)
            else:
                p = "io_%d_%d_%s_dout_%s" % (s[0], s[1], match.group(1), match.group(3))
                net_segs.add(p)
            if lookup_pins or pcf_data:
                for entry in icebox.pinloc_db:
                    if s[0] == entry[1] and s[1] == entry[2] and int(match.group(1)) == entry[3]:
                        if (entry[0],) in pcf_data:
                            p = pcf_data[(entry[0],)]
                            unmatched_ports.discard(p)
                        elif (entry[1], entry[2], entry[3]) in pcf_data:
                            p = pcf_data[(entry[1], entry[2], entry[3])]
                            unmatched_ports.discard(p)
                        elif lookup_pins:
                            p = "pin_%d" % entry[0]
            if p == "clk":
                auto_clk = False
            if p == "en":
                auto_en = False
            if not renamed_net_to_port:
                n = p
                if match.group(2) == "IN":
                    text_ports.append("input %s" % p)
                else:
                    text_ports.append("output %s" % p)
                text_wires.append("wire %s;" % n)
                renamed_net_to_port = True
            elif match.group(2) == "IN":
                text_ports.append("input %s" % p)
                text_wires.append("assign %s = %s;" % (n, p))
            else:
                text_ports.append("output %s" % p)
                text_wires.append("assign %s = %s;" % (p, n))

        match =  re.match("lutff_(\d+)/", s[2])
        if match:
            luts_queue.add((s[0], s[1], int(match.group(1))))

    nets[n] = segs

    for s in segs:
        seg2net[s] = n

    if not renamed_net_to_port:
        text_wires.append("wire %s;" % n)

    for s in segs:
        if not strip_interconn or not is_interconn(s[2]):
            if s[2].startswith("glb_netwk_"):
                net_segs.add((0, 0, s[2]))
            else:
                net_segs.add(s)

    if not renamed_net_to_port:
        has_clk = False
        has_cen = False
        has_global = False
        has_driver = False
        for s in sorted(net_segs):
            if s[2].startswith("glb_netwk_"):
                has_global = True
            elif re.search(r"/out", s[2]):
                has_driver = True
            elif s[2] == "lutff_global/clk":
                has_clk = True
            elif s[2] == "lutff_global/cen":
                has_cen = True
        if has_global and not has_driver:
            if has_clk:
                auto_clk_nets.add(n)
            if has_cen and not has_clk:
                auto_en_nets.add(n)

    if not strip_comments:
        for s in sorted(net_segs):
                text_wires.append("// %s" % (s,))
        text_wires.append("")

for p in unmatched_ports:
    text_ports.append("input %s" % p)

if auto_clk and auto_clk_nets and "clk" in unmatched_ports:
    assert len(auto_clk_nets) == 1
    if not strip_comments:
        text_wires.append("// automatically detected clock network")
    text_wires.append("assign %s = clk;" % auto_clk_nets.pop())
    if not strip_comments:
        text_wires.append("")
    unmatched_ports.remove("clk")

if auto_en and auto_en_nets and "en" in unmatched_ports:
    assert len(auto_en_nets) == 1
    if not strip_comments:
        text_wires.append("// automatically detected enable network")
    text_wires.append("assign %s = en;" % auto_en_nets.pop())
    if not strip_comments:
        text_wires.append("")
    unmatched_ports.remove("en")

def seg_to_net(seg, default=None):
    if seg not in seg2net:
        if default is not None:
            return default
        while True:
            netidx[0] += 1
            n = "n%d" % netidx[0]
            if n not in portnames: break
        nets[n] = set([seg])
        seg2net[seg] = n
        text_wires.append("wire %s;" % n)
        if not strip_comments:
            if not strip_interconn or not is_interconn(seg[2]):
                text_wires.append("// %s" % (seg,))
            text_wires.append("")
    return seg2net[seg]

wire_to_reg = set()
lut_assigns = list()
const_assigns = list()
carry_assigns = list()
always_stmts = list()
max_net_len = 0

for lut in luts_queue:
    seq_bits = icebox.get_lutff_seq_bits(ic.logic_tiles[(lut[0], lut[1])], lut[2])
    if seq_bits[0] == "1":
        seg_to_net((lut[0], lut[1], "lutff_%d/cout" % lut[2]))

for lut in luts_queue:
    tile = ic.logic_tiles[(lut[0], lut[1])]
    lut_bits = icebox.get_lutff_lut_bits(tile, lut[2])
    seq_bits = icebox.get_lutff_seq_bits(tile, lut[2])
    net_in0 = seg_to_net((lut[0], lut[1], "lutff_%d/in_0" % lut[2]), "0")
    net_in1 = seg_to_net((lut[0], lut[1], "lutff_%d/in_1" % lut[2]), "0")
    net_in2 = seg_to_net((lut[0], lut[1], "lutff_%d/in_2" % lut[2]), "0")
    net_in3 = seg_to_net((lut[0], lut[1], "lutff_%d/in_3" % lut[2]), "0")
    net_out = seg_to_net((lut[0], lut[1], "lutff_%d/out" % lut[2]))
    if seq_bits[0] == "1":
        net_cout = seg_to_net((lut[0], lut[1], "lutff_%d/cout" % lut[2]))
        net_in1 = seg_to_net((lut[0], lut[1], "lutff_%d/in_1" % lut[2]), "0")
        net_in2 = seg_to_net((lut[0], lut[1], "lutff_%d/in_2" % lut[2]), "0")
        if lut[2] == 0:
            net_cin = seg_to_net((lut[0], lut[1], "carry_in_mux"))
            if icebox.get_carry_cascade_bit(tile) == "0":
                if not strip_comments:
                    text_wires.append("// Carry-In for (%d %d)" % (lut[0], lut[1]))
                text_wires.append("assign %s = %s;" % (net_cin, icebox.get_carry_bit(tile)))
                if not strip_comments:
                    text_wires.append("")
        else:
            net_cin = seg_to_net((lut[0], lut[1], "lutff_%d/cout" % (lut[2]-1)), "0")
        carry_assigns.append([net_cout, "/* CARRY %2d %2d %2d */ (%s & %s) | ((%s | %s) & %s)" %
                (lut[0], lut[1], lut[2], net_in1, net_in2, net_in1, net_in2, net_cin)])
    if seq_bits[1] == "1":
        while True:
            netidx[0] += 1
            n = "n%d" % netidx[0]
            if n not in portnames: break
        text_wires.append("wire %s;" % n)
        if not strip_comments:
            text_wires.append("// FF %s" % (lut,))
            text_wires.append("")
        net_cen = seg_to_net((lut[0], lut[1], "lutff_global/cen"), "1")
        net_clk = seg_to_net((lut[0], lut[1], "lutff_global/clk"), "0")
        net_sr  = seg_to_net((lut[0], lut[1], "lutff_global/s_r"), "0")
        if seq_bits[3] == "0":
            always_stmts.append("/* FF %2d %2d %2d */ always @(%sedge %s) if (%s) %s <= %s ? %s : %s;" %
                    (lut[0], lut[1], lut[2], "neg" if icebox.get_negclk_bit(tile) == "1" else "pos",
                    net_clk, net_cen, net_out, net_sr, seq_bits[2], n))
        else:
            always_stmts.append("/* FF %2d %2d %2d */ always @(%sedge %s, posedge %s) if (%s) %s <= %s; else if (%s) %s <= %s;" %
                    (lut[0], lut[1], lut[2], "neg" if icebox.get_negclk_bit(tile) == "1" else "pos",
                    net_clk, net_sr, net_sr, net_out, seq_bits[2], net_cen, net_out, n))
        wire_to_reg.add(net_out)
        net_out = n
    if not "1" in lut_bits:
        const_assigns.append([net_out, "1'b0"])
    elif not "0" in lut_bits:
        const_assigns.append([net_out, "1'b1"])
    else:
        def make_lut_expr(bits, sigs):
            if not sigs:
                return "%s" % bits[0]
            l_expr = make_lut_expr(bits[0:len(bits)//2], sigs[1:])
            h_expr = make_lut_expr(bits[len(bits)//2:len(bits)], sigs[1:])
            if h_expr == l_expr: return h_expr
            if sigs[0] == "0": return l_expr
            if sigs[0] == "1": return h_expr
            if h_expr == "1" and l_expr == "0": return sigs[0]
            if h_expr == "0" and l_expr == "1": return "!" + sigs[0]
            return "%s ? %s : %s" % (sigs[0], h_expr, l_expr)
        lut_expr = make_lut_expr(lut_bits, [net_in3, net_in2, net_in1, net_in0])
        lut_assigns.append([net_out, "/* LUT   %2d %2d %2d */ %s" % (lut[0], lut[1], lut[2], lut_expr)])
    max_net_len = max(max_net_len, len(net_out))

for a in const_assigns + lut_assigns + carry_assigns:
    text_func.append("assign %-*s = %s;" % (max_net_len, a[0], a[1]))

print("module chip (%s);\n" % ", ".join(text_ports))

new_text_wires = list()
for line in text_wires:
    match = re.match(r"wire ([^ ;]+)(.*)", line)
    if match and match.group(1) in wire_to_reg:
        line = "reg " + match.group(1) + match.group(2)
    if strip_comments:
        if new_text_wires and new_text_wires[-1].split()[0] == line.split()[0] and new_text_wires[-1][-1] == ";":
            new_text_wires[-1] = new_text_wires[-1][0:-1] + "," + line[len(line.split()[0]):]
        else:
            new_text_wires.append(line)
    else:
        print(line)
for line in new_text_wires:
    print(line)
if strip_comments:
    print()

for line in text_func:
    print(line)
for line in always_stmts:
    print(line)
print()

for p in unmatched_ports:
    print("// Warning: unmatched port '%s'" %p)
if unmatched_ports:
    print()

print("endmodule")
print()

