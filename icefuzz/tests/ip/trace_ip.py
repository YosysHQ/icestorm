#!/usr/bin/env python3

import os, sys, re

device = "up5k"

pins = "2 3 4 6 9 10 11 12 13 18 19 20 21 25 26 27 28 31 32 34 35 36 37 38 42 43 44 45 46 47 48".split()

# This is the master IP reverse engineering script for three similar IPs: I2C, SPI and LEDDA_IP
ip_types = ["I2C", "SPI", "LEDDA_IP"]
ip_locs = { }
ip_locs["I2C"] = [(0, 31, 0), (25, 31, 0)]
ip_locs["SPI"] = [(0, 0, 0), (25, 0, 1)]
ip_locs["LEDDA_IP"] = [(0, 31, 2)]
#spram_locs = [(0, 0, 1)]
ip_data = { }

#signals[x][0] -> inputs, signals[x][1] ->outputs
ip_signals = {}
ip_signals["I2C"] = [["SBCLKI", "SBRWI", "SBSTBI", "SCLI", "SDAI"], 
                     ["SBACKO", "I2CIRQ", "I2CWKUP", "SCLO", "SCLOE", "SDAO", "SDAOE"]]
ip_signals["SPI"] = [["SBCLKI", "SBRWI", "SBSTBI", "MI", "SI", "SCKI", "SCSNI"],
                     ["SBACKO", "SPIIRQ", "SPIWKUP", "SO", "SOE", "MO", "MOE", "SCKO", "SCKOE"]]

# LEDDRST is missing because it doesn't really exist...
ip_signals["LEDDA_IP"] = [["LEDDCS", "LEDDCLK", "LEDDDEN", "LEDDEXE"], ["PWMOUT0", "PWMOUT1", "PWMOUT2", "LEDDON"]]

fixed_cbits = {}

fixed_cbits[("I2C", (0, 31, 0))]  = ["BUS_ADDR74_0", "I2C_SLAVE_INIT_ADDR_0"]
fixed_cbits[("I2C", (25, 31, 0))] = ["BUS_ADDR74_0", "BUS_ADDR74_1", "I2C_SLAVE_INIT_ADDR_1"]

fixed_cbits[("SPI", (0, 0, 0))]  = []
fixed_cbits[("SPI", (25, 0, 1))] = ["BUS_ADDR74_1"] # WARNING: this is documented as BUS_ADDR74_0, but this is wrong and will cause icecube to fail. May be the same across devices

fuzz_cbits = {}
fuzz_cbits["I2C"] = ["SDA_INPUT_DELAYED", "SDA_OUTPUT_DELAYED"]

# Don't add slave address to the list, despite confusing primitive declaration,
# it's only set in registers not the bitstream

#for i in range(2, 10):
    #fuzz_cbits["I2C"].append("I2C_SLAVE_INIT_ADDR_%d" % i)

for i in range(8):
    ip_signals["I2C"][0].append("SBADRI%d" % i)
    ip_signals["SPI"][0].append("SBADRI%d" % i)
for i in range(4):
    ip_signals["LEDDA_IP"][0].append("LEDDADDR%d" % i)
    
for i in range(8):
    ip_signals["I2C"][0].append("SBDATI%d" % i)
    ip_signals["SPI"][0].append("SBDATI%d" % i)
    ip_signals["LEDDA_IP"][0].append("LEDDDAT%d" % i)
    
for i in range(8):
    ip_signals["I2C"][1].append("SBDATO%d" % i)
    ip_signals["SPI"][1].append("SBDATO%d" % i)
    
for i in range(4):
    ip_signals["SPI"][1].append("MCSNO%d" % i)
    ip_signals["SPI"][1].append("MCSNOE%d" % i)

fuzz_net_options = {}
fuzz_net_options["I2C"] = ["SBADRI", "SBDATI", "SBDATO"]
fuzz_net_options["SPI"] = ["SBADRI", "SBDATI", "SBDATO", "MCSN"]
fuzz_net_options["LEDDA_IP"] = ["LEDDADDR", "LEDDDAT"]

    
available_cbits = {}
available_cbits["I2C"] = [("BUS_ADDR74", 4), ("I2C_SLAVE_INIT_ADDR", 10)]
available_cbits["SPI"] = [("BUS_ADDR74", 4)]

# Return a param value in "Lattice style"
def get_param_value(param_size, param_name, set_cbits):
    val = "\"0b"
    for i in range(param_size):
        if param_name + "_" + str((param_size - 1) - i) in set_cbits:
            val += "1"
        else:
            val += "0"
    val += "\""
    return val

