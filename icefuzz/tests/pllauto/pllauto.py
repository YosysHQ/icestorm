#!/usr/bin/env python3

import os, sys
# PLL automatic fuzzing script (WIP)

device = "up5k"

# PLL config bits to be fuzzed
# These must be in an order such that a config with bit i set doesn't set any other undiscovered bits yet
# e.g. PLL_TYPE must be fuzzed first as these will need to be set later on by virtue of enabling the PLL

fuzz_bits = [
    "PLLTYPE_1",
    "PLLTYPE_2",
    "PLLTYPE_0", #NB: as per the rule above this comes later is it can only be set by also setting 1 or 2
    
    "FEEDBACK_PATH_0",
    "FEEDBACK_PATH_1",
    "FEEDBACK_PATH_2",
    
    "PLLOUT_SELECT_A_0",
    "PLLOUT_SELECT_A_1",
    
    "PLLOUT_SELECT_B_0",
    "PLLOUT_SELECT_B_1",
    
    "SHIFTREG_DIV_MODE",
    
    "FDA_FEEDBACK_0",
    "FDA_FEEDBACK_1",
    "FDA_FEEDBACK_2",
    "FDA_FEEDBACK_3",

    "FDA_RELATIVE_0",
    "FDA_RELATIVE_1",
    "FDA_RELATIVE_2",
    "FDA_RELATIVE_3",
    
    "DIVR_0",
    "DIVR_1",
    "DIVR_2",
    "DIVR_3",
    
    "DIVF_0",
    "DIVF_1",
    "DIVF_2",
    "DIVF_3",
    "DIVF_4",
    "DIVF_5",
    "DIVF_6",
    
    #DIVQ_0 is missing, see comments later on
    "DIVQ_1",
    "DIVQ_2",
    
    "FILTER_RANGE_0",
    "FILTER_RANGE_1",
    "FILTER_RANGE_2",
    
    "TEST_MODE",
    
    "DELAY_ADJMODE_FB", #these come at the end in case they set FDA_RELATIVE??
    "DELAY_ADJMODE_REL"
]

# Boilerplate code based on the icefuzz script
code_prefix = """
module top(packagepin, a, b, w, x, y, z, extfeedback, bypass, resetb, lock, latchinputvalue, sdi, sdo, sclk, dynamicdelay_0, dynamicdelay_1, dynamicdelay_2, dynamicdelay_3, dynamicdelay_4, dynamicdelay_5, dynamicdelay_6, dynamicdelay_7);
input packagepin;
input a;
input b;
output w;
output x;
output reg y;
output reg z;
input extfeedback;
input bypass;
input resetb;
output lock;
input latchinputvalue;
input sdi;
output sdo;
input sclk;
wire plloutcorea;
wire plloutcoreb;
wire plloutglobala;
wire plloutglobalb;
assign w = plloutcorea ^ a;
assign x = plloutcoreb ^ b;
always @(posedge plloutglobala) y <= a;
always @(posedge plloutglobalb) z <= b;
input dynamicdelay_0;
input dynamicdelay_1;
input dynamicdelay_2;
input dynamicdelay_3;
input dynamicdelay_4;
input dynamicdelay_5;
input dynamicdelay_6;
input dynamicdelay_7;
"""

def get_param_value(param_name, param_size, fuzz_bit):
    param = str(param_size) + "'b";
    for i in range(param_size - 1, -1, -1):
        if fuzz_bit == param_name + "_" + str(i):
            param += '1'
        else:
            param += '0'
    return param
