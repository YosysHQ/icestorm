#!/usr/bin/env python3

import os, sys, re

device = "up5k"

pins = "2 3 4 6 9 10 11 12 13 18 19 20 21 25 26 27 28 31 32 34 35 36 37 38 42 43 44 45 46 47 48".split()

# This script is designed to determine the routing of 5k SPRAM signals,
# and the location of the enable config bits

spram_locs = [(0, 0, 1), (0, 0, 2), (25, 0, 3), (25, 0, 4)]
#spram_locs = [(0, 0, 1)]
spram_data = { }

spram_signals = ["WREN", "CHIPSELECT", "CLOCK", "STANDBY", "SLEEP", "POWEROFF"]

for i in range(14):
    spram_signals.append("ADDRESS[%d]" % i)
    
for i in range(16):
    spram_signals.append("DATAIN[%d]" % i)
    
for i in range(16):
    spram_signals.append("DATAOUT[%d]" % i)
    
for i in range(4):
    spram_signals.append("MASKWREN[%d]" % i)
    
fuzz_options = ["ADDRESS", "DATAIN", "MASKWREN", "DATAOUT"]

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
            if splitline[1][:5] == "CBIT_":
                bitidx = int(splitline[1][5:])
                bits.add((current_x, current_y, splitline[1].strip()))    
    return bits
            
if not os.path.exists("./work_spram"):
    os.mkdir("./work_spram")

for loc in spram_locs:
    x, y, z = loc
    net_map = {}
    for sig in spram_signals:
        net_map[sig] = set()
    net_map["SPRAM_EN"] = set() # actually a CBIT not a net
    
    for n in fuzz_options:
        with open("./work_spram/spram.v","w") as f:
            print("""
            module top(
            input WREN,
            input CHIPSELECT,
            input CLOCK,
            input STANDBY,
            input SLEEP,
            input POWEROFF,
            """, file=f)
            if n == "ADDRESS":
                print("\t\t\tinput [13:0] ADDRESS,", file=f)
            if n == "DATAIN":
                print("\t\t\tinput [15:0] DATAIN,", file=f)
            if n == "MASKWREN":
                print("\t\t\tinput [3:0] MASKWREN,", file=f)
            if n == "DATAOUT":
                print("\t\t\toutput [15:0] DATAOUT);", file=f)
            else:
                print("\t\t\toutput [0:0] DATAOUT);", file=f) #some dataout is always required to prevent optimisation away
            
            addr_net = "ADDRESS" if n == "ADDRESS" else ""
            din_net = "DATAIN" if n == "DATAIN" else ""
            mwren_net = "MASKWREN" if n == "MASKWREN" else ""
                
            print("""
            SB_SPRAM256KA spram_i
              (
                .ADDRESS(%s),
                .DATAIN(%s),
                .MASKWREN(%s),
                .WREN(WREN),
                .CHIPSELECT(CHIPSELECT),
                .CLOCK(CLOCK),
                .STANDBY(STANDBY),
                .SLEEP(SLEEP),
                .POWEROFF(POWEROFF),
                .DATAOUT(DATAOUT)
              );
            """ % (addr_net, din_net, mwren_net), file=f)
            print("endmodule",file=f)
        pin2net = {}
        with open("./work_spram/spram.pcf","w") as f:
            temp_pins = list(pins)
            for sig in spram_signals:
                if sig.startswith("ADDRESS") and n != "ADDRESS":
                    continue
                if sig.startswith("DATAIN") and n != "DATAIN":
                    continue
                if sig.startswith("MASKWREN") and n != "MASKWREN":
                    continue
                if sig.startswith("DATAOUT") and n != "DATAOUT" and sig != "DATAOUT[0]":
                    continue
                
                if len(temp_pins) == 0:
                    sys.stderr.write("ERROR: no remaining pins to alloc")
                    sys.exit(1)
                
                pin = temp_pins.pop()
                pin2net[pin] = sig
                print("set_io %s %s" % (sig, pin), file=f)
            print("set_location spram_i %d %d %d" % loc, file=f)
        retval = os.system("bash ../../icecube.sh -" + device + " ./work_spram/spram.v > ./work_spram/icecube.log 2>&1")
        if retval != 0:
            sys.stderr.write('ERROR: icecube returned non-zero error code\n')
            sys.exit(1)
        retval = os.system("../../../icebox/icebox_explain.py ./work_spram/spram.asc > ./work_spram/spram.exp")
        if retval != 0:
            sys.stderr.write('ERROR: icebox_explain returned non-zero error code\n')
            sys.exit(1)
        retval = os.system("../../../icebox/icebox_vlog.py -l ./work_spram/spram.asc > ./work_spram/spram.vlog")
        if retval != 0:
            sys.stderr.write('ERROR: icebox_vlog returned non-zero error code\n')
            sys.exit(1)
        with open("./work_spram/spram.vlog", "r") as f:
            parse_vlog(f, pin2net, net_map)
        bits = []
        with open("./work_spram/spram.exp", "r") as f:
            bits = parse_exp(f)
        net_map["SPRAM_EN"].update(bits)
    spram_data[loc] = net_map         

with open(device + "_spram_data.txt", "w") as f:
    for loc in spram_data:
        print("\t(%d, %d, %d): {" % loc, file=f)
        data = spram_data[loc]
        for net in sorted(data):
            cnets = []
            for cnet in data[net]:
                cnets.append("(%d, %d, \"%s\")" % cnet)
            print("\t\t%s %s, " % (("\"" + net.replace("[","_").replace("]","") + "\":").ljust(24), " ".join(cnets)), file=f)
        print("\t},", file=f)
