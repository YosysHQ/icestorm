#!/usr/bin/env python3

import re, sys, os

device_class = os.getenv("ICEDEVICE")

def sort_bits_key(a):
    if a[0] == "!": a = a[1:]
    return re.sub(r"\d+", lambda m: "%02d" % int(m.group(0)), a)

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
            line = re.sub(r"^MAC16 functional bit:", "IpConfig", line)
            line = re.sub(r"^Hard IP config bit:", "IpConfig", line)

            line = line.split()
            if line[0] == "routing":
                if line[3] == "wire_gbuf/in": line[3] = "fabout"
                raw_db.append((bit, (line[0], line[1], line[3])))
            elif line[0] == "IoCtrl":
                line[1] = re.sub(r"^.*?_", "", line[1]).replace("_en", "")
                # LP384 chips have reversed IE_0/IE_1 and REN_0/REN_1 bit assignments
                # we simply use the assignments for 1k/8k for all chips and fix it in ieren_db
                if bit == "B6[3]" and line == ['IoCtrl', 'IE_0']: continue
                if bit == "B9[3]" and line == ['IoCtrl', 'IE_1']: continue
                if bit == "B1[3]" and line == ['IoCtrl', 'REN_0']: continue
                if bit == "B6[2]" and line == ['IoCtrl', 'REN_1']: continue
                # Ignore some additional configuration bits that sneaked in via ice5k fuzzing
                if line[0] == "IoCtrl" and line[1].startswith("cf_bit_"): continue
                if line[0] == "IoCtrl" and line[1].startswith("extra_padeb_test_"): continue
                raw_db.append((bit, (line[0], line[1])))
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
                line[1] = re.sub(r"(LH|MEM[BT]|MULT\d|IPCON)_colbuf_cntl_", "glb_netwk_", line[1])
                if m.group(1) == "7":
                    line[1] = re.sub(r"glb_netwk_", "8k_glb_netwk_", line[1])
                elif m.group(1) in ["1", "2"]:
                    line[1] = re.sub(r"glb_netwk_", "1k_glb_netwk_", line[1])
                raw_db.append((bit, (line[0], line[1])))
            elif line[0] == "Cascade":
                match = re.match("LH_LC0(\d)_inmux02_5", line[1])
                if match:
                    raw_db.append((bit, ("buffer", "wire_logic_cluster/lc_%d/lout" % (int(match.group(1))-1), "input_2_%s" % match.group(1))))
                else:
                    match = re.match("MEMT_LC\d+_inmux\d+_bram_cbit_(\d+)", line[1])
                    if match:
                        raw_db.append((bit, ("RamCascade", "CBIT_%d" % int(match.group(1)))))
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
            elif line[0] == "IpConfig":
                line[1] = re.sub(r"MULT\d_bram_cbit_", "CBIT_", line[1]) #not a typo, sometimes IP config bits are in DSP tiles and use a MULT prefix...
                line[1] = re.sub(r"IPCON_bram_cbit_", "CBIT_", line[1])    
                raw_db.append((bit, (line[0], line[1])))       
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
        entry = (",".join(sorted(bits, key=sort_bits_key)),) + func
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

for device_class in ["8k"]:
  with open("database_ramb_%s.txt" % (device_class, ), "w") as f:
      for entry in read_database("bitdata_ramb_%s.txt" % (device_class, ), "ramb_" + device_class):
          print("\t".join(entry), file=f)

  with open("database_ramt_%s.txt" % (device_class, ), "w") as f:
      for entry in read_database("bitdata_ramt_%s.txt" % (device_class, ), "ramt_" + device_class):
          print("\t".join(entry), file=f)

for dsp_idx in range(4):
  with open("database_dsp%d_5k.txt" % (dsp_idx, ), "w") as f:
      for entry in read_database("bitdata_dsp%d_5k.txt" % (dsp_idx, ), "dsp%d_5" % (dsp_idx, )):
          print("\t".join(entry), file=f)
with open("database_ipcon_5k.txt", "w") as f:
    for entry in read_database("bitdata_ipcon_5k.txt", "ipcon"):
        print("\t".join(entry), file=f)