def inst_pll(fuzz_bit):
    pll_type = "SB_PLL40_2F_PAD" #default to this as it's most flexible
    
    if fuzz_bit == "PLLTYPE_0":
        pll_type = "SB_PLL40_CORE"
    elif fuzz_bit == "PLLTYPE_1":
        pll_type = "SB_PLL40_PAD"
    elif fuzz_bit == "PLLTYPE_2":
        pll_type = "SB_PLL40_2_PAD"        
        
    v = pll_type + " pll_inst (\n"
    if pll_type == "SB_PLL40_CORE":
        v += "\t.REFERENCECLK(referenceclk), \n"
    else:
        v += "\t.PACKAGEPIN(packagepin), \n"
    v += "\t.RESETB(resetb),\n"
    v += "\t.BYPASS(bypass),\n"
    v += "\t.EXTFEEDBACK(extfeedback),\n"
    v += "\t.LOCK(lock),\n"
    v += "\t.LATCHINPUTVALUE(latchinputvalue),\n"
    v += "\t.SDI(sdi),\n"
    v += "\t.SDO(sdo),\n"
    v += "\t.SCLK(sclk),\n"
    if pll_type == "SB_PLL40_2F_PAD" or pll_type == "SB_PLL40_2_PAD":
      v += "\t.PLLOUTCOREA(plloutcorea),\n"
      v += "\t.PLLOUTGLOBALA(plloutglobala),\n"
      v += "\t.PLLOUTCOREB(plloutcoreb),\n"
      v += "\t.PLLOUTGLOBALB(plloutglobalb),\n"
    else:
      v += "\t.PLLOUTCORE(plloutcorea),\n"
      v += "\t.PLLOUTGLOBAL(plloutglobala),\n"    
    v += "\t.DYNAMICDELAY({dynamicdelay_7, dynamicdelay_6, dynamicdelay_5, dynamicdelay_4, dynamicdelay_3, dynamicdelay_2, dynamicdelay_1, dynamicdelay_0})\n"
    v += ");\n"
    
    v += "defparam pll_inst.DIVR = " + get_param_value("DIVR", 4, fuzz_bit) + ";\n"
    v += "defparam pll_inst.DIVF = " + get_param_value("DIVF", 7, fuzz_bit) + ";\n"
    v += "defparam pll_inst.DIVQ = " + get_param_value("DIVQ", 3, fuzz_bit) + ";\n"
    v += "defparam pll_inst.FILTER_RANGE = " + get_param_value("FILTER_RANGE", 3, fuzz_bit) + ";\n"
    
    if fuzz_bit == "FEEDBACK_PATH_0":
        v += "defparam pll_inst.FEEDBACK_PATH = \"SIMPLE\";\n"
    elif fuzz_bit == "FEEDBACK_PATH_1":
        v += "defparam pll_inst.FEEDBACK_PATH = \"PHASE_AND_DELAY\";\n"
    elif fuzz_bit == "FEEDBACK_PATH_2":
        v += "defparam pll_inst.FEEDBACK_PATH = \"EXTERNAL\";\n"
    else:
        v += "defparam pll_inst.FEEDBACK_PATH = \"DELAY\";\n"
        
    v += "defparam pll_inst.DELAY_ADJUSTMENT_MODE_FEEDBACK = \"" + ("DYNAMIC" if (fuzz_bit == "DELAY_ADJMODE_FB") else "FIXED") + "\";\n"
    v += "defparam pll_inst.FDA_FEEDBACK = " + get_param_value("FDA_FEEDBACK", 4, fuzz_bit) + ";\n"
    v += "defparam pll_inst.DELAY_ADJUSTMENT_MODE_RELATIVE = \"" + ("DYNAMIC" if (fuzz_bit == "DELAY_ADJMODE_REL") else "FIXED") + "\";\n"
    v += "defparam pll_inst.FDA_RELATIVE = " + get_param_value("FDA_RELATIVE", 4, fuzz_bit) + ";\n"
    v += "defparam pll_inst.SHIFTREG_DIV_MODE = " + ("1'b1" if (fuzz_bit == "SHIFTREG_DIV_MODE") else "1'b0") + ";\n"
    

        
    if pll_type == "SB_PLL40_2F_PAD" or pll_type == "SB_PLL40_2_PAD":
        if pll_type == "SB_PLL40_2F_PAD":
            if fuzz_bit == "PLLOUT_SELECT_A_0":
                v += "defparam pll_inst.PLLOUT_SELECT_PORTA = \"GENCLK_HALF\";\n"
            elif fuzz_bit == "PLLOUT_SELECT_A_1":
                v += "defparam pll_inst.PLLOUT_SELECT_PORTA = \"SHIFTREG_90deg\";\n"
            else:
                v += "defparam pll_inst.PLLOUT_SELECT_PORTA = \"GENCLK\";\n"
        if fuzz_bit == "PLLOUT_SELECT_B_0":
            v += "defparam pll_inst.PLLOUT_SELECT_PORTB = \"GENCLK_HALF\";\n"
        elif fuzz_bit == "PLLOUT_SELECT_B_1":
            v += "defparam pll_inst.PLLOUT_SELECT_PORTB = \"SHIFTREG_90deg\";\n"
        else:
            v += "defparam pll_inst.PLLOUT_SELECT_PORTB = \"GENCLK\";\n"
    else:
        if fuzz_bit == "PLLOUT_SELECT_A_0":
            v += "defparam pll_inst.PLLOUT_SELECT = \"GENCLK_HALF\";\n"
        elif fuzz_bit == "PLLOUT_SELECT_A_1":
            v += "defparam pll_inst.PLLOUT_SELECT = \"SHIFTREG_90deg\";\n"
        else:
            v += "defparam pll_inst.PLLOUT_SELECT = \"GENCLK\";\n"
    v += "defparam pll_inst.TEST_MODE = " + ("1'b1" if (fuzz_bit == "TEST_MODE") else "1'b0") + ";\n"
    
    return v;

