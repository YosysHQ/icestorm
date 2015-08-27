#!/usr/bin/env python3
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

import icebox
import getopt, sys, re

strip_comments = False
strip_interconn = False
lookup_pins = False
check_ieren = False
check_driver = False
lookup_symbols = False
do_collect = False
pcf_data = dict()
portnames = set()
unmatched_ports = set()
modname = "chip"

def usage():
    print("""
Usage: icebox_vlog [options] [bitmap.txt]

    -s
        strip comments from output

    -S
        strip comments about interconn wires from output

    -l
        convert io tile port names to chip pin numbers

    -L
        lookup symbol names (using .sym statements in input)

    -n <module-name>
        name for the exported module (default: "chip")

    -p <pcf-file>
        use the set_io command from the specified pcf file

    -P <pcf-file>
        like -p, enable some hacks for pcf files created
        by the iCEcube2 placer.

    -c
        collect multi-bit ports

    -R
        enable IeRen database checks

    -D
        enable exactly-one-driver checks
""")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "sSlLap:P:n:cRD")
except:
    usage()

for o, a in opts:
    if o == "-s":
        strip_comments = True
    elif o == "-S":
        strip_interconn = True
    elif o == "-l":
        lookup_pins = True
    elif o == "-L":
        lookup_symbols = True
    elif o == "-n":
        modname = a
    elif o == "-a":
        pass # ignored for backward compatibility
    elif o in ("-p", "-P"):
        with open(a, "r") as f:
            for line in f:
                if o == "-P" and not re.search(" # ICE_(GB_)?IO", line):
                    continue
                line = re.sub(r"#.*", "", line.strip()).split()
                if len(line) and line[0] == "set_io":
                    p = line[1]
                    if o == "-P":
                        p = p.lower()
                        p = re.sub(r"_ibuf$", "", p)
                        p = re.sub(r"_obuft$", "", p)
                        p = re.sub(r"_obuf$", "", p)
                        p = re.sub(r"_gb_io$", "", p)
                        p = re.sub(r"_pad(_[0-9]+|)$", r"\1", p)
                    portnames.add(p)
                    if not re.match(r"[a-zA-Z_][a-zA-Z0-9_]*$", p):
                        p = "\\%s " % p
                    unmatched_ports.add(p)
                    if len(line) > 3:
                        pinloc = tuple([int(s) for s in line[2:]])
                    else:
                        pinloc = (line[2],)
                    pcf_data[pinloc] = p
    elif o == "-c":
        do_collect = True
    elif o == "-R":
        check_ieren = True
    elif o == "-D":
        check_driver = True
    else:
        usage()

if len(args) == 0:
    args.append("/dev/stdin")

if len(args) != 1:
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
failed_drivers_check = list()

netidx = [0]
nets = dict()
seg2net = dict()

iocells = set()
iocells_in = set()
iocells_out = set()
iocells_special = set()
iocells_type = dict()
iocells_negclk = set()
iocells_inbufs = set()
iocells_skip = set()
iocells_pll = set()

def is_interconn(netname):
    if netname.startswith("sp4_"): return True
    if netname.startswith("sp12_"): return True
    if netname.startswith("span4_"): return True
    if netname.startswith("span12_"): return True
    if netname.startswith("logic_op_"): return True
    if netname.startswith("neigh_op_"): return True
    if netname.startswith("local_"): return True
    return False

pll_config_bitidx = dict()
pll_gbuf = dict()

for entry in icebox.iotile_l_db:
    if entry[1] == "PLL":
        match = re.match(r"B(\d+)\[(\d+)\]", entry[0][0]);
        assert match
        pll_config_bitidx[entry[2]] = (int(match.group(1)), int(match.group(2)))

def get_pll_bit(pllinfo, name):
    bit = pllinfo[name]
    assert bit[2] in pll_config_bitidx
    return ic.tile(bit[0], bit[1])[pll_config_bitidx[bit[2]][0]][pll_config_bitidx[bit[2]][1]]

def get_pll_bits(pllinfo, name, n):
    return "".join([get_pll_bit(pllinfo, "%s_%d" % (name, i)) for i in range(n-1, -1, -1)])

for pllid in ic.pll_list():
    pllinfo = icebox.pllinfo_db[pllid]
    plltype = get_pll_bits(pllinfo, "PLLTYPE", 3)
    if plltype != "000":
        if plltype in ["010", "100", "110"]:
            iocells_special.add(pllinfo["PLLOUT_A"])
        else:
            iocells_skip.add(pllinfo["PLLOUT_A"])
        iocells_pll.add(pllinfo["PLLOUT_A"])
        if plltype not in ["010", "011"]:
            iocells_skip.add(pllinfo["PLLOUT_B"])
            iocells_pll.add(pllinfo["PLLOUT_B"])

extra_connections = list()
extra_segments = list()

