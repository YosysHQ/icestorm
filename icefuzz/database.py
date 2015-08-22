#!/usr/bin/env python3

import re, sys, os

def cmp_bits(a, b):
    if a[0] == "!": a = a[1:]
    if b[0] == "!": b = b[1:]
    a = re.sub(r"\d+", lambda m: "%02d" % int(m.group(0)), a)
    b = re.sub(r"\d+", lambda m: "%02d" % int(m.group(0)), b)
    return cmp(a, b)

def read_database(filename, tile_type):
    raw_db = list()
    route_to_buffer = set()
    add_mux_bits = dict()

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            m = re.match(r"\s*\((\d+)\s+(\d+)\)\s+(.*)", line)
            assert m
            bit = "B%d[%d]" % (int(m.group(2)), int(m.group(1)))
            line = m.group(3)
            line = re.sub(r"^Enable bit of Mux", "MuxEn", line)
            line = re.sub(r"^IO control bit:", "IoCtrl", line)
            line = re.sub(r"^Column buffer control bit:", "ColBufCtrl", line)
            line = re.sub(r"^Negative Clock bit", "NegClk", line)
            line = re.sub(r"^Cascade (buffer Enable )?bit:", "Cascade", line)
            line = re.sub(r"^Ram config bit:", "RamConfig", line)
            line = re.sub(r"^PLL config bit:", "PLL", line)
            line = re.sub(r"^Icegate Enable bit:", "Icegate", line)
            line = line.split()
            if line[0] == "routing":
                if line[3] == "wire_gbuf/in": line[3] = "fabout"
                raw_db.append((bit, (line[0], line[1], line[3])))
            elif line[0] == "IoCtrl":
                raw_db.append((bit, (line[0], re.sub(r"^.*?_", "", line[1]).replace("_en", ""))))
            elif line[0] in ("IOB_0", "IOB_1"):
                if line[1] != "IO":
                    raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "PLL":
                line[1] = re.sub(r"CLOCK_T_\d+_\d+_IO(LEFT|RIGHT|UP|DOWN)_", "pll_", line[1])
                line[1] = re.sub(r"pll_cf_bit_", "PLLCONFIG_", line[1])
                raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "ColBufCtrl":
                line[1] = re.sub(r"B?IO(LEFT|RIGHT)_", "IO_", line[1])
                line[1] = re.sub(r"IO_half_column_clock_enable_", "glb_netwk_", line[1])
                line[1] = re.sub(r"(LH|MEM[BT])_colbuf_cntl_", "glb_netwk_", line[1])
                if m.group(1) == "7":
                    line[1] = re.sub(r"glb_netwk_", "8k_glb_netwk_", line[1])
                elif m.group(1) in ["1", "2"]:
                    line[1] = re.sub(r"glb_netwk_", "1k_glb_netwk_", line[1])
                raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "Cascade":
                match = re.match("LH_LC0(\d)_inmux02_5", line[1])
                if match:
                    raw_db.append((bit, ("buffer", "wire_logic_cluster/lc_%d/out" % (int(match.group(1))-1), "input_2_%s" % match.group(1))))
                else:
                    raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "RamConfig":
                if line[1] == "MEMB_Power_Up_Control": line[1] = "PowerUp"
                line[1] = re.sub(r"MEMT_bram_cbit_", "CBIT_", line[1])
                raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "MuxEn":
                if line[4] == "wire_gbuf/in": line[4] = "fabout"
                if line[3].startswith("logic_op_"):
                    for prefix in ["IO_L.", "IO_R.", "IO_T.", "IO_B."]:
                        route_to_buffer.add((prefix + line[3], line[4]))
                        add_mux_bits.setdefault(prefix + line[3], set()).add((bit, ("buffer", prefix + line[3], line[4])))
                else:
                    raw_db.append((bit, ("buffer", line[3], line[4])))
                    route_to_buffer.add((line[3], line[4]))
            elif line[0] == "NegClk" or line[0] == "Icegate" or re.match(r"LC_\d+", line[0]):
                raw_db.append((bit, (line[0],)))
            elif line[0] == "Carry_In_Mux":
                continue
            else:
                print("unsupported statement: %s: %s" % (bit, line))
                assert False

    for i in range(len(raw_db)):
        if raw_db[i][1][0] == "routing" and (raw_db[i][1][1], raw_db[i][1][2]) in route_to_buffer:
            if raw_db[i][1][1] in add_mux_bits:
                for entry in add_mux_bits[raw_db[i][1][1]]:
                    raw_db.append(entry)
            raw_db[i] = (raw_db[i][0], ("buffer", raw_db[i][1][1], raw_db[i][1][2]))

    func_to_bits = dict()
    for entry in raw_db:
        func_to_bits.setdefault(entry[1], set()).add(entry[0])

    bit_groups = dict()
    for func, bits in list(func_to_bits.items()):
        for bit in bits:
            bit_groups[bit] = bit_groups.setdefault(bit, set()).union(bits)

    for func in func_to_bits:
        new_bits = set()
        for bit2 in func_to_bits[func]:
            for bit in bit_groups[bit2]:
                if bit in func_to_bits[func]:
                    new_bits.add(bit)
                else:
                    new_bits.add("!" + bit)
        func_to_bits[func] = new_bits

    database = list()
    for func in sorted(func_to_bits):
        bits = func_to_bits[func]
        entry = (",".join(sorted(bits, cmp_bits)),) + func
        database.append(entry)

    return database

with open("database_io.txt", "w") as f:
    for entry in read_database("bitdata_io.txt", "io"):
        print("\t".join(entry), file=f)

with open("database_logic.txt", "w") as f:
    for entry in read_database("bitdata_logic.txt", "logic"):
        print("\t".join(entry), file=f)

with open("database_ramb.txt", "w") as f:
    for entry in read_database("bitdata_ramb.txt", "ramb"):
        print("\t".join(entry), file=f)

with open("database_ramt.txt", "w") as f:
    for entry in read_database("bitdata_ramt.txt", "ramt"):
        print("\t".join(entry), file=f)

with open("database_ramb_8k.txt", "w") as f:
    for entry in read_database("bitdata_ramb_8k.txt", "ramb_8k"):
        print("\t".join(entry), file=f)

with open("database_ramt_8k.txt", "w") as f:
    for entry in read_database("bitdata_ramt_8k.txt", "ramt_8k"):
        print("\t".join(entry), file=f)