# Build the output files for a given IP and config, returning
# the pin2net map
def make_ip(ip_type, ip_loc, fuzz_opt, set_cbits):
    used_inputs = [ ]
    used_outputs = [ ]
    for insig in ip_signals[ip_type][0]:
        ignore = False
        for o in fuzz_net_options[ip_type]:
            if o != fuzz_opt and insig.startswith(o):
                ignore = True
        if not ignore:
            used_inputs.append(insig)
    for outsig in ip_signals[ip_type][1]:
        ignore = False
        for o in fuzz_net_options[ip_type]:
            if o != fuzz_opt and outsig.startswith(o):
                ignore = True
        if not ignore:
            used_outputs.append(outsig)
    all_sigs = used_inputs + used_outputs
    all_cbits = set()
    all_cbits.update(set_cbits)
    if (ip_type, ip_loc) in fixed_cbits:
        all_cbits.update(fixed_cbits[(ip_type, ip_loc)])
    with open("./work_ip/ip.v", "w") as f:
        print("module top(", file=f)
        for s in used_inputs:
            print("input %s," % s, file=f)
        for s in used_outputs[:-1]:
            print("output %s," % s, file=f)
        print("output %s);" % used_outputs[-1], file=f)
        print("SB_%s" % ip_type, file=f)
        if ip_type in available_cbits:
            print("\t#(", file=f)
            for p in available_cbits[ip_type]:
                name, width = p
                comma = "," if p != available_cbits[ip_type][-1] else ""
                print("\t\t.%s(%s)%s" % (name, get_param_value(width, name, all_cbits), comma), file=f)
            print("\t)", file=f)
        print("\tip_inst (",file=f)
        for sig in all_sigs[:-1]:
            print("\t\t.%s(%s)," % (sig, sig), file=f)
        print("\t\t.%s(%s)" % (all_sigs[-1], all_sigs[-1]), file=f)
        print("\t)", file=f)
        if "SDA_INPUT_DELAYED" in all_cbits:
            print("\t/* synthesis SDA_INPUT_DELAYED=1 */", file=f)
        else:
            print("\t/* synthesis SDA_INPUT_DELAYED=0 */", file=f)
        if "SDA_OUTPUT_DELAYED" in all_cbits:
            print("\t/* synthesis SDA_OUTPUT_DELAYED=1 */", file=f)
        else:
            print("\t/* synthesis SDA_OUTPUT_DELAYED=0 */", file=f)
        print(";", file=f)
        print("endmodule", file=f)
    pin2net = {}
    with open("./work_ip/ip.pcf","w") as f:
        temp_pins = list(pins)
        for sig in all_sigs:
            if len(temp_pins) == 0:
                sys.stderr.write("ERROR: no remaining pins to alloc")
                sys.exit(1)
            pin = temp_pins.pop()
            pin2net[pin] = sig
            print("set_io %s %s" % (sig, pin), file=f)
        print("set_location ip_inst %d %d %d" % ip_loc, file=f)
    return pin2net
#Parse the output of an icebox vlog file to determine connectivity
def parse_vlog(f, pin2net, net_map):
    current_net = None
    
    for line in f:
        m = re.match(r"wire ([a-zA-Z0-9_]+);", line)
        if m:
            net = m.group(1)
            mp = re.match(r"pin_([a-zA-Z0-9]+)", net)
            if mp:
                pin = mp.group(1)
                if pin in pin2net:
                    current_net = pin2net[pin]
                else:
                    current_net = None
            else:
                current_net = None
        elif current_net is not None:
            m = re.match(r"// \((\d+), (\d+), '([a-zA-Z0-9_/]+)'\)", line)
            if m:
                x = int(m.group(1))
                y = int(m.group(2)) 
                net = m.group(3)
                if not (net.startswith("sp") or net.startswith("glb") or net.startswith("neigh") or net.startswith("io") or net.startswith("local") or net.startswith("fabout")):
                    net_map[current_net].add((x, y, net))
def parse_exp(f):
    current_x = 0
    current_y = 0
    bits = set()
    for line in f:
        splitline = line.split(' ')
        if splitline[0].endswith("_tile"):
            current_x = int(splitline[1])
            current_y = int(splitline[2])
        elif splitline[0] == "IpConfig":
            bits.add((current_x, current_y, splitline[1].strip()))    
    return bits
            