for bit in ic.extra_bits:
    entry = ic.lookup_extra_bit(bit)
    if entry[0] == "padin_glb_netwk":
        glb = int(entry[1])
        pin_entry = ic.padin_pio_db()[glb]
        if pin_entry in iocells_pll:
            pll_gbuf[pin_entry] = (pin_entry[0], pin_entry[1], "padin_%d" % pin_entry[2])
            extra_segments.append(pll_gbuf[pin_entry])
        else:
            iocells.add((pin_entry[0], pin_entry[1], pin_entry[2]))
            iocells_in.add((pin_entry[0], pin_entry[1], pin_entry[2]))
            s1 = (pin_entry[0], pin_entry[1], "io_%d/PAD" % pin_entry[2])
            s2 = (pin_entry[0], pin_entry[1], "padin_%d" % pin_entry[2])
            extra_connections.append((s1, s2))

for idx, tile in list(ic.io_tiles.items()):
    tc = icebox.tileconfig(tile)
    iocells_type[(idx[0], idx[1], 0)] = ["0" for i in range(6)]
    iocells_type[(idx[0], idx[1], 1)] = ["0" for i in range(6)]
    for entry in ic.tile_db(idx[0], idx[1]):
        if check_ieren and entry[1] == "IoCtrl" and entry[2].startswith("IE_") and not tc.match(entry[0]):
            iren_idx = (idx[0], idx[1], 0 if entry[2] == "IE_0" else 1)
            for iren_entry in ic.ieren_db():
                if iren_idx[0] == iren_entry[3] and iren_idx[1] == iren_entry[4] and iren_idx[2] == iren_entry[5]:
                    iocells_inbufs.add((iren_entry[0], iren_entry[1], iren_entry[2]))
        if entry[1] == "NegClk" and tc.match(entry[0]):
            iocells_negclk.add((idx[0], idx[1], 0))
            iocells_negclk.add((idx[0], idx[1], 1))
        if entry[1].startswith("IOB_") and entry[2].startswith("PINTYPE_") and tc.match(entry[0]):
            match1 = re.match("IOB_(\d+)", entry[1])
            match2 = re.match("PINTYPE_(\d+)", entry[2])
            assert match1 and match2
            iocells_type[(idx[0], idx[1], int(match1.group(1)))][int(match2.group(1))] = "1"
    iocells_type[(idx[0], idx[1], 0)] = "".join(iocells_type[(idx[0], idx[1], 0)])
    iocells_type[(idx[0], idx[1], 1)] = "".join(iocells_type[(idx[0], idx[1], 1)])

for segs in sorted(ic.group_segments()):
    for seg in segs:
        if ic.tile_type(seg[0], seg[1]) == "IO":
            match = re.match("io_(\d+)/D_(IN|OUT)_(\d+)", seg[2])
            if match:
                cell = (seg[0], seg[1], int(match.group(1)))
                if cell in iocells_skip:
                    continue
                iocells.add(cell)
                if match.group(2) == "IN":
                    if check_ieren:
                        assert cell in iocells_inbufs
                    if iocells_type[cell] != "100000" or match.group(3) != "0":
                        iocells_special.add(cell)
                    iocells_in.add(cell)
                if match.group(2) == "OUT" and iocells_type[cell][2:6] != "0000":
                    if iocells_type[cell] != "100110" or match.group(3) != "0":
                        iocells_special.add(cell)
                    iocells_out.add(cell)
                extra_segments.append((seg[0], seg[1], "io_%d/PAD" % int(match.group(1))))

for cell in iocells:
    if iocells_type[cell] == "100110" and not cell in iocells_special:
        s1 = (cell[0], cell[1], "io_%d/PAD" % cell[2])
        s2 = (cell[0], cell[1], "io_%d/D_OUT_0" % cell[2])
        extra_connections.append((s1, s2))
        del iocells_type[cell]
    elif iocells_type[cell] == "100000" and not cell in iocells_special:
        s1 = (cell[0], cell[1], "io_%d/PAD" % cell[2])
        s2 = (cell[0], cell[1], "io_%d/D_IN_0" % cell[2])
        extra_connections.append((s1, s2))
        del iocells_type[cell]

def next_netname():
    while True:
        netidx[0] += 1
        n = "n%d" % netidx[0]
        if n not in portnames:
            return n