def make_vlog(fuzz_bit):
    vlog = code_prefix
    vlog += inst_pll(fuzz_bit)
    vlog += "endmodule"
    return vlog

known_bits = []

# Set to true to continue even if multiple bits are changed (needed because
# of the issue discusssed below)
show_all_bits = False #TODO: make this an argument

device = "up5k" #TODO: environment variable?

#HACK: icecube doesn't let you set all of the DIVQ bits to 0,
#which makes fuzzing early on annoying as there is never a case
#with just 1 bit set. So a tiny bit of semi-manual work is needed
#first to discover this (basically run this script with show_all_bits=True
#and look for the stuck bit)
#TODO: clever code could get rid of this
divq_bit0 = {
    "up5k" : (11, 31, 3),
    "lm4k" : (11, 0, 3)
}

#Return a list of PLL config bits in the format (x, y, bit)
def parse_exp(expfile):
    current_x = 0
    current_y = 0
    bits = []
    with open(expfile, 'r') as f:
        for line in f:
            splitline = line.split(' ')
            if splitline[0] == ".io_tile":
                current_x = int(splitline[1])
                current_y = int(splitline[2])
            elif splitline[0] == "PLL":
                if splitline[1][:10] == "PLLCONFIG_":
                    bitidx = int(splitline[1][10:])
                    bits.append((current_x, current_y, bitidx))    
    return bits

#Convert a bit tuple as returned from the above to a nice string
def bit_to_str(bit):
    return "(%d, %d, \"PLLCONFIG_%d\")" % bit

#The main fuzzing function
def do_fuzz():
    if not os.path.exists("./work_pllauto"):
        os.mkdir("./work_pllauto")
    known_bits.append(divq_bit0[device])
    with open("pll_data_" + device + ".txt", 'w') as dat:
        for fuzz_bit in fuzz_bits:
            vlog = make_vlog(fuzz_bit)
            with open("./work_pllauto/pllauto.v", 'w') as f:
                f.write(vlog)
            retval = os.system("bash ../../icecube.sh -" + device + " ./work_pllauto/pllauto.v > ./work_pllauto/icecube.log 2>&1")
            if retval != 0:
                sys.stderr.write('ERROR: icecube returned non-zero error code\n')
                sys.exit(1)
            retval = os.system("../../../icebox/icebox_explain.py ./work_pllauto/pllauto.asc > ./work_pllauto/pllauto.exp")
            if retval != 0:
                sys.stderr.write('ERROR: icebox_explain returned non-zero error code\n')
                sys.exit(1)
            pll_bits = parse_exp("./work_pllauto/pllauto.exp")
            new_bits = []
            for set_bit in pll_bits:
                if not (set_bit in known_bits):
                    new_bits.append(set_bit)
            if len(new_bits) == 0:
                sys.stderr.write('ERROR: no new bits set when setting config bit ' + fuzz_bit + '\n')
                sys.exit(1)      
            if len(new_bits) > 1:
                sys.stderr.write('ERROR: multiple new bits set when setting config bit ' + fuzz_bit + '\n')
                for bit in new_bits:
                    sys.stderr.write('\t' + bit_to_str(bit) + '\n')
                if not show_all_bits:
                    sys.exit(1)
            if len(new_bits) == 1:
                known_bits.append(new_bits[0])
                #print DIVQ_0 at the right moment, as it's not fuzzed normally
                if fuzz_bit == "DIVQ_1":
                    print(("\"DIVQ_0\":").ljust(24) + bit_to_str(divq_bit0[device]) + ",")
                    dat.write(("\"DIVQ_0\":").ljust(24) + bit_to_str(divq_bit0[device]) + ",\n")
                print(("\"" + fuzz_bit + "\":").ljust(24) + bit_to_str(new_bits[0]) + ",")
                dat.write(("\"" + fuzz_bit + "\":").ljust(24) + bit_to_str(new_bits[0]) + ",\n")
do_fuzz()