if not os.path.exists("./work_ip"):
    os.mkdir("./work_ip")
for ip in ip_types:
    ip_data[ip] = {}
    for loc in ip_locs[ip]:
        x, y, z = loc
        net_cbit_map = {}
        init_cbits = []
        for sig in ip_signals[ip][0]:
            net_cbit_map[sig] = set()
        for sig in ip_signals[ip][1]:
            net_cbit_map[sig] = set()
        first = True
        for state in ["FUZZ_NETS", "FUZZ_CBITS"]:
            fuzz_options = None
            if state == "FUZZ_NETS":
                fuzz_options = fuzz_net_options[ip]
            else:
                if ip in fuzz_cbits:
                    fuzz_options = fuzz_cbits[ip]
                else:
                    fuzz_options = []
            for n in fuzz_options:
                print("Fuzzing %s (%d, %d, %d) %s" % (ip, x, y, z, n))
                fuzz_nets = fuzz_net_options[ip][0]
                if state == "FUZZ_NETS":
                    fuzz_nets = n
                set_cbits = set()
                if state == "FUZZ_CBITS":
                    set_cbits.add(n)
                pin2net = make_ip(ip, loc, fuzz_nets, set_cbits)
                retval = os.system("bash ../../icecube.sh -" + device + " ./work_ip/ip.v > ./work_ip/icecube.log 2>&1")
                if retval != 0:
                    sys.stderr.write('ERROR: icecube returned non-zero error code\n')
                    sys.exit(1)
                retval = os.system("../../../icebox/icebox_explain.py ./work_ip/ip.asc > ./work_ip/ip.exp")
                if retval != 0:
                    sys.stderr.write('ERROR: icebox_explain returned non-zero error code\n')
                    sys.exit(1)
                retval = os.system("../../../icebox/icebox_vlog.py -l ./work_ip/ip.asc > ./work_ip/ip.vlog")
                if retval != 0:
                    sys.stderr.write('ERROR: icebox_vlog returned non-zero error code\n')
                    sys.exit(1)
                with open("./work_ip/ip.vlog", "r") as f:
                    parse_vlog(f, pin2net, net_cbit_map)
                bits = []
                with open("./work_ip/ip.exp", "r") as f:
                    bits = parse_exp(f)
                if first:
                    idx = 0
                    for bit in bits:
                        init_cbits.append(bit)
                        if len(bits) == 1:
                            net_cbit_map[ip + "_ENABLE"] = [bit]
                        else:
                            net_cbit_map[ip + "_ENABLE_" + str(idx)] = [bit]
                        idx += 1
                for bit in init_cbits:
                    if bit not in bits:
                        bx, by, bn = bit
                        print('WARNING: while fuzzing %s (%d, %d, %d) bit (%d, %d, %s) has unknown function (not always set)' % 
                              (ip, x, y, z, bx, by, bn))
                new_bits = []
                for bit in bits:
                    if bit not in init_cbits:
                        new_bits.append(bit)
                if state == "FUZZ_NETS" and len(new_bits) != 0:
                    for bit in new_bits:
                        bx, by, bn = bit
                        print('WARNING: while fuzzing %s (%d, %d, %d) bit (%d, %d, %s) has unknown function (not always set)' % 
                              (ip, x, y, z, bx, by, bn))
                elif state == "FUZZ_CBITS":
                    if len(new_bits) == 0:
                        print('WARNING: while fuzzing %s (%d, %d, %d) param %s causes no change' % 
                              (ip, x, y, z, n))
                    else:
                        idx = 0
                        for bit in new_bits:
                            if len(new_bits) == 1:
                                net_cbit_map[n] = [bit]
                            else:
                                net_cbit_map[n + "_" + str(idx)] = [bit]
                            idx += 1
                first = False
        ip_data[ip][loc] = net_cbit_map         

    with open(device + "_" + ip + "_data.txt", "w") as f:
        for loc in ip_data[ip]:
            x, y, z = loc
            print("\t(\"%s\", (%d, %d, %d)): {" % (ip, x, y, z), file=f)
            data = ip_data[ip][loc]
            for net in sorted(data):
                cnets = []
                for cnet in data[net]:
                    cnets.append("(%d, %d, \"%s\")" % cnet)
                print("\t\t%s %s, " % (("\"" + net.replace("[","_").replace("]","") + "\":").ljust(24), " ".join(cnets)), file=f)
            print("\t},", file=f)