for segs in sorted(ic.group_segments(extra_connections=extra_connections, extra_segments=extra_segments)):
    n = next_netname()
    net_segs = set()
    renamed_net_to_port = False

    for s in segs:
        match =  re.match("io_(\d+)/PAD", s[2])
        if match:
            idx = (s[0], s[1], int(match.group(1)))
            p = "io_%d_%d_%d" % idx
            if lookup_pins or pcf_data:
                for entry in ic.pinloc_db():
                    if idx[0] == entry[1] and idx[1] == entry[2] and idx[2] == entry[3]:
                        if (entry[0],) in pcf_data:
                            p = pcf_data[(entry[0],)]
                            unmatched_ports.discard(p)
                        elif (entry[1], entry[2], entry[3]) in pcf_data:
                            p = pcf_data[(entry[1], entry[2], entry[3])]
                            unmatched_ports.discard(p)
                        elif lookup_pins:
                            p = "pin_%s" % entry[0]
            if not renamed_net_to_port:
                n = p
                if idx in iocells_in and idx not in iocells_out:
                    text_ports.append("input %s" % p)
                elif idx not in iocells_in and idx in iocells_out:
                    text_ports.append("output %s" % p)
                else:
                    text_ports.append("inout %s" % p)
                text_wires.append("wire %s;" % n)
                renamed_net_to_port = True
            elif idx in iocells_in and idx not in iocells_out:
                text_ports.append("input %s" % p)
                text_wires.append("assign %s = %s;" % (n, p))
            elif idx not in iocells_in and idx in iocells_out:
                text_ports.append("output %s" % p)
                text_wires.append("assign %s = %s;" % (p, n))
            else:
                text_ports.append("inout %s" % p)
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

    count_drivers = 0
    for s in segs:
        if re.match(r"ram/RDATA_", s[2]): count_drivers += 1
        if re.match(r"io_./D_IN_", s[2]): count_drivers += 1
        if re.match(r"lutff_./out", s[2]): count_drivers += 1

    if count_drivers != 1 and check_driver:
        failed_drivers_check.append(n)

    if not strip_comments:
        for s in sorted(net_segs):
                text_wires.append("// %s" % (s,))
        if count_drivers != 1 and check_driver:
            text_wires.append("// Number of drivers: %d" % count_drivers)
        text_wires.append("")

def seg_to_net(seg, default=None):
    if seg not in seg2net:
        if default is not None:
            return default
        n = next_netname()
        nets[n] = set([seg])
        seg2net[seg] = n
        text_wires.append("wire %s;" % n)
        if not strip_comments:
            if not strip_interconn or not is_interconn(seg[2]):
                text_wires.append("// %s" % (seg,))
            text_wires.append("")
    return seg2net[seg]

if lookup_symbols:
    text_func.append("// Debug Symbols")
    with open("/usr/local/share/icebox/chipdb-%s.txt" % ic.device, "r") as f:
        current_net = -1
        exported_names = dict()
        for line in f:
            line = line.split()
            if len(line) == 0:
                pass
            elif line[0] == ".net":
                current_net = int(line[1])
                if current_net not in ic.symbols:
                    current_net = -1
            elif line[0].startswith("."):
                current_net = -1
            elif current_net >= 0:
                seg = (int(line[0]), int(line[1]), line[2])
                if seg in seg2net:
                    for name in ic.symbols[current_net]:
                        while name in exported_names:
                            if exported_names[name] == seg2net[seg]:
                                break
                            name += "_"
                        if name not in exported_names:
                            text_func.append("wire \\_%s = %s;" % (name, seg2net[seg]))
                            exported_names[name] = seg2net[seg]
                    current_net = -1
    text_func.append("")

wb_boot = seg_to_net(icebox.warmbootinfo_db[ic.device]["BOOT"], "")
wb_s0 = seg_to_net(icebox.warmbootinfo_db[ic.device]["S0"], "")
wb_s1 = seg_to_net(icebox.warmbootinfo_db[ic.device]["S1"], "")

if wb_boot != "" or wb_s0 != "" or wb_s1 != "":
    text_func.append("SB_WARMBOOT (")
    text_func.append("  .BOOT(%s)," % wb_boot)
    text_func.append("  .S0(%s)," % wb_s0)
    text_func.append("  .S1(%s)," % wb_s1)
    text_func.append(");")
    text_func.append("")

def get_pll_feedback_path(pllinfo):
    v = get_pll_bits(pllinfo, "FEEDBACK_PATH", 3)
    if v == "000": return "DELAY"
    if v == "001": return "SIMPLE"
    if v == "010": return "PHASE_AND_DELAY"
    if v == "110": return "EXTERNAL"
    assert False

def get_pll_adjmode(pllinfo, name):
    v = get_pll_bit(pllinfo, name)
    if v == "0": return "FIXED"
    if v == "1": return "DYNAMIC"
    assert False

def get_pll_outsel(pllinfo, name):
    v = get_pll_bits(pllinfo, name, 2)
    if v == "00": return "GENCLK"
    if v == "01": return "GENCLK_HALF"
    if v == "10": return "SHIFTREG_90deg"
    if v == "11": return "SHIFTREG_0deg"
    assert False

for pllid in ic.pll_list():
    pllinfo = icebox.pllinfo_db[pllid]
    plltype = get_pll_bits(pllinfo, "PLLTYPE", 3)

    if plltype == "000":
        continue

    if not strip_comments:
        text_func.append("// plltype = %s" % plltype)
        for ti in sorted(ic.io_tiles):
            for bit in sorted(pll_config_bitidx):
                if ic.io_tiles[ti][pll_config_bitidx[bit][0]][pll_config_bitidx[bit][1]] == "1":
                    resolved_bitname = ""
                    for bitname in pllinfo:
                        if pllinfo[bitname] == (ti[0], ti[1], bit):
                            resolved_bitname = " " + bitname
                    text_func.append("// (%2d, %2d, \"%s\")%s" % (ti[0], ti[1], bit, resolved_bitname))

    if plltype in ["010", "100", "110"]:
        if plltype == "010": text_func.append("SB_PLL40_PAD #(")
        if plltype == "100": text_func.append("SB_PLL40_2_PAD #(")
        if plltype == "110": text_func.append("SB_PLL40_2F_PAD #(")
        text_func.append("  .FEEDBACK_PATH(\"%s\")," % get_pll_feedback_path(pllinfo))
        text_func.append("  .DELAY_ADJUSTMENT_MODE_FEEDBACK(\"%s\")," % get_pll_adjmode(pllinfo, "DELAY_ADJMODE_FB"))
        text_func.append("  .DELAY_ADJUSTMENT_MODE_RELATIVE(\"%s\")," % get_pll_adjmode(pllinfo, "DELAY_ADJMODE_REL"))
        if plltype == "010":
            text_func.append("  .PLLOUT_SELECT(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_A"))
        else:
            if plltype != "100":
                text_func.append("  .PLLOUT_SELECT_PORTA(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_A"))
            text_func.append("  .PLLOUT_SELECT_PORTB(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_B"))
        text_func.append("  .SHIFTREG_DIV_MODE(1'b%s)," % get_pll_bit(pllinfo, "SHIFTREG_DIV_MODE"))
        text_func.append("  .FDA_FEEDBACK(4'b%s)," % get_pll_bits(pllinfo, "FDA_FEEDBACK", 4))
        text_func.append("  .FDA_RELATIVE(4'b%s)," % get_pll_bits(pllinfo, "FDA_RELATIVE", 4))
        text_func.append("  .DIVR(4'b%s)," % get_pll_bits(pllinfo, "DIVR", 4))
        text_func.append("  .DIVF(7'b%s)," % get_pll_bits(pllinfo, "DIVF", 7))
        text_func.append("  .DIVQ(3'b%s)," % get_pll_bits(pllinfo, "DIVQ", 3))
        text_func.append("  .FILTER_RANGE(3'b%s)," % get_pll_bits(pllinfo, "FILTER_RANGE", 3))
        if plltype == "010":
            text_func.append("  .ENABLE_ICEGATE(1'b0),")
        else:
            text_func.append("  .ENABLE_ICEGATE_PORTA(1'b0),")
            text_func.append("  .ENABLE_ICEGATE_PORTB(1'b0),")
        text_func.append("  .TEST_MODE(1'b%s)" % get_pll_bit(pllinfo, "TEST_MODE"))
        text_func.append(") PLL_%d_%d (" % pllinfo["LOC"])
        if plltype == "010":
            pad_segment = (pllinfo["PLLOUT_A"][0], pllinfo["PLLOUT_A"][1], "io_%d/PAD" % pllinfo["PLLOUT_A"][2])
            text_func.append("  .PACKAGEPIN(%s)," % seg_to_net(pad_segment))
            del seg2net[pad_segment]
            text_func.append("  .PLLOUTCORE(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_A"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBAL(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_A"]]))
        else:
            pad_segment = (pllinfo["PLLOUT_A"][0], pllinfo["PLLOUT_A"][1], "io_%d/PAD" % pllinfo["PLLOUT_A"][2])
            text_func.append("  .PACKAGEPIN(%s)," % seg_to_net(pad_segment))
            del seg2net[pad_segment]
            text_func.append("  .PLLOUTCOREA(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_A"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBALA(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_A"]]))
            pad_segment = (pllinfo["PLLOUT_B"][0], pllinfo["PLLOUT_B"][1], "io_%d/D_IN_0" % pllinfo["PLLOUT_B"][2])
            text_func.append("  .PLLOUTCOREB(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_B"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBALB(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_B"]]))
        text_func.append("  .EXTFEEDBACK(%s)," % seg_to_net(pllinfo["EXTFEEDBACK"], "1'b0"))
        text_func.append("  .DYNAMICDELAY({%s})," % ", ".join([seg_to_net(pllinfo["DYNAMICDELAY_%d" % i], "1'b0") for i in range(7, -1, -1)]))
        text_func.append("  .LOCK(%s)," % seg_to_net(pllinfo["LOCK"]))
        text_func.append("  .BYPASS(%s)," % seg_to_net(pllinfo["BYPASS"], "1'b0"))
        text_func.append("  .RESETB(%s)," % seg_to_net(pllinfo["RESETB"], "1'b0"))
        text_func.append("  .LATCHINPUTVALUE(%s)," % seg_to_net(pllinfo["LATCHINPUTVALUE"], "1'b0"))
        text_func.append("  .SDO(%s)," % seg_to_net(pllinfo["SDO"]))
        text_func.append("  .SDI(%s)," % seg_to_net(pllinfo["SDI"], "1'b0"))
        text_func.append("  .SCLK(%s)" % seg_to_net(pllinfo["SCLK"], "1'b0"))
        text_func.append(");")

    if plltype in ["011", "111"]:
        if plltype == "011": text_func.append("SB_PLL40_CORE #(")
        if plltype == "111": text_func.append("SB_PLL40_2F_CORE #(")
        text_func.append("  .FEEDBACK_PATH(\"%s\")," % get_pll_feedback_path(pllinfo))
        text_func.append("  .DELAY_ADJUSTMENT_MODE_FEEDBACK(\"%s\")," % get_pll_adjmode(pllinfo, "DELAY_ADJMODE_FB"))
        text_func.append("  .DELAY_ADJUSTMENT_MODE_RELATIVE(\"%s\")," % get_pll_adjmode(pllinfo, "DELAY_ADJMODE_REL"))
        if plltype == "011":
            text_func.append("  .PLLOUT_SELECT(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_A"))
        else:
            text_func.append("  .PLLOUT_SELECT_PORTA(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_A"))
            text_func.append("  .PLLOUT_SELECT_PORTB(\"%s\")," % get_pll_outsel(pllinfo, "PLLOUT_SELECT_B"))
        text_func.append("  .SHIFTREG_DIV_MODE(1'b%s)," % get_pll_bit(pllinfo, "SHIFTREG_DIV_MODE"))
        text_func.append("  .FDA_FEEDBACK(4'b%s)," % get_pll_bits(pllinfo, "FDA_FEEDBACK", 4))
        text_func.append("  .FDA_RELATIVE(4'b%s)," % get_pll_bits(pllinfo, "FDA_RELATIVE", 4))
        text_func.append("  .DIVR(4'b%s)," % get_pll_bits(pllinfo, "DIVR", 4))
        text_func.append("  .DIVF(7'b%s)," % get_pll_bits(pllinfo, "DIVF", 7))
        text_func.append("  .DIVQ(3'b%s)," % get_pll_bits(pllinfo, "DIVQ", 3))
        text_func.append("  .FILTER_RANGE(3'b%s)," % get_pll_bits(pllinfo, "FILTER_RANGE", 3))
        if plltype == "011":
            text_func.append("  .ENABLE_ICEGATE(1'b0),")
        else:
            text_func.append("  .ENABLE_ICEGATE_PORTA(1'b0),")
            text_func.append("  .ENABLE_ICEGATE_PORTB(1'b0),")
        text_func.append("  .TEST_MODE(1'b%s)" % get_pll_bit(pllinfo, "TEST_MODE"))
        text_func.append(") PLL_%d_%d (" % pllinfo["LOC"])
        text_func.append("  .REFERENCECLK(%s)," % seg_to_net(pllinfo["REFERENCECLK"], "1'b0"))
        if plltype == "011":
            pad_segment = (pllinfo["PLLOUT_A"][0], pllinfo["PLLOUT_A"][1], "io_%d/D_IN_0" % pllinfo["PLLOUT_A"][2])
            text_func.append("  .PLLOUTCORE(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_A"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBAL(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_A"]]))
        else:
            pad_segment = (pllinfo["PLLOUT_A"][0], pllinfo["PLLOUT_A"][1], "io_%d/D_IN_0" % pllinfo["PLLOUT_A"][2])
            text_func.append("  .PLLOUTCOREA(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_A"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBALA(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_A"]]))
            pad_segment = (pllinfo["PLLOUT_B"][0], pllinfo["PLLOUT_B"][1], "io_%d/D_IN_0" % pllinfo["PLLOUT_B"][2])
            text_func.append("  .PLLOUTCOREB(%s)," % seg_to_net(pad_segment))
            if pllinfo["PLLOUT_B"] in pll_gbuf:
                text_func.append("  .PLLOUTGLOBALB(%s)," % seg_to_net(pll_gbuf[pllinfo["PLLOUT_B"]]))
        text_func.append("  .EXTFEEDBACK(%s)," % seg_to_net(pllinfo["EXTFEEDBACK"], "1'b0"))
        text_func.append("  .DYNAMICDELAY({%s})," % ", ".join([seg_to_net(pllinfo["DYNAMICDELAY_%d" % i], "1'b0") for i in range(7, -1, -1)]))
        text_func.append("  .LOCK(%s)," % seg_to_net(pllinfo["LOCK"]))
        text_func.append("  .BYPASS(%s)," % seg_to_net(pllinfo["BYPASS"], "1'b0"))
        text_func.append("  .RESETB(%s)," % seg_to_net(pllinfo["RESETB"], "1'b0"))
        text_func.append("  .LATCHINPUTVALUE(%s)," % seg_to_net(pllinfo["LATCHINPUTVALUE"], "1'b0"))
        text_func.append("  .SDO(%s)," % seg_to_net(pllinfo["SDO"]))
        text_func.append("  .SDI(%s)," % seg_to_net(pllinfo["SDI"], "1'b0"))
        text_func.append("  .SCLK(%s)" % seg_to_net(pllinfo["SCLK"], "1'b0"))
        text_func.append(");")

    text_func.append("")

for cell in iocells:
    if cell in iocells_type:
        net_pad   = seg_to_net((cell[0], cell[1], "io_%d/PAD" % cell[2]))
        net_din0  = seg_to_net((cell[0], cell[1], "io_%d/D_IN_0" % cell[2]), "")
        net_din1  = seg_to_net((cell[0], cell[1], "io_%d/D_IN_1" % cell[2]), "")
        net_dout0 = seg_to_net((cell[0], cell[1], "io_%d/D_OUT_0" % cell[2]), "0")
        net_dout1 = seg_to_net((cell[0], cell[1], "io_%d/D_OUT_1" % cell[2]), "0")
        net_oen   = seg_to_net((cell[0], cell[1], "io_%d/OUT_ENB" % cell[2]), "1")
        net_cen   = seg_to_net((cell[0], cell[1], "io_global/cen"), "1")
        net_iclk  = seg_to_net((cell[0], cell[1], "io_global/inclk"), "0")
        net_oclk  = seg_to_net((cell[0], cell[1], "io_global/outclk"), "0")
        net_latch = seg_to_net((cell[0], cell[1], "io_global/latch"), "0")
        iotype = iocells_type[cell]

        if cell in iocells_negclk:
            posedge = "negedge"
            negedge = "posedge"
        else:
            posedge = "posedge"
            negedge = "negedge"

        text_func.append("// IO Cell %s" % (cell,))
        if not strip_comments:
            text_func.append("// PAD     = %s" % net_pad)
            text_func.append("// D_IN_0  = %s" % net_din0)
            text_func.append("// D_IN_1  = %s" % net_din1)
            text_func.append("// D_OUT_0 = %s" % net_dout0)
            text_func.append("// D_OUT_1 = %s" % net_dout1)
            text_func.append("// OUT_ENB = %s" % net_oen)
            text_func.append("// CLK_EN  = %s" % net_cen)
            text_func.append("// IN_CLK  = %s" % net_iclk)
            text_func.append("// OUT_CLK = %s" % net_oclk)
            text_func.append("// LATCH   = %s" % net_latch)
            text_func.append("// TYPE    = %s (LSB:MSB)" % iotype)
        
        if net_din0 != "" or net_din1 != "":
            if net_cen == "1":
                icen_cond = ""
            else:
                icen_cond = "if (%s) " % net_cen

            if net_din0 != "":
                if iotype[1] == "0" and iotype[0] == "0":
                    reg_din0 = next_netname()
                    text_func.append("reg %s;" % reg_din0)
                    text_func.append("always @(%s %s) %s%s <= %s;" % (posedge, net_iclk, icen_cond, reg_din0, net_pad))
                    text_func.append("assign %s = %s;" % (net_din0, reg_din0))

                if iotype[1] == "0" and iotype[0] == "1":
                    text_func.append("assign %s = %s;" % (net_din0, net_pad))

                if iotype[1] == "1" and iotype[0] == "0":
                    reg_din0 = next_netname()
                    reg_din0_latched = next_netname()
                    text_func.append("reg %s, %s;" % (reg_din0, reg_din0_latched))
                    text_func.append("always @(%s %s) %s%s <= %s;" % (posedge, net_iclk, icen_cond, reg_din0, net_pad))
                    text_func.append("always @* if (!%s) %s = %s;" % (net_latch, reg_din0_latched, reg_din0))
                    text_func.append("assign %s = %s;" % (net_din0, reg_din0_latched))

                if iotype[1] == "1" and iotype[0] == "1":
                    reg_din0 = next_netname()
                    text_func.append("reg %s;" % reg_din0)
                    text_func.append("always @* if (!%s) %s = %s;" % (net_latch, reg_din0, net_pad))
                    text_func.append("assign %s = %s;" % (net_din0, reg_din0))

            if net_din1 != "":
                reg_din1 = next_netname()
                text_func.append("reg %s;" % reg_din1)
                text_func.append("always @(%s %s) %s%s <= %s;" % (negedge, net_iclk, icen_cond, reg_din1, net_pad))
                text_func.append("assign %s = %s;" % (net_din1, reg_din1))

        if iotype[5] != "0" or iotype[4] != "0":
            if net_cen == "1":
                ocen_cond = ""
            else:
                ocen_cond = "if (%s) " % net_cen

            # effective OEN: iotype[4], iotype[5]

            if iotype[5] == "0" and iotype[4] == "1":
                eff_oen = "1"

            if iotype[5] == "1" and iotype[4] == "0":
                eff_oen = net_oen

            if iotype[5] == "1" and iotype[4] == "1":
                eff_oen = next_netname()
                text_func.append("reg %s;" % eff_oen)
                text_func.append("always @(%s %s) %s%s <= %s;" % (posedge, net_oclk, ocen_cond, eff_oen, net_oen))

            # effective DOUT: iotype[2], iotype[3]

            if iotype[2] == "0" and iotype[3] == "0":
                ddr_posedge = next_netname()
                ddr_negedge = next_netname()
                text_func.append("reg %s, %s;" % (ddr_posedge, ddr_negedge))
                text_func.append("always @(%s %s) %s%s <= %s;" % (posedge, net_oclk, ocen_cond, ddr_posedge, net_dout0))
                text_func.append("always @(%s %s) %s%s <= %s;" % (negedge, net_oclk, ocen_cond, ddr_negedge, net_dout1))
                eff_dout = next_netname()
                text_func.append("wire %s;" % (eff_dout))
                if cell in iocells_negclk:
                    text_func.append("assign %s = %s ? %s : %s;" % (eff_dout, net_oclk, ddr_negedge, ddr_posedge))
                else:
                    text_func.append("assign %s = %s ? %s : %s;" % (eff_dout, net_oclk, ddr_posedge, ddr_negedge))

            if iotype[2] == "0" and iotype[3] == "1":
                eff_dout = net_dout0

            if iotype[2] == "1" and iotype[3] == "0":
                eff_dout = next_netname()
                text_func.append("reg %s;" % eff_dout)
                text_func.append("always @(%s %s) %s%s <= %s;" % (posedge, net_oclk, ocen_cond, eff_dout, net_dout0))

            if iotype[2] == "1" and iotype[3] == "1":
                eff_dout = next_netname()
                text_func.append("reg %s;" % eff_dout)
                text_func.append("always @(%s %s) %s%s <= !%s;" % (posedge, net_oclk, ocen_cond, eff_dout, net_dout0))

            if eff_oen == "1":
                text_func.append("assign %s = %s;" % (net_pad, eff_dout))
            else:
                text_func.append("assign %s = %s ? %s : 1'bz;" % (net_pad, eff_oen, eff_dout))

        text_func.append("")

for p in unmatched_ports:
    text_ports.append("input %s" % p)

ram_config_bitidx = dict()

for tile in ic.ramb_tiles:
    for entry in ic.tile_db(tile[0], tile[1]):
        if entry[1] == "RamConfig":
            assert entry[2] not in ram_config_bitidx
            ram_config_bitidx[entry[2]] = ('B', entry[0])
    for entry in ic.tile_db(tile[0], tile[1]+1):
        if entry[1] == "RamConfig":
            assert entry[2] not in ram_config_bitidx
            ram_config_bitidx[entry[2]] = ('T', entry[0])
    break

for tile in ic.ramb_tiles:
    ramb_config = icebox.tileconfig(ic.tile(tile[0], tile[1]))
    ramt_config = icebox.tileconfig(ic.tile(tile[0], tile[1]+1))
    def get_ram_config(name):
        assert name in ram_config_bitidx
        if ram_config_bitidx[name][0] == 'B':
            return ramb_config.match(ram_config_bitidx[name][1])
        elif ram_config_bitidx[name][0] == 'T':
            return ramt_config.match(ram_config_bitidx[name][1])
        else:
            assert False
    def get_ram_wire(name, msb, lsb, default="1'b0"):
        wire_bits = []
        for i in range(msb, lsb-1, -1):
            if msb != lsb:
                n = "ram/%s_%d" % (name, i)
            else:
                n = "ram/" + name
            b = seg_to_net((tile[0], tile[1], n), default)
            b = seg_to_net((tile[0], tile[1]+1, n), b)
            if len(wire_bits) != 0 or b != default or i == lsb:
                wire_bits.append(b)
        if len(wire_bits) > 1:
            return "{%s}" % ", ".join(wire_bits)
        return wire_bits[0]
    if get_ram_config('PowerUp') == (ic.device == "8k"):
        if not strip_comments:
            text_func.append("// RAM TILE %d %d" % tile)
        text_func.append("SB_RAM40_4K #(");
        text_func.append("  .READ_MODE(%d)," % ((1 if get_ram_config('CBIT_2') else 0) + (2 if get_ram_config('CBIT_3') else 0)));
        text_func.append("  .WRITE_MODE(%d)," % ((1 if get_ram_config('CBIT_0') else 0) + (2 if get_ram_config('CBIT_1') else 0)));
        for i in range(16):
            text_func.append("  .INIT_%X(256'h%s)%s" % (i, ic.ram_data[tile][i], "," if i < 15 else ""));
        text_func.append(") ram40_%d_%d (" % tile);
        text_func.append("  .WADDR(%s),"  % get_ram_wire('WADDR', 10, 0))
        text_func.append("  .RADDR(%s),"  % get_ram_wire('RADDR', 10, 0))
        text_func.append("  .MASK(%s),"  % get_ram_wire('MASK', 15, 0))
        text_func.append("  .WDATA(%s),"  % get_ram_wire('WDATA', 15, 0))
        text_func.append("  .RDATA(%s),"  % get_ram_wire('RDATA', 15, 0))
        text_func.append("  .WE(%s),"  % get_ram_wire('WE', 0, 0))
        text_func.append("  .WCLKE(%s),"  % get_ram_wire('WCLKE', 0, 0, "1'b1"))
        text_func.append("  .WCLK(%s),"  % get_ram_wire('WCLK', 0, 0))
        text_func.append("  .RE(%s),"  % get_ram_wire('RE', 0, 0))
        text_func.append("  .RCLKE(%s),"  % get_ram_wire('RCLKE', 0, 0, "1'b1"))
        text_func.append("  .RCLK(%s)"  % get_ram_wire('RCLK', 0, 0))
        text_func.append(");")
        text_func.append("")

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
    net_in0 = seg_to_net((lut[0], lut[1], "lutff_%d/in_0" % lut[2]), "1'b0")
    net_in1 = seg_to_net((lut[0], lut[1], "lutff_%d/in_1" % lut[2]), "1'b0")
    net_in2 = seg_to_net((lut[0], lut[1], "lutff_%d/in_2" % lut[2]), "1'b0")
    net_in3 = seg_to_net((lut[0], lut[1], "lutff_%d/in_3" % lut[2]), "1'b0")
    net_out = seg_to_net((lut[0], lut[1], "lutff_%d/out" % lut[2]))
    if seq_bits[0] == "1":
        net_cout = seg_to_net((lut[0], lut[1], "lutff_%d/cout" % lut[2]))
        net_in1 = seg_to_net((lut[0], lut[1], "lutff_%d/in_1" % lut[2]), "1'b0")
        net_in2 = seg_to_net((lut[0], lut[1], "lutff_%d/in_2" % lut[2]), "1'b0")
        if lut[2] == 0:
            net_cin = seg_to_net((lut[0], lut[1], "carry_in_mux"))
            if icebox.get_carry_cascade_bit(tile) == "0":
                if not strip_comments:
                    text_wires.append("// Carry-In for (%d %d)" % (lut[0], lut[1]))
                text_wires.append("assign %s = %s;" % (net_cin, icebox.get_carry_bit(tile)))
                if not strip_comments:
                    text_wires.append("")
        else:
            net_cin = seg_to_net((lut[0], lut[1], "lutff_%d/cout" % (lut[2]-1)), "1'b0")
        carry_assigns.append([net_cout, "/* CARRY %2d %2d %2d */ (%s & %s) | ((%s | %s) & %s)" %
                (lut[0], lut[1], lut[2], net_in1, net_in2, net_in1, net_in2, net_cin)])
    if seq_bits[1] == "1":
        n = next_netname()
        text_wires.append("wire %s;" % n)
        if not strip_comments:
            text_wires.append("// FF %s" % (lut,))
            text_wires.append("")
        net_cen = seg_to_net((lut[0], lut[1], "lutff_global/cen"), "1'b1")
        net_clk = seg_to_net((lut[0], lut[1], "lutff_global/clk"), "1'b0")
        net_sr  = seg_to_net((lut[0], lut[1], "lutff_global/s_r"), "1'b0")
        if seq_bits[3] == "0":
            always_stmts.append("/* FF %2d %2d %2d */ always @(%sedge %s) if (%s) %s <= %s ? 1'b%s : %s;" %
                    (lut[0], lut[1], lut[2], "neg" if icebox.get_negclk_bit(tile) == "1" else "pos",
                    net_clk, net_cen, net_out, net_sr, seq_bits[2], n))
        else:
            always_stmts.append("/* FF %2d %2d %2d */ always @(%sedge %s, posedge %s) if (%s) %s <= 1'b%s; else if (%s) %s <= %s;" %
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
                return "1'b%s" % bits[0]
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

if do_collect:
    new_text_ports = set()
    vec_ports_min = dict()
    vec_ports_max = dict()
    vec_ports_dir = dict()
    for port in text_ports:
        match = re.match(r"(input|output|inout) (.*)\[(\d+)\] ?$", port);
        if match:
            vec_ports_min[match.group(2)] = min(vec_ports_min.setdefault(match.group(2), int(match.group(3))), int(match.group(3)))
            vec_ports_max[match.group(2)] = max(vec_ports_max.setdefault(match.group(2), int(match.group(3))), int(match.group(3)))
            vec_ports_dir[match.group(2)] = match.group(1)
        else:
            new_text_ports.add(port)
    for port, direct in list(vec_ports_dir.items()):
        min_idx = vec_ports_min[port]
        max_idx = vec_ports_max[port]
        new_text_ports.add("%s [%d:%d] %s " % (direct, max_idx, min_idx, port))
    text_ports = list(new_text_ports)

print("module %s (%s);\n" % (modname, ", ".join(text_ports)))

new_text_wires = list()
new_text_regs = list()
new_text_raw = list()
for line in text_wires:
    match = re.match(r"wire ([^ ;]+)(.*)", line)
    if match:
        if strip_comments:
            name = match.group(1)
            if name.startswith("\\"):
                name += " "
            if match.group(1) in wire_to_reg:
                new_text_regs.append(name)
            else:
                new_text_wires.append(name)
            continue
        else:
            if match.group(1) in wire_to_reg:
                line = "reg " + match.group(1) + " = 0" + match.group(2)
    if strip_comments:
        new_text_raw.append(line)
    else:
        print(line)
for names in [new_text_wires[x:x+10] for x in range(0, len(new_text_wires), 10)]:
    print("wire %s;" % ", ".join(names))
for names in [new_text_regs[x:x+10] for x in range(0, len(new_text_regs), 10)]:
    print("reg %s = 0;" % " = 0, ".join(names))
if strip_comments:
    for line in new_text_raw:
        print(line)
    print()

if do_collect:
    for port, direct in list(vec_ports_dir.items()):
        min_idx = vec_ports_min[port]
        max_idx = vec_ports_max[port]
        for i in range(min_idx, max_idx+1):
            if direct == "input":  print("assign %s[%d] = %s [%d];"  % (port, i, port, i))
            if direct == "output": print("assign %s [%d] = %s[%d] ;" % (port, i, port, i))
            if direct == "inout":  print("tran(%s [%d], %s[%d] );"   % (port, i, port, i))
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

if failed_drivers_check:
    print("// Single-driver-check failed for %d nets:" % len(failed_drivers_check))
    print("// %s" % " ".join(failed_drivers_check))
    assert False

