#!/usr/bin/env python3
#
#  Copyright (C) 2015  Claire Xenia Wolf <claire@clairexen.net>
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

import iceboxdb
import re, sys, functools


if True:
    # icebox uses lots of regular expressions.
    # Supply cached versions of common re functions
    # to avoid re-calculating regular expression results
    # over and over again.
    re_cache_sizes = 2**14

    @functools.lru_cache(maxsize=re_cache_sizes)
    def re_match_cached(*args):
        return re.match(*args)

    @functools.lru_cache(maxsize=re_cache_sizes)
    def re_sub_cached(*args):
        return re.sub(*args)

    @functools.lru_cache(maxsize=re_cache_sizes)
    def re_search_cached(*args):
        return re.search(*args)
else:
    # Disable regular expression caching.
    re_match_cached = re.match
    re_sub_cached = re.sub
    re_search_cached = re.search


class iceconfig:
    def __init__(self):
        self.clear()

    def clear(self):
        self.max_x = 0
        self.max_y = 0
        self.device = ""
        self.warmboot = True
        self.logic_tiles = dict()
        self.io_tiles = dict()
        self.ramb_tiles = dict()
        self.ramt_tiles = dict()
        self.dsp_tiles = [dict() for i in range(4)]
        self.ipcon_tiles = dict()
        self.ram_data = dict()
        self.extra_bits = set()
        self.symbols = dict()
        self.tile_has_net.cache_clear()

    def setup_empty_384(self):
        self.clear()
        self.device = "384"
        self.max_x = 7
        self.max_y = 9

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def setup_empty_1k(self):
        self.clear()
        self.device = "1k"
        self.max_x = 13
        self.max_y = 17

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (3, 10):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def setup_empty_lm4k(self):
        self.clear()
        self.device = "lm4k"
        self.max_x = 25
        self.max_y = 21
        
        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (6, 19):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def setup_empty_u4k(self):
        self.clear()
        self.device = "u4k"
        self.max_x = 25
        self.max_y = 21

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (6, 19):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for x in [0, self.max_x]:
            for y in range(1, self.max_y):
                if y in [5, 13]:
                    self.dsp_tiles[0][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [6, 14]:
                    self.dsp_tiles[1][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [7, 15]:
                    self.dsp_tiles[2][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [8, 16]:
                    self.dsp_tiles[3][(x, y)] = ["0" * 54 for i in range(16)]
                else:
                    self.ipcon_tiles[(x, y)] = ["0" * 54 for i in range(16)]

    def setup_empty_5k(self):
        self.clear()
        self.device = "5k"
        self.max_x = 25
        self.max_y = 31

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (6, 19):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]
        for x in [0, self.max_x]:
            for y in range(1, self.max_y):
                if y in [5, 10, 15, 23]:
                    self.dsp_tiles[0][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [6, 11, 16, 24]:
                    self.dsp_tiles[1][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [7, 12, 17, 25]:
                    self.dsp_tiles[2][(x, y)] = ["0" * 54 for i in range(16)]
                elif y in [8, 13, 18, 26]:
                    self.dsp_tiles[3][(x, y)] = ["0" * 54 for i in range(16)]
                else:
                    self.ipcon_tiles[(x, y)] = ["0" * 54 for i in range(16)]
    def setup_empty_8k(self):
        self.clear()
        self.device = "8k"
        self.max_x = 33
        self.max_y = 33

        for x in range(1, self.max_x):
            for y in range(1, self.max_y):
                if x in (8, 25):
                    if y % 2 == 1:
                        self.ramb_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                    else:
                        self.ramt_tiles[(x, y)] = ["0" * 42 for i in range(16)]
                else:
                    self.logic_tiles[(x, y)] = ["0" * 54 for i in range(16)]

        for x in range(1, self.max_x):
            self.io_tiles[(x, 0)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(x, self.max_y)] = ["0" * 18 for i in range(16)]

        for y in range(1, self.max_y):
            self.io_tiles[(0, y)] = ["0" * 18 for i in range(16)]
            self.io_tiles[(self.max_x, y)] = ["0" * 18 for i in range(16)]

    def lookup_extra_bit(self, bit):
        assert self.device in extra_bits_db
        if bit in extra_bits_db[self.device]:
            return extra_bits_db[self.device][bit]
        return ("UNKNOWN_FUNCTION",)

    def tile(self, x, y):
        if (x, y) in self.io_tiles: return self.io_tiles[(x, y)]
        if (x, y) in self.logic_tiles: return self.logic_tiles[(x, y)]
        if (x, y) in self.ramb_tiles: return self.ramb_tiles[(x, y)]
        if (x, y) in self.ramt_tiles: return self.ramt_tiles[(x, y)]
        for i in range(4):
            if (x, y) in self.dsp_tiles[i]: return self.dsp_tiles[i][(x, y)]
        if (x, y) in self.ipcon_tiles: return self.ipcon_tiles[(x, y)]            
        return None

    def pinloc_db(self, package = None):
        if package is None:
            if self.device == "384": return pinloc_db["384-qn32"]
            if self.device == "1k": return pinloc_db["1k-tq144"]
            if self.device == "lm4k": return pinloc_db["lm4k-cm49"]
            if self.device == "u4k": return pinloc_db["u4k-sg48"]
            if self.device == "5k": return pinloc_db["5k-sg48"]
            if self.device == "8k": return pinloc_db["8k-ct256"]
        else:
            return pinloc_db[self.device + "-" + package]
        assert False

    def gbufin_db(self):
        return gbufin_db[self.device]

    def iolatch_db(self):
        return iolatch_db[self.device]

    def padin_pio_db(self):
        return padin_pio_db[self.device]

    def extra_bits_db(self):
        return extra_bits_db[self.device]

    def ieren_db(self):
        return ieren_db[self.device]

    def pll_list(self):
        if self.device == "1k":
            return ["1k"]
        if self.device == "lm4k":
            return ["lm4k"]
        if self.device == "u4k":
            return ["u4k"]
        if self.device == "5k":
            return ["5k"]
        if self.device == "8k":
            return ["8k_0", "8k_1"]
        if self.device == "384":
            return [ ]
        assert False

    # Return true if device is Ultra/UltraPlus series, i.e. has
    # IpConnect/DSP at the sides instead of IO
    def is_ultra(self):
        return self.device in ["5k", "u4k"]

    def colbuf_db(self):
        if self.device == "1k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  4: src_y =  4
                    if  5 <= y <=  8: src_y =  5
                    if  9 <= y <= 12: src_y = 12
                    if 13 <= y <= 17: src_y = 13
                    if x in [3, 10] and src_y ==  4: src_y =  3
                    if x in [3, 10] and src_y == 12: src_y = 11
                    entries.append((x, src_y, x, y))
            return entries

        # TODO(awygle) - actually capture 0 and 21 here
        if self.device == "lm4k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  4: src_y =  4
                    if  5 <= y <= 10: src_y =  5
                    if 11 <= y <= 16: src_y = 16
                    if 17 <= y <= 21: src_y = 17
                    entries.append((x, src_y, x, y))
            return entries

        if self.device == "u4k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  4: src_y =  4
                    if  5 <= y <= 10: src_y =  5
                    if 11 <= y <= 16: src_y = 16
                    if 17 <= y <= 21: src_y = 17
                    entries.append((x, src_y, x, y))
            return entries

        if self.device == "8k":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  8: src_y =  8
                    if  9 <= y <= 16: src_y =  9
                    if 17 <= y <= 24: src_y = 24
                    if 25 <= y <= 33: src_y = 25
                    entries.append((x, src_y, x, y))
            return entries

        if self.device == "5k": #Interesting, seems the 5k has more colbufs?
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None
                    if  0 <= y <=  4: src_y =  4
                    if  5 <= y <= 10: src_y =  5
                    if 11 <= y <= 14: src_y = 14
                    if 15 <= y <= 20: src_y = 15
                    if 21 <= y <= 26: src_y = 26
                    if 27 <= y <= 31: src_y = 27
                    entries.append((x, src_y, x, y))
            return entries

        if self.device == "384":
            entries = list()
            for x in range(self.max_x+1):
                for y in range(self.max_y+1):
                    src_y = None                 #Is ColBufCtrl relevant?
                    if  0 <= y <=  2: src_y =  2 #384?
                    if  3 <= y <=  4: src_y =  3 #384?
                    if  5 <= y <=  6: src_y =  6 #384?
                    if  7 <= y <=  9: src_y =  7 #384?
                    entries.append((x, src_y, x, y))
            return entries

        assert False
        
    # Return a map between HDL name and routing net and location for a given DSP cell    
    def get_dsp_nets_db(self, x, y):
        assert ((x, y) in self.dsp_tiles[0])
        # Control signals
        nets = {
            "CLK":          (x, y+2, "lutff_global/clk"),
            "CE":           (x, y+2, "lutff_global/cen"),
            "IRSTTOP":      (x, y+1, "lutff_global/s_r"),
            "IRSTBOT":      (x, y+0, "lutff_global/s_r"),
            "ORSTTOP":      (x, y+3, "lutff_global/s_r"),
            "ORSTBOT":      (x, y+2, "lutff_global/s_r"),
            "AHOLD":        (x, y+2, "lutff_0/in_0"),
            "BHOLD":        (x, y+1, "lutff_0/in_0"),
            "CHOLD":        (x, y+3, "lutff_0/in_0"),
            "DHOLD":        (x, y+0, "lutff_0/in_0"),
            "OHOLDTOP":     (x, y+3, "lutff_1/in_0"),
            "OHOLDBOT":     (x, y+0, "lutff_1/in_0"),
            "ADDSUBTOP":    (x, y+3, "lutff_3/in_0"),
            "ADDSUBBOT":    (x, y+0, "lutff_3/in_0"),
            "OLOADTOP":     (x, y+3, "lutff_2/in_0"),
            "OLOADBOT":    (x, y+0, "lutff_2/in_0"),
            "CI":           (x, y+0, "lutff_4/in_0"),
            "CO":           (x, y+4, "slf_op_0")
        }
        #Data ports
        for i in range(8):
            nets["C_%d" % i]        = (x, y+3, "lutff_%d/in_3" % i)
            nets["C_%d" % (i+8)]    = (x, y+3, "lutff_%d/in_1" % i)
            
            nets["A_%d" % i]        = (x, y+2, "lutff_%d/in_3" % i)
            nets["A_%d" % (i+8)]    = (x, y+2, "lutff_%d/in_1" % i)

            nets["B_%d" % i]        = (x, y+1, "lutff_%d/in_3" % i)
            nets["B_%d" % (i+8)]    = (x, y+1, "lutff_%d/in_1" % i)

            nets["D_%d" % i]        = (x, y+0, "lutff_%d/in_3" % i)
            nets["D_%d" % (i+8)]    = (x, y+0, "lutff_%d/in_1" % i)
        for i in range(32):
            nets["O_%d" % i]        = (x, y+(i//8), "mult/O_%d" % i)
        return nets
    
    # Return the location of configuration bits for a given DSP cell
    def get_dsp_config_db(self, x, y):
        assert ((x, y) in self.dsp_tiles[0])
         
        override = { }
        if (("%s_%d_%d" % (self.device, x, y)) in dsp_config_db):
             override = dsp_config_db["%s_%d_%d" % (self.device, x, y)]
        default_db = dsp_config_db["default"]
        merged = { }
        for cfgkey in default_db:
            cx, cy, cbit = default_db[cfgkey]
            if cfgkey in override:
                cx, cy, cbit = override[cfgkey]
            merged[cfgkey] = (x + cx, y + cy, cbit)
        return merged
    
    def tile_db(self, x, y):
        # Only these devices have IO on the left and right sides.
        if self.device in ["384", "1k", "lm4k", "8k"]:
          if x == 0: return iotile_l_db
          if x == self.max_x: return iotile_r_db
        # The 5k needs an IO db including the extra bits
        if self.device == "5k" or self.device == "u4k":
            if y == 0: return iotile_b_5k_db
            if y == self.max_y: return iotile_t_5k_db
        else:
            if y == 0: return iotile_b_db
            if y == self.max_y: return iotile_t_db
        if self.device == "1k":
            if (x, y) in self.logic_tiles: return logictile_db
            if (x, y) in self.ramb_tiles: return rambtile_db
            if (x, y) in self.ramt_tiles: return ramttile_db
        elif self.device == "5k" or self.device == "u4k":
            if (x, y) in self.logic_tiles: return logictile_5k_db
            if (x, y) in self.ramb_tiles: return rambtile_8k_db
            if (x, y) in self.ramt_tiles: return ramttile_8k_db
            if (x, y) in self.ipcon_tiles: return ipcon_5k_db
            if (x, y) in self.dsp_tiles[0]: return dsp0_5k_db
            if (x, y) in self.dsp_tiles[1]: return dsp1_5k_db
            if (x, y) in self.dsp_tiles[2]: return dsp2_5k_db
            if (x, y) in self.dsp_tiles[3]: return dsp3_5k_db

        elif self.device == "8k" or self.device == "lm4k":
            if (x, y) in self.logic_tiles: return logictile_8k_db
            if (x, y) in self.ramb_tiles: return rambtile_8k_db
            if (x, y) in self.ramt_tiles: return ramttile_8k_db
        elif self.device == "384":
            if (x, y) in self.logic_tiles: return logictile_384_db

        print("Tile type unknown at (%d, %d)" % (x, y))
        assert False

    def tile_type(self, x, y):
        if x == 0 and (not self.is_ultra()): return "IO"
        if y == 0: return "IO"
        if x == self.max_x and (not self.is_ultra()): return "IO"
        if y == self.max_y: return "IO"
        if (x, y) in self.ramb_tiles: return "RAMB"
        if (x, y) in self.ramt_tiles: return "RAMT"
        if (x, y) in self.logic_tiles: return "LOGIC"
        if (x == 0 or x == self.max_x) and self.is_ultra():
            if (x, y) in self.dsp_tiles[0]: return "DSP0"
            elif (x, y) in self.dsp_tiles[1]: return "DSP1"
            elif (x, y) in self.dsp_tiles[2]: return "DSP2"
            elif (x, y) in self.dsp_tiles[3]: return "DSP3"
            else: return "IPCON"
        assert False

    def tile_pos(self, x, y):
        if x == 0 and 0 < y < self.max_y: return "l"
        if y == 0 and 0 < x < self.max_x: return "b"
        if x == self.max_x and 0 < y < self.max_y: return "r"
        if y == self.max_y and 0 < x < self.max_x: return "t"
        if 0 < x < self.max_x and 0 < y < self.max_y: return "x"
        return None

    def tile_has_entry(self, x, y, entry):
        if entry[1] in ("routing", "buffer"):
            return self.tile_has_net(x, y, entry[2]) and self.tile_has_net(x, y, entry[3])
        return True

    @functools.lru_cache(maxsize=2**16)
    def tile_has_net(self, x, y, netname):
        if netname.startswith("logic_op_"):
            if netname.startswith("logic_op_bot_"):
                if y == self.max_y and 0 < x < self.max_x: return True
            if netname.startswith("logic_op_bnl_"):
                if x == self.max_x and 1 < y < self.max_y and (not self.is_ultra()): return True
                if y == self.max_y and 1 < x < self.max_x: return True
            if netname.startswith("logic_op_bnr_"):
                if x == 0 and 1 < y < self.max_y and (not self.is_ultra()): return True
                if y == self.max_y and 0 < x < self.max_x-1: return True

            if netname.startswith("logic_op_top_"):
                if y == 0 and 0 < x < self.max_x: return True
            if netname.startswith("logic_op_tnl_"):
                if x == self.max_x and 0 < y < self.max_y-1 and (not self.is_ultra()): return True
                if y == 0 and 1 < x < self.max_x: return True
            if netname.startswith("logic_op_tnr_"):
                if x == 0 and 0 < y < self.max_y-1 and (not self.is_ultra()): return True
                if y == 0 and 0 < x < self.max_x-1: return True

            if netname.startswith("logic_op_lft_"):
                if x == self.max_x and (not self.is_ultra()): return True
            if netname.startswith("logic_op_rgt_"):
                if x == 0 and (not self.is_ultra()): return True

            return False

        if not 0 <= x <= self.max_x: return False
        if not 0 <= y <= self.max_y: return False
        return pos_has_net(self.tile_pos(x, y), netname)

    def tile_follow_net(self, x, y, direction, netname):
        if x == 1 and y not in (0, self.max_y) and direction == 'l': return pos_follow_net("x", "L", netname, self.is_ultra())
        if y == 1 and x not in (0, self.max_x) and direction == 'b': return pos_follow_net("x", "B", netname, self.is_ultra())
        if x == self.max_x-1 and y not in (0, self.max_y) and direction == 'r': return pos_follow_net("x", "R", netname, self.is_ultra())
        if y == self.max_y-1 and x not in (0, self.max_x) and direction == 't': return pos_follow_net("x", "T", netname, self.is_ultra())
        if self.is_ultra(): # Pass through corner positions as they must be handled differently
            if y == 1 and x in (0, self.max_x) and direction == 'b': return pos_follow_net(self.tile_pos(x, y), "B", netname, self.is_ultra())
            if y == self.max_y-1 and x in (0, self.max_x) and direction == 't': return pos_follow_net(self.tile_pos(x, y), "T", netname, self.is_ultra())
            if x == 1 and y in (0, self.max_y) and direction == 'l': return pos_follow_net(self.tile_pos(x, y), "L", netname, self.is_ultra())
            if x == self.max_x-1 and y in (0, self.max_y) and direction == 'r': return pos_follow_net(self.tile_pos(x, y), "R", netname, self.is_ultra())

        return pos_follow_net(self.tile_pos(x, y), direction, netname, self.is_ultra())

    def follow_funcnet(self, x, y, func):
        neighbours = set()
        def do_direction(name, nx, ny):
            if (0 < nx < self.max_x or self.is_ultra()) and 0 < ny < self.max_y:
                neighbours.add((nx, ny, "neigh_op_%s_%d" % (name, func)))
            if nx in (0, self.max_x) and 0 < ny < self.max_y and nx != x and (not self.is_ultra()):
                neighbours.add((nx, ny, "logic_op_%s_%d" % (name, func)))
            if ny in (0, self.max_y) and 0 < nx < self.max_x and ny != y:
                neighbours.add((nx, ny, "logic_op_%s_%d" % (name, func)))
        do_direction("bot", x,   y+1)
        do_direction("bnl", x+1, y+1)
        do_direction("bnr", x-1, y+1)
        do_direction("top", x,   y-1)
        do_direction("tnl", x+1, y-1)
        do_direction("tnr", x-1, y-1)
        do_direction("lft", x+1, y  )
        do_direction("rgt", x-1, y  )
        return neighbours

    def lookup_funcnet(self, nx, ny, x, y, func):
        npos = self.tile_pos(nx, ny)
        pos = self.tile_pos(x, y)

        if npos is not None and pos is not None:
            if npos == "x":
                if (nx, ny) in self.logic_tiles:
                    return (nx, ny, "lutff_%d/out" % func)
                for i in range(4):
                    if (nx, ny) in self.dsp_tiles[i]: #TODO: check this
                        return (nx, ny, "mult/O_%d" % (i * 8 + func))
                if (nx, ny) in self.ramb_tiles:
                    if self.device == "1k":
                        return (nx, ny, "ram/RDATA_%d" % func)
                    elif self.device == "5k" or self.device == "u4k":
                        return (nx, ny, "ram/RDATA_%d" % (15-func))
                    elif self.device == "8k" or self.device == "lm4k":
                        return (nx, ny, "ram/RDATA_%d" % (15-func))
                    else:
                        assert False
                if (nx, ny) in self.ramt_tiles:
                    if self.device == "1k":
                        return (nx, ny, "ram/RDATA_%d" % (8+func))
                    elif self.device == "5k" or self.device == "u4k":
                        return (nx, ny, "ram/RDATA_%d" % (7-func))
                    elif self.device == "8k" or self.device == "lm4k":
                        return (nx, ny, "ram/RDATA_%d" % (7-func))
                    else:
                        assert False

            elif pos == "x" and ((npos in ("t", "b")) or ((not self.is_ultra()) and (npos in ("l", "r")))):
                if func in (0, 4): return (nx, ny, "io_0/D_IN_0")
                if func in (1, 5): return (nx, ny, "io_0/D_IN_1")
                if func in (2, 6): return (nx, ny, "io_1/D_IN_0")
                if func in (3, 7): return (nx, ny, "io_1/D_IN_1")

        return None

    def rlookup_funcnet(self, x, y, netname):
        funcnets = set()

        if netname == "io_0/D_IN_0":
            for net in self.follow_funcnet(x, y, 0) | self.follow_funcnet(x, y, 4):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_0/D_IN_1":
            for net in self.follow_funcnet(x, y, 1) | self.follow_funcnet(x, y, 5):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_1/D_IN_0":
            for net in self.follow_funcnet(x, y, 2) | self.follow_funcnet(x, y, 6):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        if netname == "io_1/D_IN_1":
            for net in self.follow_funcnet(x, y, 3) | self.follow_funcnet(x, y, 7):
                if self.tile_pos(net[0], net[1]) == "x": funcnets.add(net)

        match = re_match_cached(r"lutff_(\d+)/out", netname)
        if match:
            funcnets |= self.follow_funcnet(x, y, int(match.group(1)))

        match = re_match_cached(r"ram/RDATA_(\d+)", netname)
        if match:
            if self.device == "1k":
                funcnets |= self.follow_funcnet(x, y, int(match.group(1)) % 8)
            elif self.device == "5k" or self.device == "u4k":
                funcnets |= self.follow_funcnet(x, y, 7 - int(match.group(1)) % 8)
            elif self.device == "8k" or self.device == "lm4k":
                funcnets |= self.follow_funcnet(x, y, 7 - int(match.group(1)) % 8)
            else:
                assert False

        return funcnets
    
    def ultraplus_follow_corner(self, corner, direction, netname):
        m = re_match_cached(r"span4_(horz|vert)_([lrtb])_(\d+)$", netname)
        if not m:
            return None
        cur_edge = m.group(2)
        cur_index = int(m.group(3))
        if direction not in corner:
            return None
        if direction != cur_edge:
            return None
        h_idx, v_idx = self.ultraplus_trace_corner_idx(corner, cur_index)
        if h_idx is None and (direction == "b" or direction == "t"):
            return None
        if v_idx is None and (direction == "l" or direction == "r"):
            return None
        if corner == "bl" and direction == "l":
            return (0, 1, sp4v_normalize("sp4_v_b_%d" % v_idx))
        if corner == "bl" and direction == "b":
            return (1, 0, ultra_span4_horz_normalize("span4_horz_l_%d" % h_idx))
        if corner == "br" and direction == "r":
            return (self.max_x, 1, sp4v_normalize("sp4_v_b_%d" % v_idx))
        if corner == "br" and direction == "b":
            return (self.max_x-1, 0, ultra_span4_horz_normalize("span4_horz_r_%d" % h_idx))
        if corner == "tl" and direction == "l":
            return (0, self.max_y-1, sp4v_normalize("sp4_v_t_%d" % v_idx))
        if corner == "tl" and direction == "t":
            return (1, self.max_y, ultra_span4_horz_normalize("span4_horz_l_%d" % h_idx))
        if corner == "tr" and direction == "r":
            return (self.max_x, self.max_y-1, sp4v_normalize("sp4_v_t_%d" % v_idx))
        if corner == "tr" and direction == "t":
            return (self.max_x-1, self.max_y, ultra_span4_horz_normalize("span4_horz_r_%d" % h_idx))
        assert False
    #UltraPlus corner routing: given the corner name and net index,
    #return a tuple containing H and V indexes, or none if NA
    def ultraplus_trace_corner_idx(self, corner, idx):
        h_idx = None
        v_idx = None
        if corner == "bl" or corner == "br":
            if idx < 16:
                v_idx = idx + 32
            if idx >= 32 and idx < 48:
                h_idx = idx - 32
        elif corner == "tl" or corner == "tr":
            if idx >= 0 and idx < 16:
                v_idx = idx
                h_idx = idx
        return (h_idx, v_idx)
    
    def get_corner(self, x, y):
        corner = ""
        if y == 0:
            corner += "b"
        elif y == self.max_y:
            corner += "t"
        else:
            corner += "x"
        if x == 0:
            corner += "l"
        elif x == self.max_x:
            corner += "r"
        else:
            corner += "x"
        return corner
    
    def follow_net(self, netspec):
        x, y, netname = netspec
        neighbours = self.rlookup_funcnet(x, y, netname)

        #print(netspec)
        #print('\t', neighbours)

        if netname == "carry_in" and y > 1:
            neighbours.add((x, y-1, "lutff_7/cout"))

        if netname == "lutff_7/cout" and y+1 < self.max_y:
            neighbours.add((x, y+1, "carry_in"))

        if netname.startswith("glb_netwk_"):
            for nx in range(self.max_x+1):
                for ny in range(self.max_y+1):
                    if self.tile_pos(nx, ny) is not None:
                        neighbours.add((nx, ny, netname))

        match = re_match_cached(r"sp4_r_v_b_(\d+)", netname)
        if match and ((0 < x < self.max_x-1) or (self.is_ultra() and (x < self.max_x))):
            neighbours.add((x+1, y, sp4v_normalize("sp4_v_b_" + match.group(1))))
        #print('\tafter r_v_b', neighbours)

        match = re_match_cached(r"sp4_v_[bt]_(\d+)", netname)
        if match and (1 < x < self.max_x or (self.is_ultra() and (x > 0))):
            n = sp4v_normalize(netname, "b")
            if n is not None:
                n = n.replace("sp4_", "sp4_r_")
                neighbours.add((x-1, y, n))
        #print('\tafter v_[bt]', neighbours)

        match = re_match_cached(r"(logic|neigh)_op_(...)_(\d+)", netname)
        if match:
            if match.group(2) == "bot": nx, ny = (x,   y-1)
            if match.group(2) == "bnl": nx, ny = (x-1, y-1)
            if match.group(2) == "bnr": nx, ny = (x+1, y-1)
            if match.group(2) == "top": nx, ny = (x,   y+1)
            if match.group(2) == "tnl": nx, ny = (x-1, y+1)
            if match.group(2) == "tnr": nx, ny = (x+1, y+1)
            if match.group(2) == "lft": nx, ny = (x-1, y  )
            if match.group(2) == "rgt": nx, ny = (x+1, y  )
            n = self.lookup_funcnet(nx, ny, x, y, int(match.group(3)))
            if n is not None:
                neighbours.add(n)

        for direction in ["l", "r", "t", "b"]:
            n = self.tile_follow_net(x, y, direction, netname)
            if n is not None:
                if direction == "l": s = (x-1, y, n)
                if direction == "r": s = (x+1, y, n)
                if direction == "t": s = (x, y+1, n)
                if direction == "b": s = (x, y-1, n)

                if s[0] in (0, self.max_x) and s[1] in (0, self.max_y):
                    if self.is_ultra():
                        s = self.ultraplus_follow_corner(self.get_corner(s[0], s[1]), direction, n)
                        if s is None:
                            continue
                    elif re_match_cached(r"span4_(vert|horz)_[lrtb]_\d+$", n) and not self.is_ultra():
                        m = re_match_cached(r"span4_(vert|horz)_([lrtb])_\d+$", n)

                        vert_net = n.replace("_l_", "_t_").replace("_r_", "_b_").replace("_horz_", "_vert_")
                        horz_net = n.replace("_t_", "_l_").replace("_b_", "_r_").replace("_vert_", "_horz_")
                                    
                        if s[0] == 0 and s[1] == 0:
                            if direction == "l": s = (0, 1, vert_net)
                            if direction == "b": s = (1, 0, horz_net)

                        if s[0] == self.max_x and s[1] == self.max_y:
                            if direction == "r": s = (self.max_x, self.max_y-1, vert_net)
                            if direction == "t": s = (self.max_x-1, self.max_y, horz_net)

                        vert_net = netname.replace("_l_", "_t_").replace("_r_", "_b_").replace("_horz_", "_vert_")
                        horz_net = netname.replace("_t_", "_l_").replace("_b_", "_r_").replace("_vert_", "_horz_")
                            
                        if s[0] == 0 and s[1] == self.max_y:
                            if direction == "l": s = (0, self.max_y-1, vert_net)
                            if direction == "t": s = (1, self.max_y, horz_net)

                        if s[0] == self.max_x and s[1] == 0:
                            if direction == "r": s = (self.max_x, 1, vert_net)
                            if direction == "b": s = (self.max_x-1, 0, horz_net)

                if self.tile_has_net(s[0], s[1], s[2]):
                    neighbours.add((s[0], s[1], s[2]))

        #print('\tafter directions', neighbours)
        return neighbours

    def get_net_number(self, segment):
        if not hasattr(self, 'net_map') or self.net_map is None:
            self.net_map = {}
            for netidx, group in enumerate(sorted(self.all_group_segments())):
                for seg in group:
                    self.net_map[seg] = netidx

        return self.net_map[segment]

    def all_group_segments(self):
        if not hasattr(self, 'all_groups') or self.all_groups is None:
            all_tiles = set()
            for x in range(self.max_x + 1):
                for y in range(self.max_y + 1):
                    if self.tile(x, y) is not None:
                        all_tiles.add((x, y))

            self.all_groups = self.group_segments(all_tiles, connect_gb=False)
        return self.all_groups

    def group_segments(self, all_from_tiles=set(), extra_connections=list(), extra_segments=list(), connect_gb=True):
        seed_segments = set()
        seen_segments = set()
        connected_segments = dict()
        grouped_segments = set()

        for seg in extra_segments:
            seed_segments.add(seg)

        for conn in extra_connections:
            s1, s2 = conn
            connected_segments.setdefault(s1, set()).add(s2)
            connected_segments.setdefault(s2, set()).add(s1)
            seed_segments.add(s1)
            seed_segments.add(s2)

        for idx, tile in self.io_tiles.items():
            tc = tileconfig(tile)
            pintypes = [ list("000000"), list("000000") ]
            for entry in self.tile_db(idx[0], idx[1]):
                if entry[1].startswith("IOB_") and entry[2].startswith("PINTYPE_") and tc.match(entry[0]):
                    pintypes[int(entry[1][-1])][int(entry[2][-1])] = "1"
            if "".join(pintypes[0][2:6]) != "0000":
                seed_segments.add((idx[0], idx[1], "io_0/D_OUT_0"))
            if "".join(pintypes[1][2:6]) != "0000":
                seed_segments.add((idx[0], idx[1], "io_1/D_OUT_0"))

        def add_seed_segments(idx, tile, db):
            tc = tileconfig(tile)
            for entry in db:
                if entry[1] in ("routing", "buffer"):
                    config_match = tc.match(entry[0])
                    if idx in all_from_tiles or config_match:
                        if not self.tile_has_net(idx[0], idx[1], entry[2]): continue
                        if not self.tile_has_net(idx[0], idx[1], entry[3]): continue
                        s1 = (idx[0], idx[1], entry[2])
                        s2 = (idx[0], idx[1], entry[3])
                        if config_match:
                            connected_segments.setdefault(s1, set()).add(s2)
                            connected_segments.setdefault(s2, set()).add(s1)
                        seed_segments.add(s1)
                        seed_segments.add(s2)

        for idx, tile in self.io_tiles.items():
            add_seed_segments(idx, tile, self.tile_db(idx[0], idx[1]))

        for idx, tile in self.logic_tiles.items():
            if idx in all_from_tiles:
                seed_segments.add((idx[0], idx[1], "lutff_7/cout"))
            if self.device == "1k":
                add_seed_segments(idx, tile, logictile_db)
            elif self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, logictile_5k_db)
            elif self.device == "8k" or self.device == "lm4k":
                add_seed_segments(idx, tile, logictile_8k_db)
            elif self.device == "384":
                add_seed_segments(idx, tile, logictile_384_db)
            else:
                assert False

        for idx, tile in self.ramb_tiles.items():
            if self.device == "1k":
                add_seed_segments(idx, tile, rambtile_db)
            elif self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, rambtile_8k_db)
            elif self.device == "8k" or self.device == "lm4k":
                add_seed_segments(idx, tile, rambtile_8k_db)
            else:
                assert False

        for idx, tile in self.ramt_tiles.items():
            if self.device == "1k":
                add_seed_segments(idx, tile, ramttile_db)
            elif self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, ramttile_8k_db)
            elif self.device == "8k" or self.device == "lm4k":
                add_seed_segments(idx, tile, ramttile_8k_db)
            else:
                assert False

        for idx, tile in self.dsp_tiles[0].items():
            if self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, dsp0_5k_db)
        for idx, tile in self.dsp_tiles[1].items():
            if self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, dsp1_5k_db)
        for idx, tile in self.dsp_tiles[2].items():
            if self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, dsp2_5k_db)
        for idx, tile in self.dsp_tiles[3].items():
            if self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, dsp3_5k_db)
        for idx, tile in self.ipcon_tiles.items():
            if self.device == "5k" or self.device == "u4k":
                add_seed_segments(idx, tile, ipcon_5k_db)
        for padin, pio in enumerate(self.padin_pio_db()):
            s1 = (pio[0], pio[1], "padin_%d" % pio[2])
            s2 = (pio[0], pio[1], "glb_netwk_%d" % padin)
            if s1 in seed_segments or (pio[0], pio[1]) in all_from_tiles:
                connected_segments.setdefault(s1, set()).add(s2)
                connected_segments.setdefault(s2, set()).add(s1)
                seed_segments.add(s1)
                seed_segments.add(s2)

        for entry in self.iolatch_db():
            if entry[0] == 0 or entry[0] == self.max_x:
                iocells = [(entry[0], i) for i in range(1, self.max_y)]
            if entry[1] == 0 or entry[1] == self.max_y:
                iocells = [(i, entry[1]) for i in range(1, self.max_x)]
            for cell in iocells:
                s1 = (entry[0], entry[1], "fabout")
                s2 = (cell[0], cell[1], "io_global/latch")
                if s1 in seed_segments or s2 in seed_segments or \
                        (entry[0], entry[1]) in all_from_tiles or (cell[0], cell[1]) in all_from_tiles:
                    connected_segments.setdefault(s1, set()).add(s2)
                    connected_segments.setdefault(s2, set()).add(s1)
                    seed_segments.add(s1)
                    seed_segments.add(s2)

        if connect_gb:
            for entry in self.gbufin_db():
                s1 = (entry[0], entry[1], "fabout")
                s2 = (entry[0], entry[1], "glb_netwk_%d" % entry[2])
                if s1 in seed_segments or (pio[0], pio[1]) in all_from_tiles:
                    connected_segments.setdefault(s1, set()).add(s2)
                    connected_segments.setdefault(s2, set()).add(s1)
                    seed_segments.add(s1)
                    seed_segments.add(s2)

        while seed_segments:
            queue = set()
            segments = set()
            queue.add(seed_segments.pop())
            while queue:
                next_segment = queue.pop()
                expanded = self.expand_net(next_segment)
                for s in expanded:
                    if s not in segments:
                        segments.add(s)
                        if s in seen_segments:
                          print("//", s, "has already been seen. Check your bitmapping.")
                          assert False
                        seen_segments.add(s)
                        seed_segments.discard(s)
                        if s in connected_segments:
                            for cs in connected_segments[s]:
                                if not cs in segments:
                                    queue.add(cs)
            for s in segments:
                assert s not in seed_segments
            grouped_segments.add(tuple(sorted(segments)))

        return grouped_segments

    def expand_net(self, netspec):
        queue = set()
        segments = set()
        queue.add(netspec)
        while queue:
            n = queue.pop()
            segments.add(n)
            for k in self.follow_net(n):
                if k not in segments:
                    queue.add(k)
        return segments

    def read_file(self, filename):
        self.clear()
        current_data = None
        expected_data_lines = 0
        with open(filename, "r") as f:
            for linenum, linetext in enumerate(f):
                # print("DEBUG: input line %d: %s" % (linenum, linetext.strip()))
                line = linetext.strip().split()
                if len(line) == 0:
                    assert expected_data_lines == 0
                    continue
                if line[0][0] != ".":
                    if expected_data_lines == -1:
                        continue
                    if line[0][0] not in "0123456789abcdef":
                        print("Warning: ignoring data block in line %d: %s" % (linenum, linetext.strip()))
                        expected_data_lines = 0
                        continue
                    assert expected_data_lines != 0
                    current_data.append(line[0])
                    expected_data_lines -= 1
                    continue
                assert expected_data_lines <= 0
                if line[0] in (".io_tile", ".logic_tile", ".ramb_tile", ".ramt_tile", ".ram_data", ".ipcon_tile", ".dsp0_tile", ".dsp1_tile", ".dsp2_tile", ".dsp3_tile"):
                    current_data = list()
                    expected_data_lines = 16
                    self.max_x = max(self.max_x, int(line[1]))
                    self.max_y = max(self.max_y, int(line[2]))
                if line[0] == ".io_tile":
                    self.io_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".logic_tile":
                    self.logic_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ramb_tile":
                    self.ramb_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ramt_tile":
                    self.ramt_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ipcon_tile":
                    self.ipcon_tiles[(int(line[1]), int(line[2]))] = current_data
                    continue
                match = re_match_cached(r".dsp(\d)_tile", line[0])
                if match:
                    self.dsp_tiles[int(match.group(1))][(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".ram_data":
                    self.ram_data[(int(line[1]), int(line[2]))] = current_data
                    continue
                if line[0] == ".extra_bit":
                    self.extra_bits.add((int(line[1]), int(line[2]), int(line[3])))
                    continue
                if line[0] == ".device":
                    assert line[1] in ["1k", "lm4k", "u4k", "5k", "8k", "384"]
                    self.device = line[1]
                    continue
                if line[0] == ".warmboot":
                    assert line[1] in ["disabled", "enabled"]
                    self.warmboot = line[1] == "enabled"
                    continue
                if line[0] == ".sym":
                    self.symbols.setdefault(int(line[1]), set()).add(line[2])
                    continue
                if line[0] == ".comment":
                    expected_data_lines = -1
                    continue
                print("Warning: ignoring line %d: %s" % (linenum, linetext.strip()))
                expected_data_lines = -1

    def write_file(self, filename):
        with open(filename, "w") as f:
            print(".device %s" % self.device, file=f)
            if not self.warmboot:
                print(".warmboot disabled", file=f)
            for y in range(self.max_y+1):
                for x in range(self.max_x+1):
                    if self.tile_pos(x, y) is not None:
                        print(".%s_tile %d %d" % (self.tile_type(x, y).lower(), x, y), file=f)
                        for line in self.tile(x, y):
                            print(line, file=f)
            for x, y in sorted(self.ram_data):
                print(".ram_data %d %d" % (x, y), file=f)
                for line in self.ram_data[(x, y)]:
                    print(line, file=f)
            for extra_bit in sorted(self.extra_bits):
                print(".extra_bit %d %d %d" % extra_bit, file=f)
            for net in sorted(self.symbols.keys()):
                for sym_key in self.symbols[net]:
                    print(".sym %s %s" % (net, sym_key), file=f)
class tileconfig:
    def __init__(self, tile):
        self.bits = set()
        for k, line in enumerate(tile):
            for i in range(len(line)):
                if line[i] == "1":
                    self.bits.add("B%d[%d]" % (k, i))
                else:
                    self.bits.add("!B%d[%d]" % (k, i))
    def match(self, pattern):
        for bit in pattern:
            if not bit in self.bits:
                return False
        return True

if False:
    ## Lattice span net name normalization

    valid_sp4_h_l = set([1, 2, 4, 5, 7, 9, 10, 11, 15, 16, 17, 21, 24, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47])
    valid_sp4_h_r = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 19, 21, 24, 25, 27, 30, 31, 33, 34, 35, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46])

    valid_sp4_v_t = set([1, 3, 5, 9, 12, 14, 16, 17, 18, 21, 22, 23, 26, 28, 29, 30, 32, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47])
    valid_sp4_v_b = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 18, 19, 21, 22, 23, 24, 26, 30, 33, 36, 37, 38, 42, 46, 47])

    valid_sp12_h_l = set([3, 4, 5, 12, 14, 16, 17, 18, 21, 22, 23])
    valid_sp12_h_r = set([0, 1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 16, 20, 23])

    valid_sp12_v_t = set([0, 1, 2, 3, 6, 9, 10, 12, 14, 21, 22, 23])
    valid_sp12_v_b = set([0, 1, 6, 7, 8, 11, 12, 14, 16, 18, 19, 20, 21, 23])

else:
    ## IceStorm span net name normalization

    valid_sp4_h_l = set(range(36, 48))
    valid_sp4_h_r = set(range(48))

    valid_sp4_v_t = set(range(36, 48))
    valid_sp4_v_b = set(range(48))

    valid_sp12_h_l = set(range(22, 24))
    valid_sp12_h_r = set(range(24))

    valid_sp12_v_t = set(range(22, 24))
    valid_sp12_v_b = set(range(24))

def sp4h_normalize(netname, edge=""):
    m = re_match_cached(r"sp4_h_([lr])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "r" and (edge == "l" or (edge == "" and cur_index not in valid_sp4_h_r)):
        if cur_index < 12:
            return None
        return "sp4_h_l_%d" % ((cur_index-12)^1)

    if cur_edge == "l" and (edge == "r" or (edge == "" and cur_index not in valid_sp4_h_l)):
        if cur_index >= 36:
            return None
        return "sp4_h_r_%d" % ((cur_index+12)^1)

    return netname
# "Normalization" of span4 (not just sp4) is needed during Ultra/UltraPlus
# corner tracing
def ultra_span4_horz_normalize(netname, edge=""):
    m = re_match_cached(r"span4_horz_([rl])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))
    if cur_edge == edge:
        return netname
    if edge == "":
        if cur_edge == "l" and cur_index < 12:
            return "span4_horz_r_%d" % (cur_index + 4)
        else:
            return netname
    elif edge == "l" and cur_edge == "r":
        if cur_index < 4:
            return None
        else:
            cur_index -= 4
        return "span4_horz_l_%d" % cur_index
    elif edge == "r" and cur_edge == "l":
        if cur_index < 12:
            return "span4_horz_r_%d" % (cur_index + 4)
        else:
            return None
    assert False
    
def sp4v_normalize(netname, edge=""):
    m = re_match_cached(r"sp4_v_([bt])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "b" and (edge == "t" or (edge == "" and cur_index not in valid_sp4_v_b)):
        if cur_index < 12:
            return None
        return "sp4_v_t_%d" % ((cur_index-12)^1)

    if cur_edge == "t" and (edge == "b" or (edge == "" and cur_index not in valid_sp4_v_t)):
        if cur_index >= 36:
            return None
        return "sp4_v_b_%d" % ((cur_index+12)^1)

    return netname

def sp12h_normalize(netname, edge=""):
    m = re_match_cached(r"sp12_h_([lr])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "r" and (edge == "l" or (edge == "" and cur_index not in valid_sp12_h_r)):
        if cur_index < 2:
            return None
        return "sp12_h_l_%d" % ((cur_index-2)^1)

    if cur_edge == "l" and (edge == "r" or (edge == "" and cur_index not in valid_sp12_h_l)):
        if cur_index >= 22:
            return None
        return "sp12_h_r_%d" % ((cur_index+2)^1)

    return netname

def sp12v_normalize(netname, edge=""):
    m = re_match_cached(r"sp12_v_([bt])_(\d+)$", netname)
    assert m
    if not m: return None
    cur_edge = m.group(1)
    cur_index = int(m.group(2))

    if cur_edge == edge:
        return netname

    if cur_edge == "b" and (edge == "t" or (edge == "" and cur_index not in valid_sp12_v_b)):
        if cur_index < 2:
            return None
        return "sp12_v_t_%d" % ((cur_index-2)^1)

    if cur_edge == "t" and (edge == "b" or (edge == "" and cur_index not in valid_sp12_v_t)):
        if cur_index >= 22:
            return None
        return "sp12_v_b_%d" % ((cur_index+2)^1)

    return netname

def netname_normalize(netname, edge="", ramb=False, ramt=False, ramb_8k=False, ramt_8k=False):
    if netname.startswith("sp4_v_"): return sp4v_normalize(netname, edge)
    if netname.startswith("sp4_h_"): return sp4h_normalize(netname, edge)
    if netname.startswith("sp12_v_"): return sp12v_normalize(netname, edge)
    if netname.startswith("sp12_h_"): return sp12h_normalize(netname, edge)
    if netname.startswith("input_2_"): netname = netname.replace("input_2_", "wire_logic_cluster/lc_") + "/in_2"
    netname = netname.replace("lc_trk_", "local_")
    netname = netname.replace("lc_", "lutff_")
    netname = netname.replace("wire_logic_cluster/", "")
    netname = netname.replace("wire_io_cluster/", "")
    netname = netname.replace("wire_mult/", "")
    netname = netname.replace("wire_con_box/", "")
    netname = netname.replace("wire_bram/", "")
    if (ramb or ramt or ramb_8k or ramt_8k) and netname.startswith("input"):
        match = re_match_cached(r"input(\d)_(\d)", netname)
        idx1, idx2 = (int(match.group(1)), int(match.group(2)))
        if ramb: netname="ram/WADDR_%d" % (idx1*4 + idx2)
        if ramt: netname="ram/RADDR_%d" % (idx1*4 + idx2)
        if ramb_8k: netname="ram/RADDR_%d" % ([7, 6, 5, 4, 3, 2, 1, 0, -1, -1, -1, -1, -1, 10, 9, 8][idx1*4 + idx2])
        if ramt_8k: netname="ram/WADDR_%d" % ([7, 6, 5, 4, 3, 2, 1, 0, -1, -1, -1, -1, -1, 10, 9, 8][idx1*4 + idx2])
    match = re_match_cached(r"(...)_op_(.*)", netname)
    if match and (match.group(1) != "slf"):
        netname = "neigh_op_%s_%s" % (match.group(1), match.group(2))
    if re_match_cached(r"lutff_7/(cen|clk|s_r)", netname):
        netname = netname.replace("lutff_7/", "lutff_global/")
    if re_match_cached(r"io_1/(cen|inclk|outclk)", netname):
        netname = netname.replace("io_1/", "io_global/")
    if netname == "carry_in_mux/cout":
        return "carry_in_mux"
    return netname

def pos_has_net(pos, netname):
    if pos in ("l", "r"):
        if re_search_cached(r"_vert_\d+$", netname): return False
        if re_search_cached(r"_horz_[rl]_\d+$", netname): return False
    if pos in ("t", "b"):
        if re_search_cached(r"_horz_\d+$", netname): return False
        if re_search_cached(r"_vert_[bt]_\d+$", netname): return False
    return True

def pos_follow_net(pos, direction, netname, is_ultra):
    if pos == "x" or ((pos in ("l", "r")) and is_ultra):
            m = re_match_cached(r"sp4_h_[lr]_(\d+)$", netname)
            if m and direction in ("l", "L"):
                n = sp4h_normalize(netname, "l")
                if n is not None:
                    if direction == "l" or is_ultra:
                        n = re_sub_cached("_l_", "_r_", n)
                        n = sp4h_normalize(n)
                    else:
                        n = re_sub_cached("_l_", "_", n)
                        n = re_sub_cached("sp4_h_", "span4_horz_", n)
                    return n
            if m and direction in ("r", "R"):
                n = sp4h_normalize(netname, "r")
                if n is not None:
                    if direction == "r" or is_ultra:
                        n = re_sub_cached("_r_", "_l_", n)
                        n = sp4h_normalize(n)
                    else:
                        n = re_sub_cached("_r_", "_", n)
                        n = re_sub_cached("sp4_h_", "span4_horz_", n)
                    return n

            m = re_match_cached(r"sp4_v_[tb]_(\d+)$", netname)
            if m and direction in ("t", "T"):
                n = sp4v_normalize(netname, "t")
                if n is not None:
                    if is_ultra and direction == "T" and pos in ("l", "r"):
                        return re_sub_cached("sp4_v_", "span4_vert_", n)
                    elif direction == "t":
                        n = re_sub_cached("_t_", "_b_", n)
                        n = sp4v_normalize(n)
                    else:
                        n = re_sub_cached("_t_", "_", n)
                        n = re_sub_cached("sp4_v_", "span4_vert_", n)
                    return n
            if m and direction in ("b", "B"):
                n = sp4v_normalize(netname, "b")
                if n is not None:
                    if is_ultra and direction == "B" and pos in ("l", "r"):
                        return re_sub_cached("sp4_v_", "span4_vert_", n)
                    elif direction == "b":
                        n = re_sub_cached("_b_", "_t_", n)
                        n = sp4v_normalize(n)
                    else:
                        n = re_sub_cached("_b_", "_", n)
                        n = re_sub_cached("sp4_v_", "span4_vert_", n)
                    return n

            m = re_match_cached(r"sp12_h_[lr]_(\d+)$", netname)
            if m and direction in ("l", "L"):
                n = sp12h_normalize(netname, "l")
                if n is not None:
                    if direction == "l" or is_ultra:
                        n = re_sub_cached("_l_", "_r_", n)
                        n = sp12h_normalize(n)
                    else:
                        n = re_sub_cached("_l_", "_", n)
                        n = re_sub_cached("sp12_h_", "span12_horz_", n)
                    return n
            if m and direction in ("r", "R"):
                n = sp12h_normalize(netname, "r")
                if n is not None:
                    if direction == "r" or is_ultra:
                        n = re_sub_cached("_r_", "_l_", n)
                        n = sp12h_normalize(n)
                    else:
                        n = re_sub_cached("_r_", "_", n)
                        n = re_sub_cached("sp12_h_", "span12_horz_", n)
                    return n

            m = re_match_cached(r"sp12_v_[tb]_(\d+)$", netname)
            if m and direction in ("t", "T"):
                n = sp12v_normalize(netname, "t")
                if n is not None:
                    if direction == "t":
                        n = re_sub_cached("_t_", "_b_", n)
                        n = sp12v_normalize(n)
                    elif direction == "T" and pos in ("l", "r"):
                        pass
                    else:
                        n = re_sub_cached("_t_", "_", n)
                        n = re_sub_cached("sp12_v_", "span12_vert_", n)
                    return n
            if m and direction in ("b", "B"):
                n = sp12v_normalize(netname, "b")
                if n is not None:
                    if direction == "b":
                        n = re_sub_cached("_b_", "_t_", n)
                        n = sp12v_normalize(n)
                    elif direction == "B" and pos in ("l", "r"):
                        pass
                    else:
                        n = re_sub_cached("_b_", "_", n)
                        n = re_sub_cached("sp12_v_", "span12_vert_", n)
                    return n

    if (pos in ("l", "r" )) and (not is_ultra):
        m = re_match_cached(r"span4_vert_([bt])_(\d+)$", netname)
        if m:
            case, idx = direction + m.group(1), int(m.group(2))
            if case == "tt":
                return "span4_vert_b_%d" % idx
            if case == "tb" and idx >= 4:
                return "span4_vert_b_%d" % (idx-4)
            if case == "bb" and idx < 12:
                return "span4_vert_b_%d" % (idx+4)
            if case == "bb" and idx >= 12:
                return "span4_vert_t_%d" % idx

    if pos in ("t", "b" ):
        m = re_match_cached(r"span4_horz_([rl])_(\d+)$", netname)
        if m:
            case, idx = direction + m.group(1), int(m.group(2))
            if direction == "L":
                return ultra_span4_horz_normalize(netname, "l")
            elif direction == "R":
                return ultra_span4_horz_normalize(netname, "r")            
            if case == "ll":
                return "span4_horz_r_%d" % idx
            if case == "lr" and idx >= 4:
                return "span4_horz_r_%d" % (idx-4)
            if case == "rr" and idx < 12:
                return "span4_horz_r_%d" % (idx+4)
            if case == "rr" and idx >= 12:
                return "span4_horz_l_%d" % idx

    if pos == "l" and direction == "r" and (not is_ultra):
            m = re_match_cached(r"span4_horz_(\d+)$", netname)
            if m: return sp4h_normalize("sp4_h_l_%s" % m.group(1))
            m = re_match_cached(r"span12_horz_(\d+)$", netname)
            if m: return sp12h_normalize("sp12_h_l_%s" % m.group(1))

    if pos == "r" and direction == "l" and (not is_ultra):
            m = re_match_cached(r"span4_horz_(\d+)$", netname)
            if m: return sp4h_normalize("sp4_h_r_%s" % m.group(1))
            m = re_match_cached(r"span12_horz_(\d+)$", netname)
            if m: return sp12h_normalize("sp12_h_r_%s" % m.group(1))

    if pos == "t" and direction == "b":
            m = re_match_cached(r"span4_vert_(\d+)$", netname)
            if m: return sp4v_normalize("sp4_v_t_%s" % m.group(1))
            m = re_match_cached(r"span12_vert_(\d+)$", netname)
            if m: return sp12v_normalize("sp12_v_t_%s" % m.group(1))

    if pos == "b" and direction == "t":
            m = re_match_cached(r"span4_vert_(\d+)$", netname)
            if m: return sp4v_normalize("sp4_v_b_%s" % m.group(1))
            m = re_match_cached(r"span12_vert_(\d+)$", netname)
            if m: return sp12v_normalize("sp12_v_b_%s" % m.group(1))

    return None

def get_lutff_bits(tile, index):
    bits = list("--------------------")
    for k, line in enumerate(tile):
        for i in range(36, 46):
            lutff_idx = k // 2
            lutff_bitnum = (i-36) + 10*(k%2)
            if lutff_idx == index:
                bits[lutff_bitnum] = line[i];
    return bits

def get_lutff_lut_bits(tile, index):
    lutff_bits = get_lutff_bits(tile, index)
    return [lutff_bits[i] for i in [4, 14, 15, 5, 6, 16, 17, 7, 3, 13, 12, 2, 1, 11, 10, 0]]

def get_lutff_seq_bits(tile, index):
    lutff_bits = get_lutff_bits(tile, index)
    return [lutff_bits[i] for i in [8, 9, 18, 19]]

def get_carry_cascade_bit(tile):
    return tile[1][49]

def get_carry_bit(tile):
    return tile[1][50]

def get_negclk_bit(tile):
    return tile[0][0]

def key_netname(netname):
    return re_sub_cached(r"\d+", lambda m: "%09d" % int(m.group(0)), netname)

def run_checks_neigh():
    print("Running consistency checks on neighbour finder..")
    ic = iceconfig()
    # ic.setup_empty_1k()
    #ic.setup_empty_lm4k()
    ic.setup_empty_u4k()
    #ic.setup_empty_5k()
    # ic.setup_empty_8k()
    # ic.setup_empty_384()

    all_segments = set()

    def add_segments(idx, db):
        for entry in db:
            if entry[1] in ("routing", "buffer"):
                if not ic.tile_has_net(idx[0], idx[1], entry[2]): continue
                if not ic.tile_has_net(idx[0], idx[1], entry[3]): continue
                all_segments.add((idx[0], idx[1], entry[2]))
                all_segments.add((idx[0], idx[1], entry[3]))

    for x in range(ic.max_x+1):
        for y in range(ic.max_x+1):
            # Skip the corners.
            if x in (0, ic.max_x) and y in (0, ic.max_y):
                continue
            add_segments((x, y), ic.tile_db(x, y))
            if (x, y) in ic.logic_tiles:
                all_segments.add((x, y, "lutff_7/cout"))

    for s1 in all_segments:
        for s2 in ic.follow_net(s1):
            # if s1[1] > 4: continue
            if s1 not in ic.follow_net(s2):
                print("ERROR: %s -> %s, but not vice versa!" % (s1, s2))
                print("Neighbours of %s:" % (s1,))
                for s in ic.follow_net(s1):
                    print("  ", s)
                print("Neighbours of %s:" % (s2,))
                for s in ic.follow_net(s2):
                    print("  ", s)
                print()

def run_checks():
    run_checks_neigh()

def parse_db(text, device="1k"):
    db = list()
    for line in text.split("\n"):
        line_384 = line.replace("384_glb_netwk_", "glb_netwk_")
        line_1k = line.replace("1k_glb_netwk_", "glb_netwk_")
        line_8k = line.replace("8k_glb_netwk_", "glb_netwk_")
        if line_1k != line:
            if device != "1k":
                continue
            line = line_1k
        elif line_8k != line:
            # global network is the same for 8k, 5k, lm4k, and u4k
            if device != "8k" and device != "5k" and device != "lm4k" and device != "u4k":
                continue
            line = line_8k
        elif line_384 != line:
            if device != "384":
                continue
            line = line_384
        line = line.split("\t")
        if len(line) == 0 or line[0] == "":
            continue
        line[0] = line[0].split(",")
        db.append(line)
    return db

extra_bits_db = {
    "1k": {
        (0, 330, 142): ("padin_glb_netwk", "0"),
        (0, 331, 142): ("padin_glb_netwk", "1"),
        (1, 330, 143): ("padin_glb_netwk", "2"),
        (1, 331, 143): ("padin_glb_netwk", "3"), # (1 3)  (331 144)  (331 144)  routing T_0_0.padin_3 <X> T_0_0.glb_netwk_3
        (1, 330, 142): ("padin_glb_netwk", "4"),
        (1, 331, 142): ("padin_glb_netwk", "5"),
        (0, 330, 143): ("padin_glb_netwk", "6"), # (0 0)  (330 143)  (330 143)  routing T_0_0.padin_6 <X> T_0_0.glb_netwk_6
        (0, 331, 143): ("padin_glb_netwk", "7"),
    },
    "lm4k": {
        (0, 654, 174): ("padin_glb_netwk", "0"),
        (0, 655, 174): ("padin_glb_netwk", "1"),
        (1, 654, 175): ("padin_glb_netwk", "2"),
        (1, 655, 175): ("padin_glb_netwk", "3"),
        (1, 654, 174): ("padin_glb_netwk", "4"), # HSOSC
        (1, 655, 174): ("padin_glb_netwk", "5"), # LSOSC
        (0, 654, 175): ("padin_glb_netwk", "6"),
        (0, 655, 175): ("padin_glb_netwk", "7"),
    },
    "5k": {
        (0, 690, 334): ("padin_glb_netwk", "0"), # check
        (0, 691, 334): ("padin_glb_netwk", "1"), # good
        (1, 690, 175): ("padin_glb_netwk", "2"), # good
        (1, 691, 175): ("padin_glb_netwk", "3"), # check
        (1, 690, 174): ("padin_glb_netwk", "4"), # good (INTOSC only)
        (1, 691, 174): ("padin_glb_netwk", "5"), # good (INTOSC only)
        (0, 690, 335): ("padin_glb_netwk", "6"), # check
        (0, 691, 335): ("padin_glb_netwk", "7"), # good
    },
    "u4k": {
        (0, 691, 175): ("padin_glb_netwk", "0"),   # good
        (1, 690, 175): ("padin_glb_netwk", "1"),   # good
        (0, 690, 175): ("padin_glb_netwk", "2"),   # made up
        (0, 690, 174): ("padin_glb_netwk", "3"),   # good
        (1, 690, 174): ("padin_glb_netwk", "4"),   # HFOSC, good
        (1, 691, 174): ("padin_glb_netwk", "5"),   # LFOSC, good
        (0, 691, 174): ("padin_glb_netwk", "6"),   # good
        (1, 691, 175): ("padin_glb_netwk", "7"),   # made up
        },
    "8k": {
        (0, 870, 270): ("padin_glb_netwk", "0"),
        (0, 871, 270): ("padin_glb_netwk", "1"),
        (1, 870, 271): ("padin_glb_netwk", "2"),
        (1, 871, 271): ("padin_glb_netwk", "3"),
        (1, 870, 270): ("padin_glb_netwk", "4"),
        (1, 871, 270): ("padin_glb_netwk", "5"),
        (0, 870, 271): ("padin_glb_netwk", "6"),
        (0, 871, 271): ("padin_glb_netwk", "7"),
    },
    "384": {
        (0, 180, 78): ("padin_glb_netwk", "0"),
        (0, 181, 78): ("padin_glb_netwk", "1"),
        (1, 180, 79): ("padin_glb_netwk", "2"),
        (1, 181, 79): ("padin_glb_netwk", "3"),
        (1, 180, 78): ("padin_glb_netwk", "4"),
        (1, 181, 78): ("padin_glb_netwk", "5"),
        (0, 180, 79): ("padin_glb_netwk", "6"),
        (0, 181, 79): ("padin_glb_netwk", "7"),
    }
}

gbufin_db = {
    "1k": [
        (13,  8,  7),
        ( 0,  8,  6),
        ( 7, 17,  1),
        ( 7,  0,  0),
        ( 0,  9,  3),
        (13,  9,  2),
        ( 6,  0,  5),
        ( 6, 17,  4),
    ],
    "5k": [
        ( 6,  0,  6), #checked
        (12,  0,  5), #checked
        (13,  0,  0), #checked
        (19,  0,  7), #checked
        ( 6, 31,  3), #checked
        (12, 31,  4), #checked
        (13, 31,  1), #checked
        (19, 31,  2), #checked
    ],
    "u4k": [
        (13,  0,  0), # 0 ok
        (13, 21,  1), # 1 ok
        (19, 21,  2), # 2 ok
        ( 6, 21,  3), # 3 ok
        (12, 21,  4), # 4 ok
        (12,  0,  5), # 5 ok
        ( 6,  0,  6), # 6 ok
        (19,  0,  7), # 7 ok
    ],
    "lm4k": [
        ( 6,  0,  6),
        (12,  0,  5),
        (13,  0,  0),
        (19,  0,  7),
        ( 6, 21,  3),
        (12, 21,  4),
        (13, 21,  1),
        (19, 21,  2),
    ],
    "8k": [
        (33, 16,  7),
        ( 0, 16,  6),
        (17, 33,  1),
        (17,  0,  0),
        ( 0, 17,  3),
        (33, 17,  2),
        (16,  0,  5),
        (16, 33,  4),
    ],
    "384": [
        ( 7,  4,  7),
        ( 0,  4,  6),
        ( 4,  9,  1),
        ( 4,  0,  0),
        ( 0,  5,  3),
        ( 7,  5,  2),
        ( 3,  0,  5),
        ( 3,  9,  4),
    ]
}

# To figure these out:
#   1. Copy io_latched.sh and convert it for your pinout (like io_latched_5k.sh).
#   2. Run it. It will create an io_latched_<device>.work directory with a bunch of files.
#   3. Grep the *.ve files in that directory for "'fabout')". The coordinates
#      before it are where the io latches are.
#
# Note: This may not work if your icepack configuration of cell sizes is incorrect because
# icebox_vlog.py won't correctly interpret the meaning of particular bits.
iolatch_db = {
    "1k": [
        ( 0,  7),
        (13, 10),
        ( 5,  0),
        ( 8, 17),
    ],
    "lm4k": [
        (14, 0),
        (14, 21)
    ],
    "5k": [
        (14, 0),
        (14, 31),
    ],
    "u4k": [
        (14, 0),
        (14, 21),
    ],
    "8k": [
        ( 0, 15),
        (33, 18),
        (18,  0),
        (15, 33),
    ],
    "384": [
        ( 0,  3), #384?
        ( 7,  5), #384?
        ( 2,  0), #384?
        ( 5,  9), #384?
    ],
}

# The x, y cell locations of the WARMBOOT controls. Run tests/sb_warmboot.v
# through icecube.sh to determine these values.
warmbootinfo_db = {
    "1k": {
        "BOOT": ( 12, 0, "fabout" ),
        "S0":   ( 13, 1, "fabout" ),
        "S1":   ( 13, 2, "fabout" ),
    },
    "5k": {
        # These are the right locations but may be the wrong order.
        "BOOT": ( 22, 0, "fabout" ),
        "S0":   ( 23, 0, "fabout" ),
        "S1":   ( 24, 0, "fabout" ),
    },
    "u4k": {
        # These are the right locations but may be the wrong order.
        "BOOT": ( 22, 0, "fabout" ),
        "S0":   ( 23, 0, "fabout" ),
        "S1":   ( 24, 0, "fabout" ),
        },
    "lm4k": {
        # These are the right locations but may be the wrong order.
        "BOOT": ( 23, 0, "fabout" ),
        "S0":   ( 24, 0, "fabout" ),
        "S1":   ( 25, 1, "fabout" ),
    },
    "8k": {
        "BOOT": ( 31, 0, "fabout" ),
        "S0":   ( 33, 1, "fabout" ),
        "S1":   ( 33, 2, "fabout" ),
    },
    "384": {
        "BOOT": ( 6, 0, "fabout" ), #384?
        "S0":   ( 7, 1, "fabout" ),
        "S1":   ( 7, 2, "fabout" ),
    }
}

noplls_db = {
    "1k-swg16tr": [ "1k" ],
    "1k-cm36": [ "1k" ],
    "1k-cm49": [ "1k" ],
    "8k-cm81": [ "8k_1" ],
    "8k-cm81:4k": [ "8k_1" ],
    "1k-qn48": [ "1k" ],
    "1k-cb81": [ "1k" ],
    "1k-vq100": [ "1k" ],
    "384-qn32": [ "384" ],
}

pllinfo_db = {
    "1k": {
        "LOC" : (6, 0),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 0,  3, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 0,  5, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 0,  5, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 0,  5, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 0,  2, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 0,  3, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 0,  4, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 0,  4, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 0,  3, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 0,  3, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 0,  3, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 0,  3, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 0,  3, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 0,  3, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 0,  4, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 0,  4, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 0,  4, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 0,  4, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 0,  4, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 0,  4, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 0,  4, "PLLCONFIG_8"),
        "DIVR_0":               ( 0,  1, "PLLCONFIG_1"),
        "DIVR_1":               ( 0,  1, "PLLCONFIG_2"),
        "DIVR_2":               ( 0,  1, "PLLCONFIG_3"),
        "DIVR_3":               ( 0,  1, "PLLCONFIG_4"),
        "DIVF_0":               ( 0,  1, "PLLCONFIG_5"),
        "DIVF_1":               ( 0,  1, "PLLCONFIG_6"),
        "DIVF_2":               ( 0,  1, "PLLCONFIG_7"),
        "DIVF_3":               ( 0,  1, "PLLCONFIG_8"),
        "DIVF_4":               ( 0,  1, "PLLCONFIG_9"),
        "DIVF_5":               ( 0,  2, "PLLCONFIG_1"),
        "DIVF_6":               ( 0,  2, "PLLCONFIG_2"),
        "DIVQ_0":               ( 0,  2, "PLLCONFIG_3"),
        "DIVQ_1":               ( 0,  2, "PLLCONFIG_4"),
        "DIVQ_2":               ( 0,  2, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 0,  2, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 0,  2, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 0,  2, "PLLCONFIG_8"),
        "TEST_MODE":            ( 0,  3, "PLLCONFIG_8"),
        "ENABLE_ICEGATE_PORTA": ( 0,  5, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": ( 0,  5, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        "PLLOUT_A":             ( 6,  0, 1),
        "PLLOUT_B":             ( 7,  0, 0),
        "REFERENCECLK":         ( 0,  1, "fabout"),
        "EXTFEEDBACK":          ( 0,  2, "fabout"),
        "DYNAMICDELAY_0":       ( 0,  4, "fabout"),
        "DYNAMICDELAY_1":       ( 0,  5, "fabout"),
        "DYNAMICDELAY_2":       ( 0,  6, "fabout"),
        "DYNAMICDELAY_3":       ( 0, 10, "fabout"),
        "DYNAMICDELAY_4":       ( 0, 11, "fabout"),
        "DYNAMICDELAY_5":       ( 0, 12, "fabout"),
        "DYNAMICDELAY_6":       ( 0, 13, "fabout"),
        "DYNAMICDELAY_7":       ( 0, 14, "fabout"),
        "LOCK":                 ( 1,  1, "neigh_op_bnl_1"),
        "BYPASS":               ( 1,  0, "fabout"),
        "RESETB":               ( 2,  0, "fabout"),
        "LATCHINPUTVALUE":      ( 5,  0, "fabout"),
        "SDO":                  (12,  1, "neigh_op_bnr_3"),
        "SDI":                  ( 4,  0, "fabout"),
        "SCLK":                 ( 3,  0, "fabout"),
    },
    "lm4k": {
        "LOC" : (12, 0),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            (12,  0, "PLLCONFIG_5"),
        "PLLTYPE_1":            (14,  0, "PLLCONFIG_1"),
        "PLLTYPE_2":            (14,  0, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      (14,  0, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      (11,  0, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      (12,  0, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     (13,  0, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    (13,  0, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    (12,  0, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    (12,  0, "PLLCONFIG_7"),
        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    (12,  0, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    (12,  0, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    (12,  0, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       (12,  0, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       (13,  0, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       (13,  0, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       (13,  0, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       (13,  0, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       (13,  0, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       (13,  0, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       (13,  0, "PLLCONFIG_8"),
        "DIVR_0":               (10,  0, "PLLCONFIG_1"),
        "DIVR_1":               (10,  0, "PLLCONFIG_2"),
        "DIVR_2":               (10,  0, "PLLCONFIG_3"),
        "DIVR_3":               (10,  0, "PLLCONFIG_4"),
        "DIVF_0":               (10,  0, "PLLCONFIG_5"),
        "DIVF_1":               (10,  0, "PLLCONFIG_6"),
        "DIVF_2":               (10,  0, "PLLCONFIG_7"),
        "DIVF_3":               (10,  0, "PLLCONFIG_8"),
        "DIVF_4":               (10,  0, "PLLCONFIG_9"),
        "DIVF_5":               (11,  0, "PLLCONFIG_1"),
        "DIVF_6":               (11,  0, "PLLCONFIG_2"),
        "DIVQ_0":               (11,  0, "PLLCONFIG_3"),
        "DIVQ_1":               (11,  0, "PLLCONFIG_4"),
        "DIVQ_2":               (11,  0, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       (11,  0, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       (11,  0, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       (11,  0, "PLLCONFIG_8"),
        "TEST_MODE":            (12,  0, "PLLCONFIG_8"),
        "ENABLE_ICEGATE_PORTA": (14,  0, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": (14,  0, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        # TODO(awygle) confirm these
        "PLLOUT_A":             ( 12,  0, 1), 
        "PLLOUT_B":             ( 13,  0, 0), 
        "REFERENCECLK":         ( 10,  0, "fabout"),
        "EXTFEEDBACK":          ( 11,  0, "fabout"), 
        "DYNAMICDELAY_0":       (  1,  0, "fabout"), 
        "DYNAMICDELAY_1":       (  2,  0, "fabout"), 
        "DYNAMICDELAY_2":       (  3,  0, "fabout"), 
        "DYNAMICDELAY_3":       (  4,  0, "fabout"), 
        "DYNAMICDELAY_4":       (  5,  0, "fabout"), 
        "DYNAMICDELAY_5":       (  7,  0, "fabout"), 
        "DYNAMICDELAY_6":       (  8,  0, "fabout"), 
        "DYNAMICDELAY_7":       (  9,  0, "fabout"), 
        "LOCK":                 (  1,  1, "neigh_op_bnl_1"), #check?
        "BYPASS":               ( 15,  0, "fabout"),
        "RESETB":               ( 16,  0, "fabout"),
        "LATCHINPUTVALUE":      ( 14,  0, "fabout"),
        "SDO":                  ( 24,  1, "neigh_op_bnr_3"), #check?
        "SDI":                  ( 18,  0, "fabout"),
        "SCLK":                 ( 17,  0, "fabout"),
    },
    "5k": {
        "LOC" : (12, 31),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            (12, 31, "PLLCONFIG_5"),
        "PLLTYPE_1":            (14, 31, "PLLCONFIG_1"),
        "PLLTYPE_2":            (14, 31, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      (14, 31, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      (11, 31, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      (12, 31, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     (13, 31, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    (13, 31, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    (12, 31, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    (12, 31, "PLLCONFIG_7"),
        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    (12, 31, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    (12, 31, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE_0":  (12, 31, "PLLCONFIG_4"),
        "SHIFTREG_DIV_MODE_1":  (14, 31, "PLLCONFIG_6"),
        "FDA_FEEDBACK_0":       (12, 31, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       (13, 31, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       (13, 31, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       (13, 31, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       (13, 31, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       (13, 31, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       (13, 31, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       (13, 31, "PLLCONFIG_8"),
        "DIVR_0":               (10, 31, "PLLCONFIG_1"),
        "DIVR_1":               (10, 31, "PLLCONFIG_2"),
        "DIVR_2":               (10, 31, "PLLCONFIG_3"),
        "DIVR_3":               (10, 31, "PLLCONFIG_4"),
        "DIVF_0":               (10, 31, "PLLCONFIG_5"),
        "DIVF_1":               (10, 31, "PLLCONFIG_6"),
        "DIVF_2":               (10, 31, "PLLCONFIG_7"),
        "DIVF_3":               (10, 31, "PLLCONFIG_8"),
        "DIVF_4":               (10, 31, "PLLCONFIG_9"),
        "DIVF_5":               (11, 31, "PLLCONFIG_1"),
        "DIVF_6":               (11, 31, "PLLCONFIG_2"),
        "DIVQ_0":               (11, 31, "PLLCONFIG_3"),
        "DIVQ_1":               (11, 31, "PLLCONFIG_4"),
        "DIVQ_2":               (11, 31, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       (11, 31, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       (11, 31, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       (11, 31, "PLLCONFIG_8"),
        "TEST_MODE":            (12, 31, "PLLCONFIG_8"),
        "ENABLE_ICEGATE_PORTA": (14, 31, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": (14, 31, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        "PLLOUT_A":             ( 12, 31, 1), 
        "PLLOUT_B":             ( 13, 31, 0), 
        "REFERENCECLK":         ( 10, 31, "fabout"),
        "EXTFEEDBACK":          ( 11, 31, "fabout"), 
        "DYNAMICDELAY_0":       (  1, 31, "fabout"), 
        "DYNAMICDELAY_1":       (  2, 31, "fabout"), 
        "DYNAMICDELAY_2":       (  3, 31, "fabout"), 
        "DYNAMICDELAY_3":       (  4, 31, "fabout"), 
        "DYNAMICDELAY_4":       (  5, 31, "fabout"), 
        "DYNAMICDELAY_5":       (  7, 31, "fabout"), 
        "DYNAMICDELAY_6":       (  8, 31, "fabout"), 
        "DYNAMICDELAY_7":       (  9, 31, "fabout"), 
        "LOCK":                 (  1, 30, "neigh_op_tnl_1"), #check?
        "BYPASS":               ( 15, 31, "fabout"),
        "RESETB":               ( 16, 31, "fabout"),
        "LATCHINPUTVALUE":      ( 14, 31, "fabout"),
        "SDO":                  ( 24, 30, "neigh_op_tnr_1"), #check?
        "SDI":                  ( 18, 31, "fabout"),
        "SCLK":                 ( 17, 31, "fabout"),
    },
    "u4k": {
        "LOC" : (12, 21),

        "PLLTYPE_1":            (14, 21, "PLLCONFIG_1"),
        "PLLTYPE_2":            (14, 21, "PLLCONFIG_3"),
        "PLLTYPE_0":            (12, 21, "PLLCONFIG_5"),
        "FEEDBACK_PATH_0":      (14, 21, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      (11, 21, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      (12, 21, "PLLCONFIG_1"),
        "PLLOUT_SELECT_A_0":    (12, 21, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    (12, 21, "PLLCONFIG_7"),
        "PLLOUT_SELECT_B_0":    (12, 21, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    (12, 21, "PLLCONFIG_3"),
        "SHIFTREG_DIV_MODE":    (12, 21, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       (12, 21, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       (13, 21, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       (13, 21, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       (13, 21, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       (13, 21, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       (13, 21, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       (13, 21, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       (13, 21, "PLLCONFIG_8"),
        "DIVR_0":               (10, 21, "PLLCONFIG_1"),
        "DIVR_1":               (10, 21, "PLLCONFIG_2"),
        "DIVR_2":               (10, 21, "PLLCONFIG_3"),
        "DIVR_3":               (10, 21, "PLLCONFIG_4"),
        "DIVF_0":               (10, 21, "PLLCONFIG_5"),
        "DIVF_1":               (10, 21, "PLLCONFIG_6"),
        "DIVF_2":               (10, 21, "PLLCONFIG_7"),
        "DIVF_3":               (10, 21, "PLLCONFIG_8"),
        "DIVF_4":               (10, 21, "PLLCONFIG_9"),
        "DIVF_5":               (11, 21, "PLLCONFIG_1"),
        "DIVF_6":               (11, 21, "PLLCONFIG_2"),
        "DIVQ_0":               (11, 21, "PLLCONFIG_3"),
        "DIVQ_1":               (11, 21, "PLLCONFIG_4"),
        "DIVQ_2":               (11, 21, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       (11, 21, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       (11, 21, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       (11, 21, "PLLCONFIG_8"),
        "TEST_MODE":            (12, 21, "PLLCONFIG_8"),
        "DELAY_ADJMODE_FB":     (13, 21, "PLLCONFIG_4"),
        "DELAY_ADJMODE_REL":    (13, 21, "PLLCONFIG_9"),
        "ENABLE_ICEGATE_PORTA": (14, 21, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": (14, 21, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        "PLLOUT_A":             ( 12, 21, 1),
        "PLLOUT_B":             ( 13, 21, 0),
        "REFERENCECLK":         ( 10, 21, "fabout"),
        "EXTFEEDBACK":          ( 11, 21, "fabout"),
        "DYNAMICDELAY_0":       (  1, 21, "fabout"),
        "DYNAMICDELAY_1":       (  2, 21, "fabout"),
        "DYNAMICDELAY_2":       (  3, 21, "fabout"),
        "DYNAMICDELAY_3":       (  4, 21, "fabout"),
        "DYNAMICDELAY_4":       (  5, 21, "fabout"),
        "DYNAMICDELAY_5":       (  7, 21, "fabout"),
        "DYNAMICDELAY_6":       (  8, 21, "fabout"),
        "DYNAMICDELAY_7":       (  9, 21, "fabout"),
        "LOCK":                 (  1, 20, "neigh_op_tnl_1"), #check?
        "BYPASS":               ( 15, 21, "fabout"),
        "RESETB":               ( 16, 21, "fabout"),
        "LATCHINPUTVALUE":      ( 14, 21, "fabout"),
        "SDO":                  ( 24, 20, "neigh_op_tnr_1"), #check?
        "SDI":                  ( 18, 21, "fabout"),
        "SCLK":                 ( 17, 21, "fabout"),
    },
    "8k_0": {
        "LOC" : (16, 0),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 16, 0, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 18, 0, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 18, 0, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 18, 0, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 15, 0, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 16, 0, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 17, 0, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 17, 0, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 16, 0, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 16, 0, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 16, 0, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 16, 0, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 16, 0, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 16, 0, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 17, 0, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 17, 0, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 17, 0, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 17, 0, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 17, 0, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 17, 0, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 17, 0, "PLLCONFIG_8"),
        "DIVR_0":               ( 14, 0, "PLLCONFIG_1"),
        "DIVR_1":               ( 14, 0, "PLLCONFIG_2"),
        "DIVR_2":               ( 14, 0, "PLLCONFIG_3"),
        "DIVR_3":               ( 14, 0, "PLLCONFIG_4"),
        "DIVF_0":               ( 14, 0, "PLLCONFIG_5"),
        "DIVF_1":               ( 14, 0, "PLLCONFIG_6"),
        "DIVF_2":               ( 14, 0, "PLLCONFIG_7"),
        "DIVF_3":               ( 14, 0, "PLLCONFIG_8"),
        "DIVF_4":               ( 14, 0, "PLLCONFIG_9"),
        "DIVF_5":               ( 15, 0, "PLLCONFIG_1"),
        "DIVF_6":               ( 15, 0, "PLLCONFIG_2"),
        "DIVQ_0":               ( 15, 0, "PLLCONFIG_3"),
        "DIVQ_1":               ( 15, 0, "PLLCONFIG_4"),
        "DIVQ_2":               ( 15, 0, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 15, 0, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 15, 0, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 15, 0, "PLLCONFIG_8"),
        "TEST_MODE":            ( 16, 0, "PLLCONFIG_8"),
        "ENABLE_ICEGATE_PORTA": ( 18, 0, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": ( 18, 0, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        "PLLOUT_A":             ( 16, 0, 1),
        "PLLOUT_B":             ( 17, 0, 0),
        "REFERENCECLK":         ( 13, 0, "fabout"),
        "EXTFEEDBACK":          ( 14, 0, "fabout"),
        "DYNAMICDELAY_0":       (  5, 0, "fabout"),
        "DYNAMICDELAY_1":       (  6, 0, "fabout"),
        "DYNAMICDELAY_2":       (  7, 0, "fabout"),
        "DYNAMICDELAY_3":       (  8, 0, "fabout"),
        "DYNAMICDELAY_4":       (  9, 0, "fabout"),
        "DYNAMICDELAY_5":       ( 10, 0, "fabout"),
        "DYNAMICDELAY_6":       ( 11, 0, "fabout"),
        "DYNAMICDELAY_7":       ( 12, 0, "fabout"),
        "LOCK":                 (  1, 1, "neigh_op_bnl_1"),
        "BYPASS":               ( 19, 0, "fabout"),
        "RESETB":               ( 20, 0, "fabout"),
        "LATCHINPUTVALUE":      ( 15, 0, "fabout"),
        "SDO":                  ( 32, 1, "neigh_op_bnr_3"),
        "SDI":                  ( 22, 0, "fabout"),
        "SCLK":                 ( 21, 0, "fabout"),
    },
    "8k_1": {
        "LOC" : (16, 33),

        # 3'b000 = "DISABLED"
        # 3'b010 = "SB_PLL40_PAD"
        # 3'b100 = "SB_PLL40_2_PAD"
        # 3'b110 = "SB_PLL40_2F_PAD"
        # 3'b011 = "SB_PLL40_CORE"
        # 3'b111 = "SB_PLL40_2F_CORE"
        "PLLTYPE_0":            ( 16, 33, "PLLCONFIG_5"),
        "PLLTYPE_1":            ( 18, 33, "PLLCONFIG_1"),
        "PLLTYPE_2":            ( 18, 33, "PLLCONFIG_3"),

        # 3'b000 = "DELAY"
        # 3'b001 = "SIMPLE"
        # 3'b010 = "PHASE_AND_DELAY"
        # 3'b110 = "EXTERNAL"
        "FEEDBACK_PATH_0":      ( 18, 33, "PLLCONFIG_5"),
        "FEEDBACK_PATH_1":      ( 15, 33, "PLLCONFIG_9"),
        "FEEDBACK_PATH_2":      ( 16, 33, "PLLCONFIG_1"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_FEEDBACK=4'b1111)
        "DELAY_ADJMODE_FB":     ( 17, 33, "PLLCONFIG_4"),

        # 1'b0 = "FIXED"
        # 1'b1 = "DYNAMIC" (also set FDA_RELATIVE=4'b1111)
        "DELAY_ADJMODE_REL":    ( 17, 33, "PLLCONFIG_9"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_A_0":    ( 16, 33, "PLLCONFIG_6"),
        "PLLOUT_SELECT_A_1":    ( 16, 33, "PLLCONFIG_7"),

        # 2'b00 = "GENCLK"
        # 2'b01 = "GENCLK_HALF"
        # 2'b10 = "SHIFTREG_90deg"
        # 2'b11 = "SHIFTREG_0deg"
        "PLLOUT_SELECT_B_0":    ( 16, 33, "PLLCONFIG_2"),
        "PLLOUT_SELECT_B_1":    ( 16, 33, "PLLCONFIG_3"),

        # Numeric Parameters
        "SHIFTREG_DIV_MODE":    ( 16, 33, "PLLCONFIG_4"),
        "FDA_FEEDBACK_0":       ( 16, 33, "PLLCONFIG_9"),
        "FDA_FEEDBACK_1":       ( 17, 33, "PLLCONFIG_1"),
        "FDA_FEEDBACK_2":       ( 17, 33, "PLLCONFIG_2"),
        "FDA_FEEDBACK_3":       ( 17, 33, "PLLCONFIG_3"),
        "FDA_RELATIVE_0":       ( 17, 33, "PLLCONFIG_5"),
        "FDA_RELATIVE_1":       ( 17, 33, "PLLCONFIG_6"),
        "FDA_RELATIVE_2":       ( 17, 33, "PLLCONFIG_7"),
        "FDA_RELATIVE_3":       ( 17, 33, "PLLCONFIG_8"),
        "DIVR_0":               ( 14, 33, "PLLCONFIG_1"),
        "DIVR_1":               ( 14, 33, "PLLCONFIG_2"),
        "DIVR_2":               ( 14, 33, "PLLCONFIG_3"),
        "DIVR_3":               ( 14, 33, "PLLCONFIG_4"),
        "DIVF_0":               ( 14, 33, "PLLCONFIG_5"),
        "DIVF_1":               ( 14, 33, "PLLCONFIG_6"),
        "DIVF_2":               ( 14, 33, "PLLCONFIG_7"),
        "DIVF_3":               ( 14, 33, "PLLCONFIG_8"),
        "DIVF_4":               ( 14, 33, "PLLCONFIG_9"),
        "DIVF_5":               ( 15, 33, "PLLCONFIG_1"),
        "DIVF_6":               ( 15, 33, "PLLCONFIG_2"),
        "DIVQ_0":               ( 15, 33, "PLLCONFIG_3"),
        "DIVQ_1":               ( 15, 33, "PLLCONFIG_4"),
        "DIVQ_2":               ( 15, 33, "PLLCONFIG_5"),
        "FILTER_RANGE_0":       ( 15, 33, "PLLCONFIG_6"),
        "FILTER_RANGE_1":       ( 15, 33, "PLLCONFIG_7"),
        "FILTER_RANGE_2":       ( 15, 33, "PLLCONFIG_8"),
        "TEST_MODE":            ( 16, 33, "PLLCONFIG_8"),
        "ENABLE_ICEGATE_PORTA": ( 18, 33, "PLLCONFIG_2"), # Controls global output only !
        "ENABLE_ICEGATE_PORTB": ( 18, 33, "PLLCONFIG_4"), # Controls global output only !

        # PLL Ports
        "PLLOUT_A":             ( 16, 33, 1),
        "PLLOUT_B":             ( 17, 33, 0),
        "REFERENCECLK":         ( 13, 33, "fabout"),
        "EXTFEEDBACK":          ( 14, 33, "fabout"),
        "DYNAMICDELAY_0":       (  5, 33, "fabout"),
        "DYNAMICDELAY_1":       (  6, 33, "fabout"),
        "DYNAMICDELAY_2":       (  7, 33, "fabout"),
        "DYNAMICDELAY_3":       (  8, 33, "fabout"),
        "DYNAMICDELAY_4":       (  9, 33, "fabout"),
        "DYNAMICDELAY_5":       ( 10, 33, "fabout"),
        "DYNAMICDELAY_6":       ( 11, 33, "fabout"),
        "DYNAMICDELAY_7":       ( 12, 33, "fabout"),
        "LOCK":                 (  1, 32, "neigh_op_tnl_1"),
        "BYPASS":               ( 19, 33, "fabout"),
        "RESETB":               ( 20, 33, "fabout"),
        "LATCHINPUTVALUE":      ( 15, 33, "fabout"),
        "SDO":                  ( 32, 32, "neigh_op_tnr_1"),
        "SDI":                  ( 22, 33, "fabout"),
        "SCLK":                 ( 21, 33, "fabout"),
    },
}

padin_pio_db = {
    "1k": [
        (13,  8, 1),  # glb_netwk_0
        ( 0,  8, 1),  # glb_netwk_1
        ( 7, 17, 0),  # glb_netwk_2
        ( 7,  0, 0),  # glb_netwk_3
        ( 0,  9, 0),  # glb_netwk_4
        (13,  9, 0),  # glb_netwk_5
        ( 6,  0, 1),  # glb_netwk_6
        ( 6, 17, 1),  # glb_netwk_7
    ],
    "lm4k": [
        (19,  0, 0), #0 fixed
        ( 6,  0, 1), #1 fixed
        (13, 21, 0), #2 fixed
        (13,  0, 0), #3 fixed
        
        (19, 21, 0), #These two are questionable, but keep the order correct
        ( 6, 21, 0), #They may need to be fixed if other package options are added.

        (12,  0, 1), #6 fixed
        (12, 21, 1), #7 fixed
    ],
    "5k": [
        (19,  0, 1), #0 fixed
        ( 6,  0, 1), #1 fixed
        (13, 31, 0), #2 fixed
        (13,  0, 0), #3 fixed
        
        (19, 31, 0), #These two are questionable, but keep the order correct
        ( 6, 31, 0), #They may need to be fixed if other package options are added.

        (12,  0, 1), #6 fixed
        (12, 31, 1), #7 fixed
    ],
    "u4k": [
        (19,  0, 1), # 0 ok
        ( 6,  0, 1), # 1 ok

        (13, 21, 0), # 2 ok
        (13,  0, 0), # 3 unclear
        (19, 21, 0), # 4 HFOSC unclear
        ( 6, 21, 0), # 5 LFOSC unclear
        (12,  0, 1), # 6 unclear
        (12, 21, 1), # 7 ok
    ],
    "8k": [
        (33, 16, 1),
        ( 0, 16, 1),
        (17, 33, 0),
        (17,  0, 0),
        ( 0, 17, 0),
        (33, 17, 0),
        (16,  0, 1),
        (16, 33, 1),
    ],
    "384": [
        ( 7,  4, 1),
        ( 0,  4, 1),
        ( 4,  9, 0),
        ( 4,  0, 0), #QFN32: no pin?!
        ( 0,  5, 0),
        ( 7,  5, 0),
        ( 3,  0, 1), #QFN32: no pin?!
        ( 3,  9, 1),
    ]
}

ieren_db = {
    "1k": [
        # IO-block (X, Y, Z) <-> IeRen-block (X, Y, Z)
        ( 0,  2, 0,  0,  2, 1),
        ( 0,  2, 1,  0,  2, 0),
        ( 0,  3, 0,  0,  3, 1),
        ( 0,  3, 1,  0,  3, 0),
        ( 0,  4, 0,  0,  4, 1),
        ( 0,  4, 1,  0,  4, 0),
        ( 0,  5, 0,  0,  5, 1),
        ( 0,  5, 1,  0,  5, 0),
        ( 0,  6, 0,  0,  6, 1),
        ( 0,  6, 1,  0,  6, 0),
        ( 0,  8, 0,  0,  8, 1),
        ( 0,  8, 1,  0,  8, 0),
        ( 0,  9, 0,  0,  9, 1),
        ( 0,  9, 1,  0,  9, 0),
        ( 0, 10, 0,  0, 10, 1),
        ( 0, 10, 1,  0, 10, 0),
        ( 0, 11, 0,  0, 11, 1),
        ( 0, 11, 1,  0, 11, 0),
        ( 0, 12, 0,  0, 12, 1),
        ( 0, 12, 1,  0, 12, 0),
        ( 0, 13, 0,  0, 13, 1),
        ( 0, 13, 1,  0, 13, 0),
        ( 0, 14, 0,  0, 14, 1),
        ( 0, 14, 1,  0, 14, 0),
        ( 1,  0, 0,  1,  0, 0),
        ( 1,  0, 1,  1,  0, 1),
        ( 1, 17, 0,  1, 17, 0),
        ( 1, 17, 1,  1, 17, 1),
        ( 2,  0, 0,  2,  0, 0),
        ( 2,  0, 1,  2,  0, 1),
        ( 2, 17, 0,  2, 17, 0),
        ( 2, 17, 1,  2, 17, 1),
        ( 3,  0, 0,  3,  0, 0),
        ( 3,  0, 1,  3,  0, 1),
        ( 3, 17, 0,  3, 17, 0),
        ( 3, 17, 1,  3, 17, 1),
        ( 4,  0, 0,  4,  0, 0),
        ( 4,  0, 1,  4,  0, 1),
        ( 4, 17, 0,  4, 17, 0),
        ( 4, 17, 1,  4, 17, 1),
        ( 5,  0, 0,  5,  0, 0),
        ( 5,  0, 1,  5,  0, 1),
        ( 5, 17, 0,  5, 17, 0),
        ( 5, 17, 1,  5, 17, 1),
        ( 6,  0, 0,  7,  0, 0),
        ( 6,  0, 1,  6,  0, 0),
        ( 6, 17, 0,  6, 17, 0),
        ( 6, 17, 1,  6, 17, 1),
        ( 7,  0, 0,  6,  0, 1),
        ( 7,  0, 1,  7,  0, 1),
        ( 7, 17, 0,  7, 17, 0),
        ( 7, 17, 1,  7, 17, 1),
        ( 8,  0, 0,  8,  0, 0),
        ( 8,  0, 1,  8,  0, 1),
        ( 8, 17, 0,  8, 17, 0),
        ( 8, 17, 1,  8, 17, 1),
        ( 9,  0, 0,  9,  0, 0),
        ( 9,  0, 1,  9,  0, 1),
        ( 9, 17, 0, 10, 17, 0),
        ( 9, 17, 1, 10, 17, 1),
        (10,  0, 0, 10,  0, 0),
        (10,  0, 1, 10,  0, 1),
        (10, 17, 0,  9, 17, 0),
        (10, 17, 1,  9, 17, 1),
        (11,  0, 0, 11,  0, 0),
        (11,  0, 1, 11,  0, 1),
        (11, 17, 0, 11, 17, 0),
        (11, 17, 1, 11, 17, 1),
        (12,  0, 0, 12,  0, 0),
        (12,  0, 1, 12,  0, 1),
        (12, 17, 0, 12, 17, 0),
        (12, 17, 1, 12, 17, 1),
        (13,  1, 0, 13,  1, 0),
        (13,  1, 1, 13,  1, 1),
        (13,  2, 0, 13,  2, 0),
        (13,  2, 1, 13,  2, 1),
        (13,  3, 1, 13,  3, 1),
        (13,  4, 0, 13,  4, 0),
        (13,  4, 1, 13,  4, 1),
        (13,  6, 0, 13,  6, 0),
        (13,  6, 1, 13,  6, 1),
        (13,  7, 0, 13,  7, 0),
        (13,  7, 1, 13,  7, 1),
        (13,  8, 0, 13,  8, 0),
        (13,  8, 1, 13,  8, 1),
        (13,  9, 0, 13,  9, 0),
        (13,  9, 1, 13,  9, 1),
        (13, 11, 0, 13, 10, 0),
        (13, 11, 1, 13, 10, 1),
        (13, 12, 0, 13, 11, 0),
        (13, 12, 1, 13, 11, 1),
        (13, 13, 0, 13, 13, 0),
        (13, 13, 1, 13, 13, 1),
        (13, 14, 0, 13, 14, 0),
        (13, 14, 1, 13, 14, 1),
        (13, 15, 0, 13, 15, 0),
        (13, 15, 1, 13, 15, 1),
    ],
    "8k": [
        ( 0,  3, 0,  0,  3, 0),
        ( 0,  3, 1,  0,  3, 1),
        ( 0,  4, 0,  0,  4, 0),
        ( 0,  4, 1,  0,  4, 1),
        ( 0,  5, 0,  0,  5, 0),
        ( 0,  5, 1,  0,  5, 1),
        ( 0,  6, 0,  0,  6, 0),
        ( 0,  6, 1,  0,  6, 1),
        ( 0,  7, 0,  0,  7, 0),
        ( 0,  7, 1,  0,  7, 1),
        ( 0,  8, 0,  0,  8, 0),
        ( 0,  8, 1,  0,  8, 1),
        ( 0,  9, 0,  0,  9, 0),
        ( 0,  9, 1,  0,  9, 1),
        ( 0, 10, 0,  0, 10, 0),
        ( 0, 10, 1,  0, 10, 1),
        ( 0, 11, 0,  0, 11, 0),
        ( 0, 11, 1,  0, 11, 1),
        ( 0, 12, 0,  0, 12, 0),
        ( 0, 12, 1,  0, 12, 1),
        ( 0, 13, 0,  0, 13, 0),
        ( 0, 13, 1,  0, 13, 1),
        ( 0, 14, 0,  0, 14, 0),
        ( 0, 14, 1,  0, 14, 1),
        ( 0, 16, 0,  0, 16, 0),
        ( 0, 16, 1,  0, 16, 1),
        ( 0, 17, 0,  0, 17, 0),
        ( 0, 17, 1,  0, 17, 1),
        ( 0, 18, 0,  0, 18, 0),
        ( 0, 18, 1,  0, 18, 1),
        ( 0, 19, 0,  0, 19, 0),
        ( 0, 19, 1,  0, 19, 1),
        ( 0, 20, 0,  0, 20, 0),
        ( 0, 20, 1,  0, 20, 1),
        ( 0, 21, 0,  0, 21, 0),
        ( 0, 21, 1,  0, 21, 1),
        ( 0, 22, 0,  0, 22, 0),
        ( 0, 22, 1,  0, 22, 1),
        ( 0, 23, 0,  0, 23, 0),
        ( 0, 23, 1,  0, 23, 1),
        ( 0, 24, 0,  0, 24, 0),
        ( 0, 24, 1,  0, 24, 1),
        ( 0, 25, 0,  0, 25, 0),
        ( 0, 25, 1,  0, 25, 1),
        ( 0, 27, 0,  0, 27, 0),
        ( 0, 27, 1,  0, 27, 1),
        ( 0, 28, 0,  0, 28, 0),
        ( 0, 28, 1,  0, 28, 1),
        ( 0, 30, 0,  0, 30, 0),
        ( 0, 30, 1,  0, 30, 1),
        ( 0, 31, 0,  0, 31, 0),
        ( 0, 31, 1,  0, 31, 1),
        ( 1, 33, 0,  1, 33, 0),
        ( 1, 33, 1,  1, 33, 1),
        ( 2,  0, 0,  2,  0, 0),
        ( 2,  0, 1,  2,  0, 1),
        ( 2, 33, 0,  2, 33, 0),
        ( 2, 33, 1,  2, 33, 1),
        ( 3,  0, 0,  3,  0, 0),
        ( 3,  0, 1,  3,  0, 1),
        ( 3, 33, 0,  3, 33, 0),
        ( 3, 33, 1,  3, 33, 1),
        ( 4,  0, 0,  4,  0, 0),
        ( 4,  0, 1,  4,  0, 1),
        ( 4, 33, 0,  4, 33, 0),
        ( 4, 33, 1,  4, 33, 1),
        ( 5,  0, 0,  5,  0, 0),
        ( 5,  0, 1,  5,  0, 1),
        ( 5, 33, 0,  5, 33, 0),
        ( 5, 33, 1,  5, 33, 1),
        ( 6,  0, 0,  6,  0, 0),
        ( 6,  0, 1,  6,  0, 1),
        ( 6, 33, 0,  6, 33, 0),
        ( 6, 33, 1,  6, 33, 1),
        ( 7,  0, 0,  7,  0, 0),
        ( 7,  0, 1,  7,  0, 1),
        ( 7, 33, 0,  7, 33, 0),
        ( 7, 33, 1,  7, 33, 1),
        ( 8,  0, 0,  8,  0, 0),
        ( 8,  0, 1,  8,  0, 1),
        ( 8, 33, 0,  8, 33, 0),
        ( 8, 33, 1,  8, 33, 1),
        ( 9,  0, 0,  9,  0, 0),
        ( 9,  0, 1,  9,  0, 1),
        ( 9, 33, 0,  9, 33, 0),
        ( 9, 33, 1,  9, 33, 1),
        (10,  0, 0, 10,  0, 0),
        (10,  0, 1, 10,  0, 1),
        (10, 33, 0, 10, 33, 0),
        (10, 33, 1, 10, 33, 1),
        (11,  0, 0, 11,  0, 0),
        (11,  0, 1, 11,  0, 1),
        (11, 33, 0, 11, 33, 0),
        (11, 33, 1, 11, 33, 1),
        (12,  0, 0, 12,  0, 0),
        (12,  0, 1, 12,  0, 1),
        (12, 33, 0, 12, 33, 0),
        (13,  0, 0, 13,  0, 0),
        (13,  0, 1, 13,  0, 1),
        (13, 33, 0, 13, 33, 0),
        (13, 33, 1, 13, 33, 1),
        (14,  0, 0, 14,  0, 0),
        (14,  0, 1, 14,  0, 1),
        (14, 33, 0, 14, 33, 0),
        (14, 33, 1, 14, 33, 1),
        (15,  0, 0, 15,  0, 0),
        (15,  0, 1, 15,  0, 1),
        (16,  0, 0, 16,  0, 0),
        (16,  0, 1, 16,  0, 1),
        (16, 33, 0, 16, 33, 0),
        (16, 33, 1, 16, 33, 1),
        (17,  0, 0, 17,  0, 0),
        (17,  0, 1, 17,  0, 1),
        (17, 33, 0, 17, 33, 0),
        (17, 33, 1, 17, 33, 1),
        (18, 33, 0, 18, 33, 0),
        (18, 33, 1, 18, 33, 1),
        (19,  0, 0, 19,  0, 0),
        (19,  0, 1, 19,  0, 1),
        (19, 33, 0, 19, 33, 0),
        (19, 33, 1, 19, 33, 1),
        (20,  0, 0, 20,  0, 0),
        (20,  0, 1, 20,  0, 1),
        (20, 33, 0, 20, 33, 0),
        (20, 33, 1, 20, 33, 1),
        (21,  0, 0, 21,  0, 0),
        (21,  0, 1, 21,  0, 1),
        (21, 33, 0, 21, 33, 0),
        (21, 33, 1, 21, 33, 1),
        (22,  0, 0, 22,  0, 0),
        (22,  0, 1, 22,  0, 1),
        (22, 33, 0, 22, 33, 0),
        (22, 33, 1, 22, 33, 1),
        (23,  0, 0, 23,  0, 0),
        (23,  0, 1, 23,  0, 1),
        (23, 33, 0, 23, 33, 0),
        (23, 33, 1, 23, 33, 1),
        (24,  0, 0, 24,  0, 0),
        (24,  0, 1, 24,  0, 1),
        (24, 33, 0, 24, 33, 0),
        (24, 33, 1, 24, 33, 1),
        (25,  0, 0, 25,  0, 0),
        (25, 33, 0, 25, 33, 0),
        (25, 33, 1, 25, 33, 1),
        (26,  0, 0, 26,  0, 0),
        (26,  0, 1, 26,  0, 1),
        (26, 33, 0, 26, 33, 0),
        (26, 33, 1, 26, 33, 1),
        (27,  0, 0, 27,  0, 0),
        (27,  0, 1, 27,  0, 1),
        (27, 33, 0, 27, 33, 0),
        (27, 33, 1, 27, 33, 1),
        (28,  0, 0, 28,  0, 0),
        (28, 33, 1, 28, 33, 1),
        (29,  0, 0, 29,  0, 0),
        (29,  0, 1, 29,  0, 1),
        (29, 33, 0, 29, 33, 0),
        (29, 33, 1, 29, 33, 1),
        (30,  0, 0, 30,  0, 0),
        (30,  0, 1, 30,  0, 1),
        (30, 33, 0, 30, 33, 0),
        (30, 33, 1, 30, 33, 1),
        (31,  0, 0, 31,  0, 0),
        (31,  0, 1, 31,  0, 1),
        (31, 33, 0, 31, 33, 0),
        (31, 33, 1, 31, 33, 1),
        (33,  1, 0, 33,  1, 0),
        (33,  1, 1, 33,  1, 1),
        (33,  2, 0, 33,  2, 0),
        (33,  2, 1, 33,  2, 1),
        (33,  3, 0, 33,  3, 0),
        (33,  3, 1, 33,  3, 1),
        (33,  4, 0, 33,  4, 0),
        (33,  4, 1, 33,  4, 1),
        (33,  5, 0, 33,  5, 0),
        (33,  5, 1, 33,  5, 1),
        (33,  6, 0, 33,  6, 0),
        (33,  6, 1, 33,  6, 1),
        (33,  7, 0, 33,  7, 0),
        (33,  7, 1, 33,  7, 1),
        (33,  8, 0, 33,  8, 0),
        (33,  9, 0, 33,  9, 0),
        (33,  9, 1, 33,  9, 1),
        (33, 10, 0, 33, 10, 0),
        (33, 10, 1, 33, 10, 1),
        (33, 11, 0, 33, 11, 0),
        (33, 11, 1, 33, 11, 1),
        (33, 12, 0, 33, 12, 0),
        (33, 13, 0, 33, 13, 0),
        (33, 13, 1, 33, 13, 1),
        (33, 14, 0, 33, 14, 0),
        (33, 14, 1, 33, 14, 1),
        (33, 15, 0, 33, 15, 0),
        (33, 15, 1, 33, 15, 1),
        (33, 16, 0, 33, 16, 0),
        (33, 16, 1, 33, 16, 1),
        (33, 17, 0, 33, 17, 0),
        (33, 17, 1, 33, 17, 1),
        (33, 19, 0, 33, 19, 0),
        (33, 19, 1, 33, 19, 1),
        (33, 20, 0, 33, 20, 0),
        (33, 20, 1, 33, 20, 1),
        (33, 21, 0, 33, 21, 0),
        (33, 21, 1, 33, 21, 1),
        (33, 22, 0, 33, 22, 0),
        (33, 22, 1, 33, 22, 1),
        (33, 23, 0, 33, 23, 0),
        (33, 23, 1, 33, 23, 1),
        (33, 24, 0, 33, 24, 0),
        (33, 24, 1, 33, 24, 1),
        (33, 25, 0, 33, 25, 0),
        (33, 25, 1, 33, 25, 1),
        (33, 26, 0, 33, 26, 0),
        (33, 26, 1, 33, 26, 1),
        (33, 27, 0, 33, 27, 0),
        (33, 27, 1, 33, 27, 1),
        (33, 28, 0, 33, 28, 0),
        (33, 28, 1, 33, 28, 1),
        (33, 29, 1, 33, 29, 1),
        (33, 30, 0, 33, 30, 0),
        (33, 30, 1, 33, 30, 1),
        (33, 31, 0, 33, 31, 0),
    ],
    "384": [
        ( 0,  1, 0,  0,  1, 1),
        ( 0,  1, 1,  0,  1, 0),
        ( 0,  2, 0,  0,  2, 1),
        ( 0,  2, 1,  0,  2, 0),
        ( 0,  4, 0,  0,  4, 1),
        ( 0,  4, 1,  0,  4, 0),
        ( 0,  5, 0,  0,  5, 1),
        ( 0,  5, 1,  0,  5, 0),
        ( 0,  6, 0,  0,  6, 1),
        ( 0,  6, 1,  0,  6, 0),
        ( 0,  7, 0,  0,  7, 1),
        ( 0,  7, 1,  0,  7, 0),
        ( 2,  9, 0,  2,  9, 1),
        ( 2,  9, 1,  2,  9, 0),
        ( 3,  0, 0,  3,  0, 1),
        ( 3,  0, 1,  3,  0, 0),
        ( 3,  9, 0,  3,  9, 1),
        ( 3,  9, 1,  3,  9, 0),
        ( 4,  0, 0,  4,  0, 1),
        ( 4,  0, 1,  4,  0, 0),
        ( 4,  9, 0,  4,  9, 1),
        ( 4,  9, 1,  4,  9, 0),
        ( 5,  0, 0,  5,  0, 1),
        ( 5,  0, 1,  5,  0, 0),
        ( 5,  9, 0,  5,  9, 1),
        ( 5,  9, 1,  5,  9, 0),
        ( 6,  0, 0,  6,  0, 1),
        ( 6,  0, 1,  6,  0, 0),
        ( 6,  9, 0,  6,  9, 1),
        ( 6,  9, 1,  6,  9, 0),
        ( 7,  3, 1,  7,  3, 0),
        ( 7,  4, 0,  7,  4, 1),
        ( 7,  4, 1,  7,  4, 0),
        ( 7,  5, 0,  7,  5, 1),
        ( 7,  5, 1,  7,  5, 0),
        ( 7,  6, 0,  7,  6, 1),
        ( 7,  6, 1,  7,  6, 0),
    ],
    "lm4k": [
        ( 4, 21,  0,  4, 21,  1),
        ( 4, 21,  1,  4, 21,  0),
        ( 5, 21,  1,  5, 21,  0),
        ( 6,  0,  0,  6,  0,  1),
        ( 6,  0,  1,  6,  0,  0),
        ( 6, 21,  0,  6, 21,  1),
        ( 7,  0,  0,  7,  0,  1),
        ( 7,  0,  1,  7,  0,  0),
        ( 7, 21,  1,  7, 21,  0),
        ( 8,  0,  0,  8,  0,  1),
        ( 8,  0,  1,  8,  0,  0),
        ( 9, 21,  1,  9, 21,  0),
        ( 9, 21,  0,  9, 21,  1),
        (10,  0,  0, 10,  0,  1),
        (12,  0,  0, 12,  0,  1),
        (12,  0,  1, 12,  0,  0),
        (12, 21,  1, 12, 21,  0),
        (13,  0,  0, 13,  0,  1),
        (13,  0,  1, 13,  0,  0),
        (13, 21,  0, 13, 21,  1),
        (14,  0,  1, 14,  0,  0),
        (15, 21,  0, 15, 21,  1),
        (16, 21,  1, 16, 21,  0),
        (17, 21,  1, 17, 21,  0),
        (18, 21,  0, 18, 21,  1),
        (19,  0,  0, 19,  0,  1),
        (19,  0,  1, 19,  0,  0),
        (19, 21,  0, 19, 21,  1),
        (19, 21,  1, 19, 21,  0),
        (21,  0,  0, 21,  0,  1),
        (21,  0,  1, 21,  0,  0),
        (21, 21,  1, 21, 21,  0),
        (22,  0,  0, 22,  0,  1),
        (22,  0,  1, 22,  0,  0),
        (22, 21,  1, 22, 21,  0),
        (23,  0,  0, 23,  0,  1),
        (23,  0,  1, 23,  0,  0),
        (23, 21,  0, 23, 21,  1),
        (23, 21,  1, 23, 21,  0),
        (24,  0,  0, 24,  0,  1),
        (24,  0,  1, 24,  0,  0),
    ],
    "5k": [
        ( 8,  0,  0,  8,  0,  1),
        ( 9,  0,  1,  9,  0,  0),
        ( 9,  0,  0,  9,  0,  1),
        (13,  0,  1, 13,  0,  0),
        (15,  0,  0, 15,  0,  1),
        (16,  0,  0, 16,  0,  1),
        (17,  0,  0, 17,  0,  1),
        (18,  0,  0, 18,  0,  1),
        (19,  0,  0, 19,  0,  1),
        (23,  0,  0, 23,  0,  1),
        (24,  0,  0, 24,  0,  1),
        (24,  0,  1, 24,  0,  0),
        (23,  0,  1, 23,  0,  0),
        (22,  0,  1, 22,  0,  0),
        (21,  0,  1, 21,  0,  0),
        (19,  0,  1, 19,  0,  0),
        (18,  0,  1, 18,  0,  0),
        (19, 31,  0, 19, 31,  1),
        (19, 31,  1, 19, 31,  0),
        (18, 31,  0, 18, 31,  1),
        (18, 31,  1, 18, 31,  0),
        (17, 31,  0, 17, 31,  1),
        (16, 31,  1, 16, 31,  0),
        (16, 31,  0, 16, 31,  1),
        (13, 31,  1, 13, 31,  0),
        (12, 31,  1, 12, 31,  0),
        ( 9, 31,  1,  9, 31,  0),
        (13, 31,  0, 13, 31,  1),
        ( 4, 31,  0,  4, 31,  1),
        ( 5, 31,  0,  5, 31,  1),
        ( 6, 31,  0,  6, 31,  1),
        ( 8, 31,  1,  8, 31,  0),
        ( 8, 31,  0,  8, 31,  1),
        ( 9, 31,  0,  9, 31,  1),
        ( 6,  0,  1,  6,  0,  0),
        ( 7,  0,  1,  7,  0,  0),
        ( 5,  0,  0,  5,  0,  1),
        ( 6,  0,  0,  6,  0,  1),
        ( 7,  0,  0,  7,  0,  1),
        (12, 31,  0, 12, 31,  1),
        (12,  0,  0, 12,  0,  1),
        (13,  0,  0, 13,  0,  1),
        (12,  0,  1, 12,  0,  0)
    ],
    "u4k": [
        ( 4, 21, 0,  4, 21, 1),
        ( 5,  0, 0,  5,  0, 1),
        ( 5, 21, 0,  5, 21, 1),
        ( 6,  0, 0,  6,  0, 1),
        ( 6,  0, 1,  6,  0, 0),
        ( 6, 21, 0,  6, 21, 1),
        ( 7,  0, 0,  7,  0, 1),
        ( 7,  0, 1,  7,  0, 0),
        ( 8,  0, 0,  8,  0, 1),
        ( 8, 21, 0,  8, 21, 1),
        ( 8, 21, 1,  8, 21, 0),
        ( 9,  0, 0,  9,  0, 1),
        ( 9,  0, 1,  9,  0, 0),
        ( 9, 21, 0,  9, 21, 1),
        ( 9, 21, 1,  9, 21, 0),
        (12, 21, 1, 12, 21, 0),
        (13,  0, 1, 13,  0, 0),
        (13, 21, 0, 13, 21, 1),
        (13, 21, 1, 13, 21, 0),
        (15,  0, 0, 15,  0, 1),
        (16,  0, 0, 16,  0, 1),
        (16, 21, 0, 16, 21, 1),
        (16, 21, 1, 16, 21, 0),
        (17,  0, 0, 17,  0, 1),
        (17, 21, 0, 17, 21, 1),
        (18,  0, 0, 18,  0, 1),
        (18,  0, 1, 18,  0, 0),
        (18, 21, 0, 18, 21, 1),
        (18, 21, 1, 18, 21, 0),
        (19,  0, 0, 19,  0, 1),
        (19,  0, 1, 19,  0, 0),
        (19, 21, 0, 19, 21, 1),
        (19, 21, 1, 19, 21, 0),
        (21,  0, 1, 21,  0, 0),
        (22,  0, 1, 22,  0, 0),
        (23,  0, 0, 23,  0, 1),
        (23,  0, 1, 23,  0, 0),
        (24,  0, 0, 24,  0, 1),
        (24,  0, 1, 24,  0, 0)
    ]
}

# This dictionary maps package variants to a table of pin names and their
# corresponding grid location (x, y, block). This is most easily found through
# the package view in iCEcube2 by hovering the mouse over each pin.
pinloc_db = {
    "1k-swg16tr": [
        ( "A2",  6, 17, 1),
        ( "A4",  2, 17, 0),
        ( "B1", 11, 17, 1),
        ( "B2",  0,  8, 1),
        ( "B3",  0,  9, 0),
        ( "C1", 12,  0, 0),
        ( "C2", 11,  0, 1),
        ( "C3", 11,  0, 0),
        ( "D1", 12,  0, 1),
        ( "D3",  6,  0, 1),
    ],
    "1k-cm36": [
        ( "A1",  0, 13, 0),
        ( "A2",  4, 17, 1),
        ( "A3",  7, 17, 0),
        ( "B1",  0, 13, 1),
        ( "B3",  6, 17, 1),
        ( "B4", 13,  9, 0),
        ( "B5", 13, 11, 0),
        ( "B6", 13, 11, 1),
        ( "C1",  0,  9, 0),
        ( "C2",  0,  9, 1),
        ( "C3",  4, 17, 0),
        ( "C5", 13,  8, 1),
        ( "C6", 13, 12, 0),
        ( "D1",  0,  8, 1),
        ( "D5", 12,  0, 1),
        ( "D6", 13,  6, 0),
        ( "E1",  0,  8, 0),
        ( "E2",  6,  0, 0),
        ( "E3", 10,  0, 0),
        ( "E4", 11,  0, 0),
        ( "E5", 12,  0, 0),
        ( "E6", 13,  4, 1),
        ( "F2",  6,  0, 1),
        ( "F3", 10,  0, 1),
        ( "F5", 11,  0, 1),
    ],
    "1k-cm49": [
        ( "A1",  0, 11, 1),
        ( "A2",  3, 17, 1),
        ( "A3",  8, 17, 1),
        ( "A4",  8, 17, 0),
        ( "A5",  9, 17, 1),
        ( "A6", 10, 17, 0),
        ( "A7",  9, 17, 0),
        ( "B1",  0, 11, 0),
        ( "B2",  0, 13, 0),
        ( "B3",  4, 17, 0),
        ( "B4",  6, 17, 1),
        ( "C1",  0,  5, 0),
        ( "C2",  0, 13, 1),
        ( "C4",  7, 17, 0),
        ( "C5", 13, 12, 0),
        ( "C6", 13, 11, 1),
        ( "C7", 13, 11, 0),
        ( "D1",  0,  5, 1),
        ( "D2",  0,  9, 0),
        ( "D3",  0,  9, 1),
        ( "D4",  4, 17, 1),
        ( "D6", 13,  8, 1),
        ( "D7", 13,  9, 0),
        ( "E2",  0,  8, 1),
        ( "E6", 12,  0, 1),
        ( "E7", 13,  4, 1),
        ( "F2",  0,  8, 0),
        ( "F3",  6,  0, 0),
        ( "F4", 10,  0, 0),
        ( "F5", 11,  0, 0),
        ( "F6", 12,  0, 0),
        ( "F7", 13,  6, 0),
        ( "G3",  6,  0, 1),
        ( "G4", 10,  0, 1),
        ( "G6", 11,  0, 1),
    ],
    "1k-cm81": [
        ( "A1",  1, 17, 1),
        ( "A2",  4, 17, 0),
        ( "A3",  5, 17, 0),
        ( "A4",  6, 17, 0),
        ( "A6",  8, 17, 1),
        ( "A7",  9, 17, 0),
        ( "A8", 10, 17, 0),
        ( "A9", 13, 14, 1),
        ( "B1",  0, 13, 0),
        ( "B2",  0, 14, 0),
        ( "B3",  2, 17, 1),
        ( "B4",  4, 17, 1),
        ( "B5",  8, 17, 0),
        ( "B6",  9, 17, 1),
        ( "B7", 10, 17, 1),
        ( "B8", 11, 17, 0),
        ( "B9", 13, 11, 1),
        ( "C1",  0, 13, 1),
        ( "C2",  0, 14, 1),
        ( "C3",  0, 12, 1),
        ( "C4",  6, 17, 1),
        ( "C5",  7, 17, 0),
        ( "C9", 13, 12, 0),
        ( "D1",  0, 11, 1),
        ( "D2",  0, 12, 0),
        ( "D3",  0,  9, 0),
        ( "D5",  3, 17, 1),
        ( "D6", 13,  6, 0),
        ( "D7", 13,  7, 0),
        ( "D8", 13,  9, 0),
        ( "D9", 13, 11, 0),
        ( "E1",  0, 10, 1),
        ( "E2",  0, 10, 0),
        ( "E3",  0,  8, 1),
        ( "E4",  0, 11, 0),
        ( "E5",  5, 17, 1),
        ( "E7", 13,  6, 1),
        ( "E8", 13,  8, 1),
        ( "F1",  0,  8, 0),
        ( "F3",  0,  9, 1),
        ( "F7", 12,  0, 1),
        ( "F8", 13,  4, 0),
        ( "G1",  0,  5, 1),
        ( "G3",  0,  5, 0),
        ( "G4",  6,  0, 0),
        ( "G5", 10,  0, 0),
        ( "G6", 11,  0, 0),
        ( "G7", 12,  0, 0),
        ( "G8", 13,  4, 1),
        ( "G9", 13,  2, 1),
        ( "H1",  2,  0, 0),
        ( "H4",  6,  0, 1),
        ( "H5", 10,  0, 1),
        ( "H7", 11,  0, 1),
        ( "H9", 13,  2, 0),
        ( "J1",  3,  0, 0),
        ( "J2",  2,  0, 1),
        ( "J3",  3,  0, 1),
        ( "J4",  5,  0, 0),
        ( "J6",  7,  0, 0),
        ( "J7",  9,  0, 1),
        ( "J8", 13,  1, 0),
        ( "J9", 13,  1, 1),
    ],
    "1k-cm121": [
        ( "A1",  0, 14, 0),
        ( "A2",  2, 17, 1),
        ( "A3",  3, 17, 0),
        ( "A5",  5, 17, 1),
        ( "A7",  8, 17, 0),
        ( "A8", 10, 17, 1),
        ( "A9", 11, 17, 0),
        ("A10", 12, 17, 0),
        ("A11", 13, 15, 0),
        ( "B1",  0, 13, 0),
        ( "B2",  1, 17, 1),
        ( "B3",  2, 17, 0),
        ( "B4",  3, 17, 1),
        ( "B5",  4, 17, 1),
        ( "B7",  9, 17, 0),
        ( "B8", 11, 17, 1),
        ( "B9", 12, 17, 1),
        ("B10", 13, 15, 1),
        ("B11", 13, 14, 1),
        ( "C1",  0, 12, 0),
        ( "C2",  0, 13, 1),
        ( "C3",  0, 14, 1),
        ( "C4",  1, 17, 0),
        ( "C5",  4, 17, 0),
        ( "C6",  7, 17, 1),
        ( "C7",  8, 17, 1),
        ( "C8",  9, 17, 1),
        ( "C9", 10, 17, 0),
        ("C10", 13, 14, 0),
        ("C11", 13, 13, 1),
        ( "D1",  0, 11, 0),
        ( "D2",  0, 12, 1),
        ( "D3",  0, 11, 1),
        ( "D4",  0, 10, 1),
        ( "D5",  6, 17, 1),
        ( "D6",  7, 17, 0),
        ("D10", 13, 12, 1),
        ("D11", 13, 11, 1),
        ( "E2",  0, 10, 0),
        ( "E3",  0,  9, 1),
        ( "E4",  0,  9, 0),
        ( "E6",  5, 17, 0),
        ( "E7", 13, 12, 0),
        ( "E8", 13, 13, 0),
        ( "E9", 13,  9, 0),
        ("E10", 13,  9, 1),
        ( "F2",  0,  6, 0),
        ( "F3",  0,  5, 0),
        ( "F4",  0,  8, 1),
        ( "F5",  0,  8, 0),
        ( "F6",  6, 17, 0),
        ( "F8", 13, 11, 0),
        ( "F9", 13,  8, 1),
        ("F11", 13,  7, 1),
        ( "G2",  0,  5, 1),
        ( "G4",  0,  3, 0),
        ( "G8", 12,  0, 1),
        ( "G9", 13,  8, 0),
        ("G11", 13,  7, 0),
        ( "H1",  0,  6, 1),
        ( "H2",  0,  4, 1),
        ( "H4",  0,  2, 0),
        ( "H5",  6,  0, 0),
        ( "H6", 10,  0, 0),
        ( "H7", 11,  0, 0),
        ( "H8", 12,  0, 0),
        ( "H9", 13,  6, 1),
        ("H10", 13,  2, 1),
        ("H11", 13,  4, 1),
        ( "J1",  0,  4, 0),
        ( "J2",  1,  0, 1),
        ( "J5",  6,  0, 1),
        ( "J6", 10,  0, 1),
        ( "J8", 11,  0, 1),
        ("J10", 13,  2, 0),
        ("J11", 13,  6, 0),
        ( "K1",  0,  3, 1),
        ( "K2",  2,  0, 0),
        ( "K3",  2,  0, 1),
        ( "K4",  4,  0, 0),
        ( "K5",  5,  0, 0),
        ( "K7",  7,  0, 1),
        ( "K8",  9,  0, 0),
        ( "K9", 13,  1, 0),
        ("K10", 13,  1, 1),
        ("K11", 13,  3, 1),
        ( "L1",  0,  2, 1),
        ( "L2",  3,  0, 0),
        ( "L3",  3,  0, 1),
        ( "L4",  4,  0, 1),
        ( "L5",  7,  0, 0),
        ( "L7",  8,  0, 0),
        ( "L9",  8,  0, 1),
        ("L10",  9,  0, 1),
        ("L11", 13,  4, 0),
    ],
    "1k-cb81": [
        ( "A2",  2, 17, 1),
        ( "A3",  3, 17, 1),
        ( "A4",  6, 17, 1),
        ( "A7", 11, 17, 0),
        ( "A8", 12, 17, 1),
        ( "B1",  0, 13, 1),
        ( "B2",  0, 14, 0),
        ( "B3",  0, 13, 0),
        ( "B4",  5, 17, 1),
        ( "B5",  8, 17, 1),
        ( "B6",  9, 17, 1),
        ( "B7", 11, 17, 1),
        ( "B8", 12, 17, 0),
        ( "C1",  0, 12, 0),
        ( "C2",  0, 10, 0),
        ( "C3",  0, 14, 1),
        ( "C4",  1, 17, 1),
        ( "C5",  8, 17, 0),
        ( "C6", 10, 17, 0),
        ( "C7", 13, 15, 0),
        ( "C8", 13, 15, 1),
        ( "C9", 13, 14, 1),
        ( "D1",  0,  9, 0),
        ( "D2",  0, 10, 1),
        ( "D3",  0, 12, 1),
        ( "D4",  5, 17, 0),
        ( "D5",  4, 17, 0),
        ( "D6",  7, 17, 0),
        ( "D7", 13, 13, 0),
        ( "D8", 13, 13, 1),
        ( "E1",  0,  8, 1),
        ( "E2",  0,  8, 0),
        ( "E3",  0,  9, 1),
        ( "E6", 10, 17, 1),
        ( "E7", 13, 12, 0),
        ( "E8", 13, 11, 0),
        ( "E9", 13, 11, 1),
        ( "F2",  0,  6, 1),
        ( "F3",  0,  6, 0),
        ( "F6", 13,  8, 0),
        ( "F7", 13,  9, 0),
        ( "F8", 13,  8, 1),
        ( "F9", 13,  7, 1),
        ( "G1",  0,  4, 1),
        ( "G2",  0,  2, 1),
        ( "G3",  3,  0, 1),
        ( "G4",  4,  0, 0),
        ( "G5", 10,  0, 0),
        ( "G6", 13,  4, 0),
        ( "G7", 13,  4, 1),
        ( "G8", 13,  6, 1),
        ( "G9", 13,  7, 0),
        ( "H2",  0,  4, 0),
        ( "H3",  2,  0, 1),
        ( "H4",  6,  0, 0),
        ( "H5", 10,  0, 1),
        ( "H7", 11,  0, 0),
        ( "H8", 12,  0, 1),
        ( "J2",  2,  0, 0),
        ( "J3",  6,  0, 1),
        ( "J7", 11,  0, 1),
        ( "J8", 12,  0, 0),
    ],
    "1k-cb121": [
        ( "A2",  1, 17, 1),
        ( "A3",  2, 17, 0),
        ( "A4",  4, 17, 0),
        ( "A5",  3, 17, 1),
        ( "A6",  4, 17, 1),
        ( "A8", 10, 17, 0),
        ("A10", 12, 17, 1),
        ("A11", 13, 15, 0),
        ( "B1",  0, 14, 0),
        ( "B3",  1, 17, 0),
        ( "B4",  2, 17, 1),
        ( "B5",  3, 17, 0),
        ( "B8", 10, 17, 1),
        ( "B9", 12, 17, 0),
        ("B11", 13, 15, 1),
        ( "C1",  0, 14, 1),
        ( "C2",  0, 11, 1),
        ( "C3",  0, 13, 1),
        ( "C4",  0, 13, 0),
        ( "C5",  5, 17, 0),
        ( "C6",  7, 17, 0),
        ( "C7",  8, 17, 1),
        ( "C8", 11, 17, 0),
        ( "C9", 11, 17, 1),
        ("C11", 13, 14, 1),
        ( "D1",  0, 10, 1),
        ( "D2",  0, 11, 0),
        ( "D3",  0,  9, 0),
        ( "D4",  0, 12, 0),
        ( "D5",  5, 17, 1),
        ( "D6",  6, 17, 1),
        ( "D7",  8, 17, 0),
        ( "D8", 13, 12, 0),
        ( "D9", 13, 13, 0),
        ("D10", 13, 13, 1),
        ("D11", 13, 14, 0),
        ( "E2",  0, 10, 0),
        ( "E3",  0,  9, 1),
        ( "E4",  0, 12, 1),
        ( "E5",  6, 17, 0),
        ( "E6",  7, 17, 1),
        ( "E7",  9, 17, 0),
        ( "E8", 13, 11, 0),
        ( "E9", 13, 11, 1),
        ("E11", 13, 12, 1),
        ( "F2",  0,  6, 1),
        ( "F3",  0,  5, 1),
        ( "F4",  0,  8, 1),
        ( "F7",  9, 17, 1),
        ( "F8", 13,  8, 1),
        ( "F9", 13,  9, 0),
        ("F10", 13,  9, 1),
        ( "G1",  0,  6, 0),
        ( "G3",  0,  5, 0),
        ( "G4",  0,  8, 0),
        ( "G7", 13,  6, 1),
        ( "G8", 13,  7, 0),
        ( "G9", 13,  7, 1),
        ("G10", 13,  8, 0),
        ( "H1",  0,  3, 1),
        ( "H2",  0,  4, 1),
        ( "H3",  0,  4, 0),
        ( "H4",  4,  0, 0),
        ( "H5",  4,  0, 1),
        ( "H6", 10,  0, 0),
        ( "H7", 13,  4, 1),
        ( "H8", 13,  6, 0),
        ( "H9", 13,  4, 0),
        ("H10", 13,  3, 1),
        ("H11",  9,  0, 1),
        ( "J1",  0,  3, 0),
        ( "J2",  0,  2, 0),
        ( "J3",  0,  2, 1),
        ( "J4",  2,  0, 1),
        ( "J5",  3,  0, 0),
        ( "J6", 10,  0, 1),
        ( "J8", 11,  0, 0),
        ( "J9", 12,  0, 1),
        ("J11",  8,  0, 1),
        ( "K3",  1,  0, 0),
        ( "K4",  1,  0, 1),
        ( "K8", 11,  0, 1),
        ( "K9", 12,  0, 0),
        ("K11",  9,  0, 0),
        ( "L2",  2,  0, 0),
        ( "L3",  3,  0, 1),
        ( "L4",  5,  0, 0),
        ( "L5",  5,  0, 1),
        ( "L8",  7,  0, 0),
        ( "L9",  6,  0, 1),
        ("L10",  7,  0, 1),
        ("L11",  8,  0, 0),
    ],
    "1k-cb132": [
        ( "A1",  1, 17, 1),
        ( "A2",  2, 17, 1),
        ( "A4",  4, 17, 0),
        ( "A5",  4, 17, 1),
        ( "A6",  6, 17, 1),
        ( "A7",  7, 17, 0),
        ("A10", 10, 17, 0),
        ("A12", 12, 17, 0),
        ( "B1",  0, 14, 1),
        ("B14", 13, 15, 0),
        ( "C1",  0, 14, 0),
        ( "C3",  0, 13, 1),
        ( "C4",  1, 17, 0),
        ( "C5",  3, 17, 0),
        ( "C6",  5, 17, 0),
        ( "C7",  6, 17, 0),
        ( "C8",  8, 17, 0),
        ( "C9",  9, 17, 0),
        ("C10", 11, 17, 0),
        ("C11", 11, 17, 1),
        ("C12", 12, 17, 1),
        ("C14", 13, 14, 0),
        ( "D1",  0, 11, 1),
        ( "D3",  0, 13, 0),
        ( "D4",  0, 12, 1),
        ( "D5",  2, 17, 0),
        ( "D6",  3, 17, 1),
        ( "D7",  5, 17, 1),
        ( "D8",  7, 17, 1),
        ( "D9",  8, 17, 1),
        ("D10",  9, 17, 1),
        ("D11", 10, 17, 1),
        ("D12", 13, 15, 1),
        ("D14", 13, 13, 1),
        ( "E1",  0, 11, 0),
        ( "E4",  0, 12, 0),
        ("E11", 13, 14, 1),
        ("E12", 13, 13, 0),
        ("E14", 13, 12, 0),
        ( "F3",  0, 10, 0),
        ( "F4",  0, 10, 1),
        ("F11", 13, 12, 1),
        ("F12", 13, 11, 1),
        ("F14", 13,  8, 1),
        ( "G1",  0,  8, 1),
        ( "G3",  0,  8, 0),
        ( "G4",  0,  6, 1),
        ("G11", 13, 11, 0),
        ("G12", 13,  9, 1),
        ("G14", 13,  9, 0),
        ( "H1",  0,  9, 0),
        ( "H3",  0,  9, 1),
        ( "H4",  0,  6, 0),
        ("H11", 13,  8, 0),
        ("H12", 13,  7, 1),
        ( "J1",  0,  5, 1),
        ( "J3",  0,  5, 0),
        ("J11", 13,  7, 0),
        ("J12", 13,  6, 1),
        ( "K3",  0,  3, 0),
        ( "K4",  0,  3, 1),
        ("K11", 13,  4, 1),
        ("K12", 13,  4, 0),
        ("K14", 13,  6, 0),
        ( "L1",  0,  2, 0),
        ( "L4",  1,  0, 1),
        ( "L5",  3,  0, 1),
        ( "L6",  4,  0, 1),
        ( "L7",  8,  0, 0),
        ( "L8",  9,  0, 0),
        ( "L9", 10,  0, 0),
        ("L12", 13,  2, 0),
        ("L14", 13,  3, 1),
        ( "M1",  0,  2, 1),
        ( "M3",  1,  0, 0),
        ( "M4",  3,  0, 0),
        ( "M6",  5,  0, 1),
        ( "M7",  6,  0, 0),
        ( "M8",  8,  0, 1),
        ( "M9",  9,  0, 1),
        ("M11", 11,  0, 0),
        ("M12", 13,  1, 0),
        ("N14", 13,  2, 1),
        ( "P2",  2,  0, 0),
        ( "P3",  2,  0, 1),
        ( "P4",  4,  0, 0),
        ( "P5",  5,  0, 0),
        ( "P7",  6,  0, 1),
        ( "P8",  7,  0, 0),
        ( "P9",  7,  0, 1),
        ("P10", 10,  0, 1),
        ("P11", 11,  0, 1),
        ("P12", 12,  0, 0),
        ("P13", 12,  0, 1),
        ("P14", 13,  1, 1),
    ],
    "1k-qn84": [
        ( "A1",  0, 14, 0),
        ( "A2",  0, 13, 0),
        ( "A3",  0, 12, 0),
        ( "A4",  0, 11, 0),
        ( "A5",  0, 10, 0),
        ( "A8",  0,  9, 0),
        ( "A9",  0,  8, 1),
        ("A10",  0,  5, 1),
        ("A11",  0,  4, 0),
        ("A12",  0,  2, 0),
        ("A13",  4,  0, 0),
        ("A14",  6,  0, 1),
        ("A16",  6,  0, 0),
        ("A19",  9,  0, 1),
        ("A20", 10,  0, 1),
        ("A22", 11,  0, 1),
        ("A23", 12,  0, 0),
        ("A25", 13,  4, 0),
        ("A26", 13,  6, 0),
        ("A27", 13,  7, 1),
        ("A29", 13,  8, 1),
        ("A31", 13, 11, 1),
        ("A32", 13, 12, 1),
        ("A33", 13, 13, 1),
        ("A34", 13, 14, 0),
        ("A35", 13, 15, 0),
        ("A38", 11, 17, 0),
        ("A39", 10, 17, 0),
        ("A40",  9, 17, 0),
        ("A41",  8, 17, 0),
        ("A43",  7, 17, 0),
        ("A44",  6, 17, 0),
        ("A45",  5, 17, 0),
        ("A46",  4, 17, 0),
        ("A47",  3, 17, 0),
        ("A48",  1, 17, 1),
        ( "B1",  0, 13, 1),
        ( "B2",  0, 12, 1),
        ( "B3",  0, 11, 1),
        ( "B4",  0, 10, 1),
        ( "B5",  0,  9, 1),
        ( "B7",  0,  8, 0),
        ( "B8",  0,  5, 0),
        ( "B9",  0,  3, 0),
        ("B10",  5,  0, 0),
        ("B11",  5,  0, 1),
        ("B12",  7,  0, 0),
        ("B13",  8,  0, 0),
        ("B14",  9,  0, 0),
        ("B15", 10,  0, 0),
        ("B17", 11,  0, 0),
        ("B18", 12,  0, 1),
        ("B19", 13,  3, 1),
        ("B20", 13,  6, 1),
        ("B21", 13,  7, 0),
        ("B22", 13,  9, 0),
        ("B23", 13, 11, 0),
        ("B24", 13, 12, 0),
        ("B26", 13, 14, 1),
        ("B27", 13, 15, 1),
        ("B29", 10, 17, 1),
        ("B30",  9, 17, 1),
        ("B31",  8, 17, 1),
        ("B32",  6, 17, 1),
        ("B34",  4, 17, 1),
        ("B35",  3, 17, 1),
        ("B36",  2, 17, 1),
    ],
    "1k-tq144": [
        (  "1",  0, 14, 1),
        (  "2",  0, 14, 0),
        (  "3",  0, 13, 1),
        (  "4",  0, 13, 0),
        (  "7",  0, 12, 1),
        (  "8",  0, 12, 0),
        (  "9",  0, 11, 1),
        ( "10",  0, 11, 0),
        ( "11",  0, 10, 1),
        ( "12",  0, 10, 0),
        ( "19",  0,  9, 1),
        ( "20",  0,  9, 0),
        ( "21",  0,  8, 1),
        ( "22",  0,  8, 0),
        ( "23",  0,  6, 1),
        ( "24",  0,  6, 0),
        ( "25",  0,  5, 1),
        ( "26",  0,  5, 0),
        ( "28",  0,  4, 1),
        ( "29",  0,  4, 0),
        ( "31",  0,  3, 1),
        ( "32",  0,  3, 0),
        ( "33",  0,  2, 1),
        ( "34",  0,  2, 0),
        ( "37",  1,  0, 0),
        ( "38",  1,  0, 1),
        ( "39",  2,  0, 0),
        ( "41",  2,  0, 1),
        ( "42",  3,  0, 0),
        ( "43",  3,  0, 1),
        ( "44",  4,  0, 0),
        ( "45",  4,  0, 1),
        ( "47",  5,  0, 0),
        ( "48",  5,  0, 1),
        ( "49",  6,  0, 1),
        ( "50",  7,  0, 0),
        ( "52",  6,  0, 0),
        ( "56",  7,  0, 1),
        ( "58",  8,  0, 0),
        ( "60",  8,  0, 1),
        ( "61",  9,  0, 0),
        ( "62",  9,  0, 1),
        ( "63", 10,  0, 0),
        ( "64", 10,  0, 1),
        ( "67", 11,  0, 0),
        ( "68", 11,  0, 1),
        ( "70", 12,  0, 0),
        ( "71", 12,  0, 1),
        ( "73", 13,  1, 0),
        ( "74", 13,  1, 1),
        ( "75", 13,  2, 0),
        ( "76", 13,  2, 1),
        ( "78", 13,  3, 1),
        ( "79", 13,  4, 0),
        ( "80", 13,  4, 1),
        ( "81", 13,  6, 0),
        ( "87", 13,  6, 1),
        ( "88", 13,  7, 0),
        ( "90", 13,  7, 1),
        ( "91", 13,  8, 0),
        ( "93", 13,  8, 1),
        ( "94", 13,  9, 0),
        ( "95", 13,  9, 1),
        ( "96", 13, 11, 0),
        ( "97", 13, 11, 1),
        ( "98", 13, 12, 0),
        ( "99", 13, 12, 1),
        ("101", 13, 13, 0),
        ("102", 13, 13, 1),
        ("104", 13, 14, 0),
        ("105", 13, 14, 1),
        ("106", 13, 15, 0),
        ("107", 13, 15, 1),
        ("112", 12, 17, 1),
        ("113", 12, 17, 0),
        ("114", 11, 17, 1),
        ("115", 11, 17, 0),
        ("116", 10, 17, 1),
        ("117", 10, 17, 0),
        ("118",  9, 17, 1),
        ("119",  9, 17, 0),
        ("120",  8, 17, 1),
        ("121",  8, 17, 0),
        ("122",  7, 17, 1),
        ("128",  7, 17, 0),
        ("129",  6, 17, 1),
        ("134",  5, 17, 1),
        ("135",  5, 17, 0),
        ("136",  4, 17, 1),
        ("137",  4, 17, 0),
        ("138",  3, 17, 1),
        ("139",  3, 17, 0),
        ("141",  2, 17, 1),
        ("142",  2, 17, 0),
        ("143",  1, 17, 1),
        ("144",  1, 17, 0),
    ],
    "1k-vq100": [
        (  "1",  0, 14, 1),
        (  "2",  0, 14, 0),
        (  "3",  0, 13, 1),
        (  "4",  0, 13, 0),
        (  "7",  0, 12, 1),
        (  "8",  0, 12, 0),
        (  "9",  0, 10, 1),
        ( "10",  0, 10, 0),
        ( "12",  0,  9, 1),
        ( "13",  0,  9, 0),
        ( "15",  0,  8, 1),
        ( "16",  0,  8, 0),
        ( "18",  0,  6, 1),
        ( "19",  0,  6, 0),
        ( "20",  0,  4, 1),
        ( "21",  0,  4, 0),
        ( "24",  0,  2, 1),
        ( "25",  0,  2, 0),
        ( "26",  2,  0, 0),
        ( "27",  2,  0, 1),
        ( "28",  3,  0, 0),
        ( "29",  3,  0, 1),
        ( "30",  4,  0, 0),
        ( "33",  6,  0, 1),
        ( "34",  7,  0, 0),
        ( "36",  6,  0, 0),
        ( "37",  7,  0, 1),
        ( "40",  9,  0, 1),
        ( "41", 10,  0, 0),
        ( "42", 10,  0, 1),
        ( "45", 11,  0, 0),
        ( "46", 11,  0, 1),
        ( "48", 12,  0, 0),
        ( "49", 12,  0, 1),
        ( "51", 13,  3, 1),
        ( "52", 13,  4, 0),
        ( "53", 13,  4, 1),
        ( "54", 13,  6, 0),
        ( "56", 13,  6, 1),
        ( "57", 13,  7, 0),
        ( "59", 13,  7, 1),
        ( "60", 13,  8, 0),
        ( "62", 13,  8, 1),
        ( "63", 13,  9, 0),
        ( "64", 13, 11, 0),
        ( "65", 13, 11, 1),
        ( "66", 13, 12, 0),
        ( "68", 13, 13, 0),
        ( "69", 13, 13, 1),
        ( "71", 13, 14, 0),
        ( "72", 13, 14, 1),
        ( "73", 13, 15, 0),
        ( "74", 13, 15, 1),
        ( "78", 12, 17, 1),
        ( "79", 12, 17, 0),
        ( "80", 11, 17, 1),
        ( "81", 10, 17, 1),
        ( "82", 10, 17, 0),
        ( "83",  9, 17, 1),
        ( "85",  9, 17, 0),
        ( "86",  8, 17, 1),
        ( "87",  8, 17, 0),
        ( "89",  7, 17, 0),
        ( "90",  6, 17, 1),
        ( "91",  6, 17, 0),
        ( "93",  5, 17, 1),
        ( "94",  5, 17, 0),
        ( "95",  4, 17, 1),
        ( "96",  4, 17, 0),
        ( "97",  3, 17, 1),
        ( "99",  2, 17, 1),
        ("100",  1, 17, 1),
    ],
    "8k-cb132:4k": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 0),
        ( "A3",  3, 33, 1),
        ( "A4",  5, 33, 0),
        ( "A5", 10, 33, 1),
        ( "A6", 16, 33, 1),
        ( "A7", 17, 33, 0),
        ("A10", 25, 33, 0),
        ("A11", 26, 33, 0),
        ("A12", 30, 33, 1),
        ( "B1",  0, 30, 1),
        ("B14", 33, 28, 0),
        ( "C1",  0, 30, 0),
        ( "C3",  0, 27, 1),
        ( "C4",  4, 33, 0),
        ( "C5",  8, 33, 1),
        ( "C6", 11, 33, 1),
        ( "C7", 14, 33, 1),
        ( "C9", 20, 33, 1),
        ("C10", 22, 33, 1),
        ("C11", 28, 33, 1),
        ("C12", 29, 33, 1),
        ("C14", 33, 24, 1),
        ( "D1",  0, 25, 1),
        ( "D3",  0, 27, 0),
        ( "D4",  0, 22, 1),
        ( "D5",  9, 33, 0),
        ( "D6", 11, 33, 0),
        ( "D7", 13, 33, 1),
        ( "D9", 21, 33, 1),
        ("D10", 27, 33, 0),
        ("D11", 26, 33, 1),
        ("D12", 33, 27, 1),
        ("D14", 33, 23, 1),
        ( "E1",  0, 25, 0),
        ( "E4",  0, 22, 0),
        ("E11", 33, 20, 1),
        ("E12", 33, 21, 0),
        ("E14", 33, 21, 1),
        ( "F3",  0, 21, 0),
        ( "F4",  0, 21, 1),
        ("F11", 33, 19, 1),
        ("F12", 33, 15, 0),
        ("F14", 33, 16, 1),
        ( "G1",  0, 17, 0),
        ( "G3",  0, 17, 1),
        ( "G4",  0, 20, 0),
        ("G11", 33, 14, 1),
        ("G12", 33, 11, 0),
        ("G14", 33, 17, 0),
        ( "H1",  0, 16, 1),
        ( "H3",  0, 16, 0),
        ( "H4",  0, 20, 1),
        ("H11", 33, 10, 1),
        ("H12", 33,  6, 1),
        ( "J1",  0, 18, 0),
        ( "J3",  0, 18, 1),
        ("J11", 33,  6, 0),
        ("J12", 33,  5, 1),
        ( "K3",  0, 11, 1),
        ( "K4",  0, 11, 0),
        ("K11", 33,  4, 1),
        ("K12", 33,  4, 0),
        ("K14", 33,  5, 0),
        ( "L1",  0,  6, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 11,  0, 1),
        ( "L6", 15,  0, 0),
        ( "L8", 20,  0, 1),
        ( "L9", 29,  0, 0),
        ("L12", 33,  2, 0),
        ("L14", 33,  3, 1),
        ( "M1",  0,  6, 0),
        ( "M3",  8,  0, 0),
        ( "M4",  7,  0, 1),
        ( "M6", 14,  0, 1),
        ( "M7", 15,  0, 1),
        ( "M9", 22,  0, 1),
        ("M11", 30,  0, 0),
        ("M12", 33,  1, 0),
        ( "N1",  0,  4, 1),
        ("N14", 33,  2, 1),
        ( "P1",  0,  4, 0),
        ( "P2",  4,  0, 0),
        ( "P3",  5,  0, 1),
        ( "P4", 12,  0, 1),
        ( "P5", 13,  0, 0),
        ( "P7", 16,  0, 1),
        ( "P8", 17,  0, 0),
        ( "P9", 21,  0, 1),
        ("P10", 29,  0, 1),
        ("P11", 30,  0, 1),
        ("P12", 31,  0, 0),
        ("P13", 31,  0, 1),
        ("P14", 33,  1, 1),
    ],
    "8k-tq144:4k": [
        (  "1",  0, 30, 1),
        (  "2",  0, 30, 0),
        (  "3",  0, 28, 1),
        (  "4",  0, 28, 0),
        (  "7",  0, 27, 1),
        (  "8",  0, 27, 0),
        (  "9",  0, 25, 1),
        ( "10",  0, 25, 0),
        ( "11",  0, 22, 1),
        ( "12",  0, 22, 0),
        ( "15",  0, 20, 1),
        ( "16",  0, 20, 0),
        ( "17",  0, 18, 1),
        ( "18",  0, 18, 0),
        ( "19",  0, 17, 1),
        ( "20",  0, 17, 0),
        ( "21",  0, 16, 1),
        ( "22",  0, 16, 0),
        ( "23",  0, 12, 1),
        ( "24",  0, 12, 0),
        ( "25",  0, 11, 1),
        ( "26",  0, 11, 0),
        ( "28",  0,  6, 1),
        ( "29",  0,  6, 0),
        ( "31",  0,  5, 1),
        ( "32",  0,  5, 0),
        ( "33",  0,  4, 1),
        ( "34",  0,  4, 0),
        ( "37",  4,  0, 0),
        ( "38",  4,  0, 1),
        ( "39",  6,  0, 1),
        ( "41",  7,  0, 1),
        ( "42",  8,  0, 0),
        ( "43", 11,  0, 1),
        ( "44", 12,  0, 0),
        ( "45", 12,  0, 1),
        ( "47", 15,  0, 1),
        ( "48", 16,  0, 0),
        ( "49", 16,  0, 1),
        ( "52", 17,  0, 0),
        ( "55", 22,  0, 1),
        ( "56", 24,  0, 0),
        ( "60", 24,  0, 1),
        ( "61", 25,  0, 0),
        ( "62", 28,  0, 0),
        ( "63", 29,  0, 0),
        ( "64", 29,  0, 1),
        ( "67", 30,  0, 0),
        ( "68", 30,  0, 1),
        ( "70", 31,  0, 0),
        ( "71", 31,  0, 1),
        ( "73", 33,  1, 0),
        ( "74", 33,  1, 1),
        ( "75", 33,  2, 0),
        ( "76", 33,  2, 1),
        ( "78", 33,  3, 1),
        ( "79", 33,  4, 0),
        ( "80", 33,  4, 1),
        ( "81", 33,  5, 0),
        ( "82", 33,  5, 1),
        ( "83", 33,  6, 0),
        ( "84", 33,  6, 1),
        ( "85", 33, 10, 1),
        ( "87", 33, 14, 1),
        ( "88", 33, 15, 0),
        ( "90", 33, 15, 1),
        ( "91", 33, 16, 0),
        ( "93", 33, 16, 1),
        ( "94", 33, 17, 0),
        ( "95", 33, 19, 1),
        ( "96", 33, 20, 1),
        ( "97", 33, 21, 0),
        ( "98", 33, 21, 1),
        ( "99", 33, 23, 1),
        ("101", 33, 27, 1),
        ("102", 33, 28, 0),
        ("104", 33, 29, 1),
        ("105", 33, 30, 0),
        ("106", 33, 30, 1),
        ("107", 33, 31, 0),
        ("110", 31, 33, 1),
        ("112", 31, 33, 0),
        ("113", 30, 33, 1),
        ("114", 30, 33, 0),
        ("115", 29, 33, 1),
        ("116", 29, 33, 0),
        ("117", 28, 33, 1),
        ("118", 27, 33, 0),
        ("119", 26, 33, 1),
        ("120", 26, 33, 0),
        ("121", 25, 33, 0),
        ("122", 20, 33, 1),
        ("124", 20, 33, 0),
        ("125", 19, 33, 1),
        ("128", 17, 33, 0),
        ("129", 16, 33, 1),
        ("130", 11, 33, 1),
        ("134",  8, 33, 1),
        ("135",  8, 33, 0),
        ("136",  7, 33, 1),
        ("137",  7, 33, 0),
        ("138",  6, 33, 1),
        ("139",  6, 33, 0),
        ("141",  5, 33, 0),
        ("142",  4, 33, 1),
        ("143",  4, 33, 0),
        ("144",  3, 33, 1),
    ],
    "8k-cm81:4k": [
        ( "A1",  2, 33, 1),
        ( "A2",  4, 33, 0),
        ( "A3",  6, 33, 0),
        ( "A4", 10, 33, 1),
        ( "A6", 23, 33, 0),
        ( "A7", 27, 33, 0),
        ( "A8", 28, 33, 1),
        ( "A9", 33,  4, 1),
        ( "B1",  0, 28, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  5, 33, 1),
        ( "B4",  9, 33, 0),
        ( "B5", 21, 33, 1),
        ( "B6", 24, 33, 0),
        ( "B7", 25, 33, 1),
        ( "B8", 30, 33, 1),
        ( "B9", 33,  6, 1),
        ( "C1",  0, 28, 0),
        ( "C2",  0, 30, 1),
        ( "C3",  0, 23, 0),
        ( "C4", 16, 33, 1),
        ( "C5", 17, 33, 0),
        ( "C9", 33, 21, 1),
        ( "D1",  0, 20, 1),
        ( "D2",  0, 23, 1),
        ( "D3",  0, 17, 0),
        ( "D5",  8, 33, 1),
        ( "D6", 33,  4, 0),
        ( "D7", 33,  5, 0),
        ( "D8", 33, 17, 0),
        ( "D9", 33,  6, 0),
        ( "E1",  0, 20, 0),
        ( "E2",  0, 17, 1),
        ( "E3",  0, 16, 1),
        ( "E4",  0, 16, 0),
        ( "E5",  7, 33, 1),
        ( "E7", 33,  5, 1),
        ( "E8", 33, 16, 1),
        ( "F1",  0,  7, 1),
        ( "F3",  0,  7, 0),
        ( "F7", 31,  0, 1),
        ( "F8", 33,  3, 0),
        ( "G1",  0,  5, 0),
        ( "G2",  0,  3, 1),
        ( "G3",  0,  5, 1),
        ( "G4", 16,  0, 1),
        ( "G5", 29,  0, 0),
        ( "G6", 30,  0, 0),
        ( "G7", 31,  0, 0),
        ( "G8", 33,  3, 1),
        ( "G9", 33,  2, 1),
        ( "H1",  3,  0, 0),
        ( "H2",  0,  3, 0),
        ( "H4", 17,  0, 0),
        ( "H5", 29,  0, 1),
        ( "H7", 30,  0, 1),
        ( "H9", 33,  2, 0),
        ( "J1",  3,  0, 1),
        ( "J2",  4,  0, 0),
        ( "J3",  4,  0, 1),
        ( "J4", 11,  0, 0),
        ( "J8", 33,  1, 0),
        ( "J9", 33,  1, 1),
    ],
    "8k-cm121:4k": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 1),
        ( "A3",  3, 33, 0),
        ( "A4",  9, 33, 0),
        ( "A5", 11, 33, 0),
        ( "A6", 11, 33, 1),
        ( "A7", 19, 33, 1),
        ( "A8", 20, 33, 1),
        ( "A9", 26, 33, 1),
        ("A10", 30, 33, 1),
        ("A11", 31, 33, 1),
        ( "B1",  0, 30, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  4, 33, 0),
        ( "B4",  5, 33, 0),
        ( "B5", 10, 33, 1),
        ( "B6", 16, 33, 1),
        ( "B7", 17, 33, 0),
        ( "B8", 27, 33, 0),
        ( "B9", 28, 33, 1),
        ("B11", 33, 28, 0),
        ( "C1",  0, 25, 0),
        ( "C2",  0, 25, 1),
        ( "C3",  0, 27, 0),
        ( "C4",  0, 27, 1),
        ( "C7", 20, 33, 0),
        ( "C8", 26, 33, 0),
        ( "C9", 29, 33, 1),
        ("C11", 33, 27, 1),
        ( "D1",  0, 22, 0),
        ( "D2",  0, 21, 1),
        ( "D3",  0, 21, 0),
        ( "D5",  8, 33, 1),
        ( "D7", 25, 33, 0),
        ( "D9", 33, 21, 0),
        ("D10", 33, 24, 1),
        ("D11", 33, 23, 1),
        ( "E1",  0, 22, 1),
        ( "E2",  0, 20, 1),
        ( "E3",  0, 20, 0),
        ( "E8", 33, 20, 1),
        ( "E9", 33, 19, 1),
        ("E10", 33, 17, 0),
        ("E11", 33, 21, 1),
        ( "F1",  0, 18, 1),
        ( "F2",  0, 18, 0),
        ( "F3",  0, 17, 0),
        ( "F4",  0, 17, 1),
        ( "F9", 33, 15, 0),
        ("F10", 33, 14, 1),
        ("F11", 33, 16, 1),
        ( "G1",  0, 16, 1),
        ( "G2",  0, 16, 0),
        ( "G3",  0, 12, 1),
        ( "G8", 33,  5, 1),
        ( "G9", 33, 10, 1),
        ("G10", 33,  6, 1),
        ("G11", 33, 11, 0),
        ( "H1",  0, 11, 1),
        ( "H2",  0, 11, 0),
        ( "H3",  0, 12, 0),
        ( "H7", 20,  0, 1),
        ( "H9", 29,  0, 1),
        ("H10", 33,  4, 1),
        ("H11", 33,  6, 0),
        ( "J1",  0,  6, 1),
        ( "J2",  0,  4, 0),
        ( "J3",  4,  0, 1),
        ( "J4",  8,  0, 0),
        ( "J5", 15,  0, 0),
        ( "J7", 20,  0, 0),
        ( "J8", 22,  0, 1),
        ( "J9", 30,  0, 1),
        ("J10", 33,  5, 0),
        ("J11", 33,  3, 1),
        ( "K1",  0,  6, 0),
        ( "K2",  0,  4, 1),
        ( "K3",  7,  0, 1),
        ( "K4", 12,  0, 1),
        ( "K5", 15,  0, 1),
        ( "K6", 17,  0, 0),
        ( "K7", 21,  0, 1),
        ( "K9", 30,  0, 0),
        ("K10", 31,  0, 1),
        ("K11", 33,  4, 0),
        ( "L1",  4,  0, 0),
        ( "L2",  6,  0, 1),
        ( "L3", 11,  0, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 16,  0, 1),
        ( "L7", 24,  0, 0),
        ( "L8", 29,  0, 0),
        ("L10", 31,  0, 0),
    ],
	"8k-bg121:4k": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 1),
        ( "A3",  3, 33, 0),
        ( "A4",  9, 33, 0),
        ( "A5", 11, 33, 0),
        ( "A6", 11, 33, 1),
        ( "A7", 19, 33, 1),
        ( "A8", 20, 33, 1),
        ( "A9", 26, 33, 1),
        ("A10", 30, 33, 1),
        ("A11", 31, 33, 1),
        ( "B1",  0, 30, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  4, 33, 0),
        ( "B4",  5, 33, 0),
        ( "B5", 10, 33, 1),
        ( "B6", 16, 33, 1),
        ( "B7", 17, 33, 0),
        ( "B8", 27, 33, 0),
        ( "B9", 28, 33, 1),
        ("B11", 33, 28, 0),
        ( "C1",  0, 25, 0),
        ( "C2",  0, 25, 1),
        ( "C3",  0, 27, 0),
        ( "C4",  0, 27, 1),
        ( "C7", 20, 33, 0),
        ( "C8", 26, 33, 0),
        ( "C9", 29, 33, 1),
        ("C11", 33, 27, 1),
        ( "D1",  0, 22, 0),
        ( "D2",  0, 21, 1),
        ( "D3",  0, 21, 0),
        ( "D5",  8, 33, 1),
        ( "D7", 25, 33, 0),
        ( "D9", 33, 21, 0),
        ("D10", 33, 24, 1),
        ("D11", 33, 23, 1),
        ( "E1",  0, 22, 1),
        ( "E2",  0, 20, 1),
        ( "E3",  0, 20, 0),
        ( "E8", 33, 20, 1),
        ( "E9", 33, 19, 1),
        ("E10", 33, 17, 0),
        ("E11", 33, 21, 1),
        ( "F1",  0, 18, 1),
        ( "F2",  0, 18, 0),
        ( "F3",  0, 17, 0),
        ( "F4",  0, 17, 1),
        ( "F9", 33, 15, 0),
        ("F10", 33, 14, 1),
        ("F11", 33, 16, 1),
        ( "G1",  0, 16, 1),
        ( "G2",  0, 16, 0),
        ( "G3",  0, 12, 1),
        ( "G8", 33,  5, 1),
        ( "G9", 33, 10, 1),
        ("G10", 33,  6, 1),
        ("G11", 33, 11, 0),
        ( "H1",  0, 11, 1),
        ( "H2",  0, 11, 0),
        ( "H3",  0, 12, 0),
        ( "H7", 20,  0, 1),
        ( "H9", 29,  0, 1),
        ("H10", 33,  4, 1),
        ("H11", 33,  6, 0),
        ( "J1",  0,  6, 1),
        ( "J2",  0,  4, 0),
        ( "J3",  4,  0, 1),
        ( "J4",  8,  0, 0),
        ( "J5", 15,  0, 0),
        ( "J7", 20,  0, 0),
        ( "J8", 22,  0, 1),
        ( "J9", 30,  0, 1),
        ("J10", 33,  5, 0),
        ("J11", 33,  3, 1),
        ( "K1",  0,  6, 0),
        ( "K2",  0,  4, 1),
        ( "K3",  7,  0, 1),
        ( "K4", 12,  0, 1),
        ( "K5", 15,  0, 1),
        ( "K6", 17,  0, 0),
        ( "K7", 21,  0, 1),
        ( "K9", 30,  0, 0),
        ("K10", 31,  0, 1),
        ("K11", 33,  4, 0),
        ( "L1",  4,  0, 0),
        ( "L2",  6,  0, 1),
        ( "L3", 11,  0, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 16,  0, 1),
        ( "L7", 24,  0, 0),
        ( "L8", 29,  0, 0),
        ("L10", 31,  0, 0),
    ],
    "8k-cm225:4k": [
        ( "A1",  1, 33, 1),
        ( "A2",  3, 33, 1),
        ( "A5",  6, 33, 1),
        ( "A6", 11, 33, 0),
        ( "A7", 12, 33, 0),
        ( "A8", 17, 33, 1),
        ( "A9", 18, 33, 1),
        ("A11", 23, 33, 1),
        ("A15", 31, 33, 0),
        ( "B2",  2, 33, 1),
        ( "B3",  4, 33, 1),
        ( "B4",  5, 33, 1),
        ( "B5",  7, 33, 1),
        ( "B6", 10, 33, 0),
        ( "B7", 14, 33, 0),
        ( "B8", 19, 33, 1),
        ( "B9", 18, 33, 0),
        ("B10", 22, 33, 0),
        ("B11", 23, 33, 0),
        ("B12", 25, 33, 1),
        ("B13", 27, 33, 1),
        ("B14", 31, 33, 1),
        ("B15", 33, 31, 0),
        ( "C1",  0, 28, 0),
        ( "C3",  2, 33, 0),
        ( "C4",  3, 33, 0),
        ( "C5",  5, 33, 0),
        ( "C6", 13, 33, 0),
        ( "C7", 11, 33, 1),
        ( "C8", 19, 33, 0),
        ( "C9", 17, 33, 0),
        ("C10", 20, 33, 0),
        ("C11", 24, 33, 1),
        ("C12", 30, 33, 1),
        ("C13", 30, 33, 0),
        ("C14", 33, 30, 0),
        ( "D1",  0, 25, 0),
        ( "D2",  0, 24, 1),
        ( "D3",  0, 27, 0),
        ( "D4",  0, 30, 0),
        ( "D5",  4, 33, 0),
        ( "D6",  9, 33, 0),
        ( "D7", 10, 33, 1),
        ( "D8", 16, 33, 1),
        ( "D9", 26, 33, 1),
        ("D10", 25, 33, 0),
        ("D11", 28, 33, 1),
        ("D13", 33, 27, 1),
        ("D14", 33, 25, 0),
        ("D15", 33, 27, 0),
        ( "E2",  0, 24, 0),
        ( "E3",  0, 28, 1),
        ( "E4",  0, 30, 1),
        ( "E5",  0, 27, 1),
        ( "E6",  0, 25, 1),
        ( "E9", 26, 33, 0),
        ("E10", 27, 33, 0),
        ("E11", 29, 33, 1),
        ("E13", 33, 28, 0),
        ("E14", 33, 24, 0),
        ( "F1",  0, 20, 0),
        ( "F2",  0, 21, 0),
        ( "F3",  0, 21, 1),
        ( "F4",  0, 22, 0),
        ( "F5",  0, 22, 1),
        ( "F7",  8, 33, 1),
        ( "F9", 20, 33, 1),
        ("F11", 33, 24, 1),
        ("F12", 33, 23, 1),
        ("F13", 33, 23, 0),
        ("F14", 33, 21, 0),
        ("F15", 33, 22, 0),
        ( "G2",  0, 20, 1),
        ( "G4",  0, 17, 0),
        ( "G5",  0, 18, 1),
        ("G10", 33, 20, 1),
        ("G11", 33, 19, 1),
        ("G12", 33, 21, 1),
        ("G13", 33, 17, 0),
        ("G14", 33, 20, 0),
        ("G15", 33, 19, 0),
        ( "H1",  0, 16, 0),
        ( "H2",  0, 18, 0),
        ( "H3",  0, 14, 1),
        ( "H4",  0, 13, 1),
        ( "H5",  0, 16, 1),
        ( "H6",  0, 17, 1),
        ("H11", 33, 14, 1),
        ("H12", 33, 16, 1),
        ("H13", 33, 15, 1),
        ("H14", 33, 15, 0),
        ( "J1",  0, 13, 0),
        ( "J2",  0, 12, 0),
        ( "J3",  0, 14, 0),
        ( "J4",  0, 11, 1),
        ( "J5",  0, 12, 1),
        ("J10", 33,  5, 1),
        ("J11", 33, 10, 1),
        ("J12", 33,  6, 1),
        ("J14", 33, 14, 0),
        ("J15", 33, 13, 0),
        ( "K1",  0, 11, 0),
        ( "K4",  0,  4, 0),
        ( "K5",  0,  6, 1),
        ( "K9", 20,  0, 1),
        ("K11", 29,  0, 0),
        ("K12", 33,  4, 1),
        ("K13", 33,  5, 0),
        ("K15", 33,  9, 0),
        ( "L3",  0,  7, 1),
        ( "L4",  0,  3, 0),
        ( "L5",  4,  0, 0),
        ( "L6",  7,  0, 0),
        ( "L7", 12,  0, 0),
        ( "L9", 17,  0, 0),
        ("L10", 21,  0, 1),
        ("L11", 30,  0, 1),
        ("L12", 33,  3, 1),
        ("L13", 33,  6, 0),
        ( "M1",  0,  7, 0),
        ( "M2",  0,  6, 0),
        ( "M3",  0,  5, 0),
        ( "M4",  0,  3, 1),
        ( "M5",  6,  0, 0),
        ( "M6",  8,  0, 0),
        ( "M7", 13,  0, 1),
        ( "M8", 15,  0, 0),
        ( "M9", 19,  0, 1),
        ("M11", 30,  0, 0),
        ("M12", 31,  0, 1),
        ("M13", 33,  4, 0),
        ("M15", 33,  3, 0),
        ( "N2",  0,  5, 1),
        ( "N3",  2,  0, 0),
        ( "N4",  3,  0, 0),
        ( "N5",  9,  0, 1),
        ( "N6", 12,  0, 1),
        ( "N7", 16,  0, 1),
        ( "N9", 20,  0, 0),
        ("N10", 22,  0, 1),
        ("N12", 31,  0, 0),
        ( "P1",  0,  4, 1),
        ( "P2",  2,  0, 1),
        ( "P4",  7,  0, 1),
        ( "P5", 10,  0, 1),
        ( "P6", 14,  0, 1),
        ( "P7", 17,  0, 1),
        ( "P8", 19,  0, 0),
        ( "P9", 22,  0, 0),
        ("P10", 23,  0, 0),
        ("P11", 25,  0, 0),
        ("P12", 29,  0, 1),
        ("P13", 27,  0, 0),
        ("P14", 33,  2, 1),
        ("P15", 33,  1, 1),
        ( "R1",  3,  0, 1),
        ( "R2",  4,  0, 1),
        ( "R3",  6,  0, 1),
        ( "R4",  8,  0, 1),
        ( "R5", 11,  0, 1),
        ( "R6", 15,  0, 1),
        ( "R9", 21,  0, 0),
        ("R10", 24,  0, 0),
        ("R11", 26,  0, 0),
        ("R12", 28,  0, 0),
        ("R14", 33,  2, 0),
        ("R15", 33,  1, 0),
    ],
    "8k-cm81": [
        ( "A1",  2, 33, 1),
        ( "A2",  4, 33, 0),
        ( "A3",  6, 33, 0),
        ( "A4", 10, 33, 1),
        ( "A6", 23, 33, 0),
        ( "A7", 27, 33, 0),
        ( "A8", 28, 33, 1),
        ( "A9", 33,  4, 1),
        ( "B1",  0, 28, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  5, 33, 1),
        ( "B4",  9, 33, 0),
        ( "B5", 21, 33, 1),
        ( "B6", 24, 33, 0),
        ( "B7", 25, 33, 1),
        ( "B8", 30, 33, 1),
        ( "B9", 33,  6, 1),
        ( "C1",  0, 28, 0),
        ( "C2",  0, 30, 1),
        ( "C3",  0, 23, 0),
        ( "C4", 16, 33, 1),
        ( "C5", 17, 33, 0),
        ( "C9", 33, 21, 1),
        ( "D1",  0, 20, 1),
        ( "D2",  0, 23, 1),
        ( "D3",  0, 17, 0),
        ( "D5",  8, 33, 1),
        ( "D6", 33,  4, 0),
        ( "D7", 33,  5, 0),
        ( "D8", 33, 17, 0),
        ( "D9", 33,  6, 0),
        ( "E1",  0, 20, 0),
        ( "E2",  0, 17, 1),
        ( "E3",  0, 16, 1),
        ( "E4",  0, 16, 0),
        ( "E5",  7, 33, 1),
        ( "E7", 33,  5, 1),
        ( "E8", 33, 16, 1),
        ( "F1",  0,  7, 1),
        ( "F3",  0,  7, 0),
        ( "F7", 31,  0, 1),
        ( "F8", 33,  3, 0),
        ( "G1",  0,  5, 0),
        ( "G2",  0,  3, 1),
        ( "G3",  0,  5, 1),
        ( "G4", 16,  0, 1),
        ( "G5", 29,  0, 0),
        ( "G6", 30,  0, 0),
        ( "G7", 31,  0, 0),
        ( "G8", 33,  3, 1),
        ( "G9", 33,  2, 1),
        ( "H1",  3,  0, 0),
        ( "H2",  0,  3, 0),
        ( "H4", 17,  0, 0),
        ( "H5", 29,  0, 1),
        ( "H7", 30,  0, 1),
        ( "H9", 33,  2, 0),
        ( "J1",  3,  0, 1),
        ( "J2",  4,  0, 0),
        ( "J3",  4,  0, 1),
        ( "J4", 11,  0, 0),
        ( "J8", 33,  1, 0),
        ( "J9", 33,  1, 1),
    ],
    "8k-cm121": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 1),
        ( "A3",  3, 33, 0),
        ( "A4",  9, 33, 0),
        ( "A5", 11, 33, 0),
        ( "A6", 11, 33, 1),
        ( "A7", 19, 33, 1),
        ( "A8", 20, 33, 1),
        ( "A9", 26, 33, 1),
        ("A10", 30, 33, 1),
        ("A11", 31, 33, 1),
        ( "B1",  0, 30, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  4, 33, 0),
        ( "B4",  5, 33, 0),
        ( "B5", 10, 33, 1),
        ( "B6", 16, 33, 1),
        ( "B7", 17, 33, 0),
        ( "B8", 27, 33, 0),
        ( "B9", 28, 33, 1),
        ("B11", 33, 28, 0),
        ( "C1",  0, 25, 0),
        ( "C2",  0, 25, 1),
        ( "C3",  0, 27, 0),
        ( "C4",  0, 27, 1),
        ( "C7", 20, 33, 0),
        ( "C8", 26, 33, 0),
        ( "C9", 29, 33, 1),
        ("C11", 33, 27, 1),
        ( "D1",  0, 22, 0),
        ( "D2",  0, 21, 1),
        ( "D3",  0, 21, 0),
        ( "D5",  8, 33, 1),
        ( "D7", 25, 33, 0),
        ( "D9", 33, 21, 0),
        ("D10", 33, 24, 1),
        ("D11", 33, 23, 1),
        ( "E1",  0, 22, 1),
        ( "E2",  0, 20, 1),
        ( "E3",  0, 20, 0),
        ( "E8", 33, 20, 1),
        ( "E9", 33, 19, 1),
        ("E10", 33, 17, 0),
        ("E11", 33, 21, 1),
        ( "F1",  0, 18, 1),
        ( "F2",  0, 18, 0),
        ( "F3",  0, 17, 0),
        ( "F4",  0, 17, 1),
        ( "F9", 33, 15, 0),
        ("F10", 33, 14, 1),
        ("F11", 33, 16, 1),
        ( "G1",  0, 16, 1),
        ( "G2",  0, 16, 0),
        ( "G3",  0, 12, 1),
        ( "G8", 33,  5, 1),
        ( "G9", 33, 10, 1),
        ("G10", 33,  6, 1),
        ("G11", 33, 11, 0),
        ( "H1",  0, 11, 1),
        ( "H2",  0, 11, 0),
        ( "H3",  0, 12, 0),
        ( "H7", 20,  0, 1),
        ( "H9", 29,  0, 1),
        ("H10", 33,  4, 1),
        ("H11", 33,  6, 0),
        ( "J1",  0,  6, 1),
        ( "J2",  0,  4, 0),
        ( "J3",  4,  0, 1),
        ( "J4",  8,  0, 0),
        ( "J5", 15,  0, 0),
        ( "J7", 20,  0, 0),
        ( "J8", 22,  0, 1),
        ( "J9", 30,  0, 1),
        ("J10", 33,  5, 0),
        ("J11", 33,  3, 1),
        ( "K1",  0,  6, 0),
        ( "K2",  0,  4, 1),
        ( "K3",  7,  0, 1),
        ( "K4", 12,  0, 1),
        ( "K5", 15,  0, 1),
        ( "K6", 17,  0, 0),
        ( "K7", 21,  0, 1),
        ( "K9", 30,  0, 0),
        ("K10", 31,  0, 1),
        ("K11", 33,  4, 0),
        ( "L1",  4,  0, 0),
        ( "L2",  6,  0, 1),
        ( "L3", 11,  0, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 16,  0, 1),
        ( "L7", 24,  0, 0),
        ( "L8", 29,  0, 0),
        ("L10", 31,  0, 0),
    ],
	"8k-bg121": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 1),
        ( "A3",  3, 33, 0),
        ( "A4",  9, 33, 0),
        ( "A5", 11, 33, 0),
        ( "A6", 11, 33, 1),
        ( "A7", 19, 33, 1),
        ( "A8", 20, 33, 1),
        ( "A9", 26, 33, 1),
        ("A10", 30, 33, 1),
        ("A11", 31, 33, 1),
        ( "B1",  0, 30, 1),
        ( "B2",  0, 30, 0),
        ( "B3",  4, 33, 0),
        ( "B4",  5, 33, 0),
        ( "B5", 10, 33, 1),
        ( "B6", 16, 33, 1),
        ( "B7", 17, 33, 0),
        ( "B8", 27, 33, 0),
        ( "B9", 28, 33, 1),
        ("B11", 33, 28, 0),
        ( "C1",  0, 25, 0),
        ( "C2",  0, 25, 1),
        ( "C3",  0, 27, 0),
        ( "C4",  0, 27, 1),
        ( "C7", 20, 33, 0),
        ( "C8", 26, 33, 0),
        ( "C9", 29, 33, 1),
        ("C11", 33, 27, 1),
        ( "D1",  0, 22, 0),
        ( "D2",  0, 21, 1),
        ( "D3",  0, 21, 0),
        ( "D5",  8, 33, 1),
        ( "D7", 25, 33, 0),
        ( "D9", 33, 21, 0),
        ("D10", 33, 24, 1),
        ("D11", 33, 23, 1),
        ( "E1",  0, 22, 1),
        ( "E2",  0, 20, 1),
        ( "E3",  0, 20, 0),
        ( "E8", 33, 20, 1),
        ( "E9", 33, 19, 1),
        ("E10", 33, 17, 0),
        ("E11", 33, 21, 1),
        ( "F1",  0, 18, 1),
        ( "F2",  0, 18, 0),
        ( "F3",  0, 17, 0),
        ( "F4",  0, 17, 1),
        ( "F9", 33, 15, 0),
        ("F10", 33, 14, 1),
        ("F11", 33, 16, 1),
        ( "G1",  0, 16, 1),
        ( "G2",  0, 16, 0),
        ( "G3",  0, 12, 1),
        ( "G8", 33,  5, 1),
        ( "G9", 33, 10, 1),
        ("G10", 33,  6, 1),
        ("G11", 33, 11, 0),
        ( "H1",  0, 11, 1),
        ( "H2",  0, 11, 0),
        ( "H3",  0, 12, 0),
        ( "H7", 20,  0, 1),
        ( "H9", 29,  0, 1),
        ("H10", 33,  4, 1),
        ("H11", 33,  6, 0),
        ( "J1",  0,  6, 1),
        ( "J2",  0,  4, 0),
        ( "J3",  4,  0, 1),
        ( "J4",  8,  0, 0),
        ( "J5", 15,  0, 0),
        ( "J7", 20,  0, 0),
        ( "J8", 22,  0, 1),
        ( "J9", 30,  0, 1),
        ("J10", 33,  5, 0),
        ("J11", 33,  3, 1),
        ( "K1",  0,  6, 0),
        ( "K2",  0,  4, 1),
        ( "K3",  7,  0, 1),
        ( "K4", 12,  0, 1),
        ( "K5", 15,  0, 1),
        ( "K6", 17,  0, 0),
        ( "K7", 21,  0, 1),
        ( "K9", 30,  0, 0),
        ("K10", 31,  0, 1),
        ("K11", 33,  4, 0),
        ( "L1",  4,  0, 0),
        ( "L2",  6,  0, 1),
        ( "L3", 11,  0, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 16,  0, 1),
        ( "L7", 24,  0, 0),
        ( "L8", 29,  0, 0),
        ("L10", 31,  0, 0),
    ],
    "8k-cm225": [
        ( "A1",  1, 33, 1),
        ( "A2",  3, 33, 1),
        ( "A5",  6, 33, 1),
        ( "A6", 11, 33, 0),
        ( "A7", 12, 33, 0),
        ( "A8", 17, 33, 1),
        ( "A9", 18, 33, 1),
        ("A10", 21, 33, 0),
        ("A11", 23, 33, 1),
        ("A15", 31, 33, 0),
        ( "B1",  0, 31, 0),
        ( "B2",  2, 33, 1),
        ( "B3",  4, 33, 1),
        ( "B4",  5, 33, 1),
        ( "B5",  7, 33, 1),
        ( "B6", 10, 33, 0),
        ( "B7", 14, 33, 0),
        ( "B8", 19, 33, 1),
        ( "B9", 18, 33, 0),
        ("B10", 22, 33, 0),
        ("B11", 23, 33, 0),
        ("B12", 25, 33, 1),
        ("B13", 27, 33, 1),
        ("B14", 31, 33, 1),
        ("B15", 33, 31, 0),
        ( "C1",  0, 28, 0),
        ( "C2",  0, 31, 1),
        ( "C3",  2, 33, 0),
        ( "C4",  3, 33, 0),
        ( "C5",  5, 33, 0),
        ( "C6", 13, 33, 0),
        ( "C7", 11, 33, 1),
        ( "C8", 19, 33, 0),
        ( "C9", 17, 33, 0),
        ("C10", 20, 33, 0),
        ("C11", 24, 33, 1),
        ("C12", 30, 33, 1),
        ("C13", 30, 33, 0),
        ("C14", 33, 30, 0),
        ( "D1",  0, 25, 0),
        ( "D2",  0, 24, 1),
        ( "D3",  0, 27, 0),
        ( "D4",  0, 30, 0),
        ( "D5",  4, 33, 0),
        ( "D6",  9, 33, 0),
        ( "D7", 10, 33, 1),
        ( "D8", 16, 33, 1),
        ( "D9", 26, 33, 1),
        ("D10", 25, 33, 0),
        ("D11", 28, 33, 1),
        ("D13", 33, 27, 1),
        ("D14", 33, 25, 0),
        ("D15", 33, 27, 0),
        ( "E2",  0, 24, 0),
        ( "E3",  0, 28, 1),
        ( "E4",  0, 30, 1),
        ( "E5",  0, 27, 1),
        ( "E6",  0, 25, 1),
        ( "E9", 26, 33, 0),
        ("E10", 27, 33, 0),
        ("E11", 29, 33, 1),
        ("E13", 33, 28, 0),
        ("E14", 33, 24, 0),
        ( "F1",  0, 20, 0),
        ( "F2",  0, 21, 0),
        ( "F3",  0, 21, 1),
        ( "F4",  0, 22, 0),
        ( "F5",  0, 22, 1),
        ( "F7",  8, 33, 1),
        ( "F9", 20, 33, 1),
        ("F11", 33, 24, 1),
        ("F12", 33, 23, 1),
        ("F13", 33, 23, 0),
        ("F14", 33, 21, 0),
        ("F15", 33, 22, 0),
        ( "G1",  0, 19, 0),
        ( "G2",  0, 20, 1),
        ( "G3",  0, 19, 1),
        ( "G4",  0, 17, 0),
        ( "G5",  0, 18, 1),
        ("G10", 33, 20, 1),
        ("G11", 33, 19, 1),
        ("G12", 33, 21, 1),
        ("G13", 33, 17, 0),
        ("G14", 33, 20, 0),
        ("G15", 33, 19, 0),
        ( "H1",  0, 16, 0),
        ( "H2",  0, 18, 0),
        ( "H3",  0, 14, 1),
        ( "H4",  0, 13, 1),
        ( "H5",  0, 16, 1),
        ( "H6",  0, 17, 1),
        ("H11", 33, 14, 1),
        ("H12", 33, 16, 1),
        ("H13", 33, 15, 1),
        ("H14", 33, 15, 0),
        ( "J1",  0, 13, 0),
        ( "J2",  0, 12, 0),
        ( "J3",  0, 14, 0),
        ( "J4",  0, 11, 1),
        ( "J5",  0, 12, 1),
        ("J10", 33,  5, 1),
        ("J11", 33, 10, 1),
        ("J12", 33,  6, 1),
        ("J13", 33, 11, 0),
        ("J14", 33, 14, 0),
        ("J15", 33, 13, 0),
        ( "K1",  0, 11, 0),
        ( "K3",  0,  9, 1),
        ( "K4",  0,  4, 0),
        ( "K5",  0,  6, 1),
        ( "K9", 20,  0, 1),
        ("K11", 29,  0, 0),
        ("K12", 33,  4, 1),
        ("K13", 33,  5, 0),
        ("K14", 33, 12, 0),
        ("K15", 33,  9, 0),
        ( "L1",  0,  9, 0),
        ( "L3",  0,  7, 1),
        ( "L4",  0,  3, 0),
        ( "L5",  4,  0, 0),
        ( "L6",  7,  0, 0),
        ( "L7", 12,  0, 0),
        ( "L9", 17,  0, 0),
        ("L10", 21,  0, 1),
        ("L11", 30,  0, 1),
        ("L12", 33,  3, 1),
        ("L13", 33,  6, 0),
        ("L14", 33,  7, 0),
        ( "M1",  0,  7, 0),
        ( "M2",  0,  6, 0),
        ( "M3",  0,  5, 0),
        ( "M4",  0,  3, 1),
        ( "M5",  6,  0, 0),
        ( "M6",  8,  0, 0),
        ( "M7", 13,  0, 1),
        ( "M8", 15,  0, 0),
        ( "M9", 19,  0, 1),
        ("M11", 30,  0, 0),
        ("M12", 31,  0, 1),
        ("M13", 33,  4, 0),
        ("M14", 33,  8, 0),
        ("M15", 33,  3, 0),
        ( "N2",  0,  5, 1),
        ( "N3",  2,  0, 0),
        ( "N4",  3,  0, 0),
        ( "N5",  9,  0, 1),
        ( "N6", 12,  0, 1),
        ( "N7", 16,  0, 1),
        ( "N9", 20,  0, 0),
        ("N10", 22,  0, 1),
        ("N12", 31,  0, 0),
        ( "P1",  0,  4, 1),
        ( "P2",  2,  0, 1),
        ( "P4",  7,  0, 1),
        ( "P5", 10,  0, 1),
        ( "P6", 14,  0, 1),
        ( "P7", 17,  0, 1),
        ( "P8", 19,  0, 0),
        ( "P9", 22,  0, 0),
        ("P10", 23,  0, 0),
        ("P11", 25,  0, 0),
        ("P12", 29,  0, 1),
        ("P13", 27,  0, 0),
        ("P14", 33,  2, 1),
        ("P15", 33,  1, 1),
        ( "R1",  3,  0, 1),
        ( "R2",  4,  0, 1),
        ( "R3",  6,  0, 1),
        ( "R4",  8,  0, 1),
        ( "R5", 11,  0, 1),
        ( "R6", 15,  0, 1),
        ( "R9", 21,  0, 0),
        ("R10", 24,  0, 0),
        ("R11", 26,  0, 0),
        ("R12", 28,  0, 0),
        ("R14", 33,  2, 0),
        ("R15", 33,  1, 0),
    ],
    "8k-cb132": [
        ( "A1",  2, 33, 0),
        ( "A2",  3, 33, 0),
        ( "A3",  3, 33, 1),
        ( "A4",  5, 33, 0),
        ( "A5", 10, 33, 1),
        ( "A6", 16, 33, 1),
        ( "A7", 17, 33, 0),
        ("A10", 25, 33, 0),
        ("A11", 26, 33, 0),
        ("A12", 30, 33, 1),
        ( "B1",  0, 30, 1),
        ("B14", 33, 28, 0),
        ( "C1",  0, 30, 0),
        ( "C3",  0, 27, 1),
        ( "C4",  4, 33, 0),
        ( "C5",  8, 33, 1),
        ( "C6", 11, 33, 1),
        ( "C7", 14, 33, 1),
        ( "C9", 20, 33, 1),
        ("C10", 22, 33, 1),
        ("C11", 28, 33, 1),
        ("C12", 29, 33, 1),
        ("C14", 33, 24, 1),
        ( "D1",  0, 25, 1),
        ( "D3",  0, 27, 0),
        ( "D4",  0, 22, 1),
        ( "D5",  9, 33, 0),
        ( "D6", 11, 33, 0),
        ( "D7", 13, 33, 1),
        ( "D9", 21, 33, 1),
        ("D10", 27, 33, 0),
        ("D11", 26, 33, 1),
        ("D12", 33, 27, 1),
        ("D14", 33, 23, 1),
        ( "E1",  0, 25, 0),
        ( "E4",  0, 22, 0),
        ("E11", 33, 20, 1),
        ("E12", 33, 21, 0),
        ("E14", 33, 21, 1),
        ( "F3",  0, 21, 0),
        ( "F4",  0, 21, 1),
        ("F11", 33, 19, 1),
        ("F12", 33, 15, 0),
        ("F14", 33, 16, 1),
        ( "G1",  0, 17, 0),
        ( "G3",  0, 17, 1),
        ( "G4",  0, 20, 0),
        ("G11", 33, 14, 1),
        ("G12", 33, 11, 0),
        ("G14", 33, 17, 0),
        ( "H1",  0, 16, 1),
        ( "H3",  0, 16, 0),
        ( "H4",  0, 20, 1),
        ("H11", 33, 10, 1),
        ("H12", 33,  6, 1),
        ( "J1",  0, 18, 0),
        ( "J3",  0, 18, 1),
        ("J11", 33,  6, 0),
        ("J12", 33,  5, 1),
        ( "K3",  0, 11, 1),
        ( "K4",  0, 11, 0),
        ("K11", 33,  4, 1),
        ("K12", 33,  4, 0),
        ("K14", 33,  5, 0),
        ( "L1",  0,  6, 1),
        ( "L4", 12,  0, 0),
        ( "L5", 11,  0, 1),
        ( "L6", 15,  0, 0),
        ( "L8", 20,  0, 1),
        ( "L9", 29,  0, 0),
        ("L12", 33,  2, 0),
        ("L14", 33,  3, 1),
        ( "M1",  0,  6, 0),
        ( "M3",  8,  0, 0),
        ( "M4",  7,  0, 1),
        ( "M6", 14,  0, 1),
        ( "M7", 15,  0, 1),
        ( "M9", 22,  0, 1),
        ("M11", 30,  0, 0),
        ("M12", 33,  1, 0),
        ( "N1",  0,  4, 1),
        ("N14", 33,  2, 1),
        ( "P1",  0,  4, 0),
        ( "P2",  4,  0, 0),
        ( "P3",  5,  0, 1),
        ( "P4", 12,  0, 1),
        ( "P5", 13,  0, 0),
        ( "P7", 16,  0, 1),
        ( "P8", 17,  0, 0),
        ( "P9", 21,  0, 1),
        ("P10", 29,  0, 1),
        ("P11", 30,  0, 1),
        ("P12", 31,  0, 0),
        ("P13", 31,  0, 1),
        ("P14", 33,  1, 1),
    ],
    "8k-ct256": [
        ( "A1",  4, 33, 1),
        ( "A2",  5, 33, 1),
        ( "A5",  8, 33, 0),
        ( "A6",  9, 33, 0),
        ( "A7", 12, 33, 0),
        ( "A9", 18, 33, 1),
        ("A10", 22, 33, 1),
        ("A11", 22, 33, 0),
        ("A15", 27, 33, 0),
        ("A16", 27, 33, 1),
        ( "B1",  0, 30, 0),
        ( "B2",  0, 31, 0),
        ( "B3",  3, 33, 0),
        ( "B4",  6, 33, 1),
        ( "B5",  7, 33, 1),
        ( "B6", 10, 33, 1),
        ( "B7", 11, 33, 0),
        ( "B8", 13, 33, 0),
        ( "B9", 16, 33, 0),
        ("B10", 24, 33, 0),
        ("B11", 23, 33, 1),
        ("B12", 24, 33, 1),
        ("B13", 26, 33, 1),
        ("B14", 30, 33, 0),
        ("B15", 31, 33, 0),
        ("B16", 33, 30, 0),
        ( "C1",  0, 28, 1),
        ( "C2",  0, 28, 0),
        ( "C3",  1, 33, 0),
        ( "C4",  3, 33, 1),
        ( "C5",  4, 33, 0),
        ( "C6", 10, 33, 0),
        ( "C7", 11, 33, 1),
        ( "C8", 17, 33, 0),
        ( "C9", 20, 33, 0),
        ("C10", 23, 33, 0),
        ("C11", 25, 33, 1),
        ("C12", 29, 33, 1),
        ("C13", 28, 33, 1),
        ("C14", 31, 33, 1),
        ("C16", 33, 28, 0),
        ( "D1",  0, 25, 0),
        ( "D2",  0, 27, 0),
        ( "D3",  1, 33, 1),
        ( "D4",  2, 33, 1),
        ( "D5",  5, 33, 0),
        ( "D6",  8, 33, 1),
        ( "D7",  9, 33, 1),
        ( "D8", 14, 33, 1),
        ( "D9", 19, 33, 0),
        ("D10", 20, 33, 1),
        ("D11", 25, 33, 0),
        ("D13", 30, 33, 1),
        ("D14", 33, 31, 0),
        ("D15", 33, 26, 0),
        ("D16", 33, 24, 0),
        ( "E2",  0, 23, 0),
        ( "E3",  0, 24, 0),
        ( "E4",  0, 31, 1),
        ( "E5",  2, 33, 0),
        ( "E6",  7, 33, 0),
        ( "E9", 19, 33, 1),
        ("E10", 26, 33, 0),
        ("E11", 29, 33, 0),
        ("E13", 33, 30, 1),
        ("E14", 33, 27, 1),
        ("E16", 33, 23, 0),
        ( "F1",  0, 20, 0),
        ( "F2",  0, 21, 0),
        ( "F3",  0, 22, 0),
        ( "F4",  0, 27, 1),
        ( "F5",  0, 30, 1),
        ( "F7", 16, 33, 1),
        ( "F9", 17, 33, 1),
        ("F11", 33, 26, 1),
        ("F12", 33, 25, 1),
        ("F13", 33, 28, 1),
        ("F14", 33, 25, 0),
        ("F15", 33, 22, 0),
        ("F16", 33, 21, 0),
        ( "G1",  0, 17, 0),
        ( "G2",  0, 19, 0),
        ( "G3",  0, 22, 1),
        ( "G4",  0, 24, 1),
        ( "G5",  0, 25, 1),
        ("G10", 33, 20, 1),
        ("G11", 33, 21, 1),
        ("G12", 33, 24, 1),
        ("G13", 33, 23, 1),
        ("G14", 33, 22, 1),
        ("G15", 33, 20, 0),
        ("G16", 33, 19, 0),
        ( "H1",  0, 16, 0),
        ( "H2",  0, 18, 0),
        ( "H3",  0, 21, 1),
        ( "H4",  0, 19, 1),
        ( "H5",  0, 23, 1),
        ( "H6",  0, 20, 1),
        ("H11", 33, 16, 1),
        ("H12", 33, 19, 1),
        ("H13", 33, 16, 0),
        ("H14", 33, 17, 1),
        ("H16", 33, 17, 0),
        ( "J1",  0, 14, 0),
        ( "J2",  0, 14, 1),
        ( "J3",  0, 16, 1),
        ( "J4",  0, 18, 1),
        ( "J5",  0, 17, 1),
        ("J10", 33,  7, 1),
        ("J11", 33,  9, 1),
        ("J12", 33, 14, 1),
        ("J13", 33, 15, 0),
        ("J14", 33, 13, 1),
        ("J15", 33, 11, 1),
        ("J16", 33, 15, 1),
        ( "K1",  0, 13, 1),
        ( "K3",  0, 13, 0),
        ( "K4",  0, 11, 1),
        ( "K5",  0,  9, 1),
        ( "K9", 17,  0, 0),
        ("K11", 29,  0, 0),
        ("K12", 33,  6, 1),
        ("K13", 33, 10, 1),
        ("K14", 33, 11, 0),
        ("K15", 33, 12, 0),
        ("K16", 33, 13, 0),
        ( "L1",  0, 12, 0),
        ( "L3",  0, 10, 0),
        ( "L4",  0, 12, 1),
        ( "L5",  0,  6, 1),
        ( "L6",  0, 10, 1),
        ( "L7",  0,  8, 1),
        ( "L9", 13,  0, 0),
        ("L10", 19,  0, 1),
        ("L11", 26,  0, 1),
        ("L12", 33,  4, 1),
        ("L13", 33,  5, 1),
        ("L14", 33,  6, 0),
        ("L16", 33, 10, 0),
        ( "M1",  0, 11, 0),
        ( "M2",  0,  9, 0),
        ( "M3",  0,  7, 0),
        ( "M4",  0,  5, 0),
        ( "M5",  0,  4, 0),
        ( "M6",  0,  7, 1),
        ( "M7",  8,  0, 0),
        ( "M8", 10,  0, 0),
        ( "M9", 16,  0, 0),
        ("M11", 23,  0, 1),
        ("M12", 27,  0, 1),
        ("M13", 33,  3, 1),
        ("M14", 33,  4, 0),
        ("M15", 33,  8, 0),
        ("M16", 33,  7, 0),
        ( "N2",  0,  8, 0),
        ( "N3",  0,  6, 0),
        ( "N4",  0,  3, 0),
        ( "N5",  4,  0, 0),
        ( "N6",  2,  0, 0),
        ( "N7",  9,  0, 0),
        ( "N9", 15,  0, 0),
        ("N10", 20,  0, 1),
        ("N12", 26,  0, 0),
        ("N16", 33,  5, 0),
        ( "P1",  0,  5, 1),
        ( "P2",  0,  4, 1),
        ( "P4",  3,  0, 0),
        ( "P5",  5,  0, 0),
        ( "P6",  9,  0, 1),
        ( "P7", 14,  0, 1),
        ( "P8", 12,  0, 0),
        ( "P9", 17,  0, 1),
        ("P10", 20,  0, 0),
        ("P11", 30,  0, 1),
        ("P12", 30,  0, 0),
        ("P13", 29,  0, 1),
        ("P14", 33,  2, 0),
        ("P15", 33,  2, 1),
        ("P16", 33,  3, 0),
        ( "R1",  0,  3, 1),
        ( "R2",  3,  0, 1),
        ( "R3",  5,  0, 1),
        ( "R4",  7,  0, 1),
        ( "R5",  6,  0, 0),
        ( "R6", 11,  0, 1),
        ( "R9", 16,  0, 1),
        ("R10", 19,  0, 0),
        ("R11", 31,  0, 0),
        ("R12", 31,  0, 1),
        ("R14", 33,  1, 0),
        ("R15", 33,  1, 1),
        ("R16", 28,  0, 0),
        ( "T1",  2,  0, 1),
        ( "T2",  4,  0, 1),
        ( "T3",  6,  0, 1),
        ( "T5", 10,  0, 1),
        ( "T6", 12,  0, 1),
        ( "T7", 13,  0, 1),
        ( "T8", 14,  0, 0),
        ( "T9", 15,  0, 1),
        ("T10", 21,  0, 0),
        ("T11", 21,  0, 1),
        ("T13", 24,  0, 0),
        ("T14", 23,  0, 0),
        ("T15", 22,  0, 1),
        ("T16", 27,  0, 0),
    ],
    "384-qn32": [
        (  "1",  0,  7, 0),
        (  "2",  0,  7, 1),
        (  "5",  0,  5, 1),
        (  "6",  0,  5, 0),
        (  "7",  0,  4, 0),
        (  "8",  0,  4, 1),
        ( "12",  5,  0, 0),
        ( "13",  5,  0, 1),
        ( "14",  6,  0, 1),
        ( "15",  6,  0, 0),
        ( "18",  7,  4, 0),
        ( "19",  7,  4, 1),
        ( "20",  7,  5, 0),
        ( "22",  7,  6, 0),
        ( "23",  7,  6, 1),
        ( "26",  6,  9, 0),
        ( "27",  5,  9, 0),
        ( "29",  4,  9, 0),
        ( "30",  3,  9, 1),
        ( "31",  2,  9, 0),
        ( "32",  2,  9, 1),
    ],
    "384-cm36": [
        ( "A1",  0,  7, 0),
        ( "A2",  2,  9, 1),
        ( "A3",  3,  9, 1),
        ( "B1",  0,  7, 1),
        ( "B3",  4,  9, 0),
        ( "B4",  7,  5, 0),
        ( "B5",  7,  5, 1),
        ( "B6",  7,  6, 0),
        ( "C1",  0,  5, 0),
        ( "C2",  0,  5, 1),
        ( "C3",  2,  9, 0),
        ( "C5",  7,  4, 1),
        ( "C6",  7,  6, 1),
        ( "D1",  0,  4, 1),
        ( "D5",  6,  0, 1),
        ( "D6",  7,  4, 0),
        ( "E1",  0,  4, 0),
        ( "E2",  3,  0, 1),
        ( "E3",  4,  0, 0),
        ( "E4",  5,  0, 0),
        ( "E5",  6,  0, 0),
        ( "E6",  7,  3, 1),
        ( "F2",  3,  0, 0),
        ( "F3",  4,  0, 1),
        ( "F5",  5,  0, 1),
    ],
    "384-cm49": [
        ( "A1",  0,  7, 1),
        ( "A2",  2,  9, 1),
        ( "A3",  3,  9, 0),
        ( "A4",  4,  9, 1),
        ( "A5",  5,  9, 0),
        ( "A6",  6,  9, 0),
        ( "A7",  6,  9, 1),
        ( "B1",  0,  7, 0),
        ( "B2",  0,  6, 0),
        ( "B3",  2,  9, 0),
        ( "B4",  4,  9, 0),
        ( "C1",  0,  5, 1),
        ( "C2",  0,  6, 1),
        ( "C4",  3,  9, 1),
        ( "C5",  7,  6, 1),
        ( "C6",  7,  5, 1),
        ( "C7",  7,  6, 0),
        ( "D1",  0,  4, 0),
        ( "D2",  0,  5, 0),
        ( "D3",  0,  2, 0),
        ( "D4",  5,  9, 1),
        ( "D6",  7,  4, 1),
        ( "D7",  7,  5, 0),
        ( "E2",  0,  4, 1),
        ( "E6",  6,  0, 1),
        ( "E7",  7,  4, 0),
        ( "F1",  0,  2, 1),
        ( "F2",  0,  1, 0),
        ( "F3",  3,  0, 1),
        ( "F4",  4,  0, 0),
        ( "F5",  5,  0, 0),
        ( "F6",  6,  0, 0),
        ( "F7",  7,  3, 1),
        ( "G1",  0,  1, 1),
        ( "G3",  3,  0, 0),
        ( "G4",  4,  0, 1),
        ( "G6",  5,  0, 1),
    ],
    "5k-sg48": [
        (  "2",  8,  0, 0),
        (  "3",  9,  0, 1),
        (  "4",  9,  0, 0),
        (  "6", 13,  0, 1),
        (  "9", 15,  0, 0),
        ( "10", 16,  0, 0),
        ( "11", 17,  0, 0),
        ( "12", 18,  0, 0),
        ( "13", 19,  0, 0),
        ( "14", 23,  0, 0),
        ( "15", 24,  0, 0),
        ( "16", 24,  0, 1),
        ( "17", 23,  0, 1),
        ( "18", 22,  0, 1),
        ( "19", 21,  0, 1),
        ( "20", 19,  0, 1),
        ( "21", 18,  0, 1),
        ( "23", 19, 31, 0),
        ( "25", 19, 31, 1),
        ( "26", 18, 31, 0),
        ( "27", 18, 31, 1),
        ( "28", 17, 31, 0),
        ( "31", 16, 31, 1),
        ( "32", 16, 31, 0),
        ( "34", 13, 31, 1),
        ( "35", 12, 31, 1),
        ( "36",  9, 31, 1),
        ( "37", 13, 31, 0),
        ( "38",  8, 31, 1),
        ( "39",  4, 31, 0),
        ( "40",  5, 31, 0),
        ( "41",  6, 31, 0),
        ( "42",  8, 31, 0),
        ( "43",  9, 31, 0),
        ( "44",  6,  0, 1),
        ( "45",  7,  0, 1),
        ( "46",  5,  0, 0),
        ( "47",  6,  0, 0),
        ( "48",  7,  0, 0),
    ],
    "u4k-sg48": [
        (  "2",  8,  0, 0),
        (  "3",  9,  0, 1),
        (  "4",  9,  0, 0),
        (  "6", 13,  0, 1),
        (  "9", 15,  0, 0),
        ( "10", 16,  0, 0),
        ( "11", 17,  0, 0),
        ( "12", 18,  0, 0),
        ( "13", 19,  0, 0),
        ( "14", 23,  0, 0),
        ( "15", 24,  0, 0),
        ( "16", 24,  0, 1),
        ( "17", 23,  0, 1),
        ( "18", 22,  0, 1),
        ( "19", 21,  0, 1),
        ( "20", 19,  0, 1),
        ( "21", 18,  0, 1),
        ( "23", 19, 21, 0),
        ( "25", 19, 21, 1),
        ( "26", 18, 21, 0),
        ( "27", 18, 21, 1),
        ( "28", 17, 21, 0),
        ( "31", 16, 21, 1),
        ( "32", 16, 21, 0),
        ( "34", 13, 21, 1),
        ( "35", 12, 21, 1),
        ( "36",  9, 21, 1),
        ( "37", 13, 21, 0),
        ( "38",  8, 21, 1),
        ( "39",  6, 21, 0),
        ( "40",  5, 21, 0),
        ( "41",  4, 21, 0),
        ( "42",  8, 21, 0),
        ( "43",  9, 21, 0),
        ( "44",  6,  0, 1),
        ( "45",  7,  0, 1),
        ( "46",  5,  0, 0),
        ( "47",  6,  0, 0),
        ( "48",  7,  0, 0),
    ],
    "5k-uwg30": [
        ( "A1", 19, 31, 1),
        ( "A2", 19, 31, 0),
        ( "A4", 12, 31, 0),
        ( "A5",  4, 31, 0),
        ( "B1", 19,  0, 0),
        ( "B3", 12, 31, 1),
        ( "B5",  5, 31, 0),
        ( "C1", 24,  0, 1),
        ( "C3", 12,  0, 0),
        ( "C5",  6, 31, 0),
        ( "D1", 24,  0, 0),
        ( "D3", 13,  0, 0),
        ( "D5",  6,  0, 0),
        ( "E1", 23,  0, 1),
        ( "E3", 13,  0, 1),
        ( "E4",  9,  0, 1),
        ( "E5",  5,  0, 0),
        ( "F1", 23,  0, 0),
        ( "F2", 19,  0, 1),
        ( "F4", 12,  0, 1),
        ( "F5",  6,  0, 1),
    ],
    "lm4k-cm49": [
        ( "A1",  5,  21, 1),
        ( "A2",  6,  21, 0),
        ( "A3",  12, 21, 1),
        ( "A4",  13, 21, 0),
        ( "A5",  17, 21, 1),
        ( "A6",  19, 21, 1),
        ( "A7",  22, 21, 1),
        ( "B1",  4, 21, 1),
        ( "B2",  7, 21, 1),
        ( "B4",  15, 21, 0),
        ( "B6",  18, 21, 0),
        ( "B7",  23, 21, 1),
        ( "C1",  4, 21, 0),
        ( "C3",  9, 21, 0),
        ( "C4",  19, 21, 0),
        ( "C6",  21, 21, 1),
        ( "C7",  23, 21, 0),
        ( "D1",  7,  0, 1),
        ( "D2",  6,  0, 1),
        ( "D3", 10,  0, 0),
        ( "D6", 19,  0, 1),
        ( "D7", 21,  0, 0),
        ( "E1",  6,  0, 0),
        ( "E2", 12,  0, 1),
        ( "E3",  7,  0, 0),
        ( "E4", 12,  0, 0),
        ( "E5", 19,  0, 0),
        ( "E6", 24,  0, 1),
        ( "E7", 22,  0, 0),
        ( "F2",  8,  0, 1),
        ( "F3",  8,  0, 0),
        ( "F4", 13,  0, 1),
        ( "F5", 23,  0, 0),
        ( "F6", 24,  0, 0),
        ( "F7", 21,  0, 1),
        ( "G3", 13,  0, 0),
        ( "G6", 23,  0, 1),
    ],
    "lm4k-cm36": [
        ( "A1",  5, 21, 1),
        ( "A2",  7, 21, 1),
        ( "A3",  9, 21, 1),
        ( "A4", 16, 21, 1),
        ( "A5", 19, 21, 1),
        ( "A6", 22, 21, 1),
        ( "B1",  4, 21, 1),
        ( "B2",  6, 21, 0),
        ( "B3", 12, 21, 1),
        ( "B4", 13, 21, 0),
        ( "B5", 21, 21, 1),
        ( "B6", 23, 21, 1),
        ( "C1",  7,  0, 1),
        ( "C5", 23, 21, 0),
        ( "C6", 23,  0, 0),
        ( "D1",  6,  0, 1),
        ( "D6", 24,  0, 0),
        ( "E1",  7,  0, 0),
        ( "E2", 13,  0, 0),
        ( "E3", 14,  0, 1),
        ( "E5", 22,  0, 1),
        ( "E6", 24,  0, 1),
        ( "F1",  6,  0, 0),
        ( "F2", 10,  0, 0),
        ( "F3", 12,  0, 1),
        ( "F4", 19,  0, 0),
        ( "F5", 22,  0, 0),
        ( "F6", 23,  0, 1),
    ],
    "lm4k-swg25tr": [
        ( "A1", 22, 21, 1),
        ( "A3", 13, 21, 0),
        ( "A4", 12, 21, 1),
        ( "A5",  5, 21, 1),
        ( "B1", 21, 21, 1),
        ( "B5",  6, 21, 0),
        ( "C1", 23,  0, 1),
        ( "C2", 19, 21, 1),
        ( "C4", 13,  0, 0),
        ( "C5",  7,  0, 1),
        ( "D1", 24,  0, 0),
        ( "D2", 23,  0, 0),
        ( "D3", 19,  0, 0),
        ( "D5",  6,  0, 1),
        ( "E1", 24,  0, 1),
        ( "E3", 12,  0, 1),
        ( "E4",  7,  0, 0),
        ( "E5",  6,  0, 0),
    ]
}

# This database contains the locations of configuration bits of the DSP tiles
# The standard configuration is stored under the key  "default". If it is necessary to
# override it for a certain DSP on a certain device use the key "{device}_{x}_{y}" where
# {x} and {y} are the location of the DSP0 tile of the DSP (NOT the tile the cbit is in).
# x and y are relative to the DSP0 tile.
dsp_config_db = {
    "default" : {
            "C_REG":                        (0, 0, "CBIT_0"),
            "A_REG":                        (0, 0, "CBIT_1"),
            "B_REG":                        (0, 0, "CBIT_2"),
            "D_REG":                        (0, 0, "CBIT_3"),
            "TOP_8x8_MULT_REG":             (0, 0, "CBIT_4"),
            "BOT_8x8_MULT_REG":             (0, 0, "CBIT_5"),
            "PIPELINE_16x16_MULT_REG1":     (0, 0, "CBIT_6"),
            "PIPELINE_16x16_MULT_REG2":     (0, 0, "CBIT_7"),
            "TOPOUTPUT_SELECT_0":           (0, 1, "CBIT_0"),
            "TOPOUTPUT_SELECT_1":           (0, 1, "CBIT_1"),
            "TOPADDSUB_LOWERINPUT_0":       (0, 1, "CBIT_2"),
            "TOPADDSUB_LOWERINPUT_1":       (0, 1, "CBIT_3"),
            "TOPADDSUB_UPPERINPUT":         (0, 1, "CBIT_4"),
            "TOPADDSUB_CARRYSELECT_0":      (0, 1, "CBIT_5"),
            "TOPADDSUB_CARRYSELECT_1":      (0, 1, "CBIT_6"),
            "BOTOUTPUT_SELECT_0":           (0, 1, "CBIT_7"),
            "BOTOUTPUT_SELECT_1":           (0, 2, "CBIT_0"),
            "BOTADDSUB_LOWERINPUT_0":       (0, 2, "CBIT_1"),
            "BOTADDSUB_LOWERINPUT_1":       (0, 2, "CBIT_2"),
            "BOTADDSUB_UPPERINPUT":         (0, 2, "CBIT_3"),
            "BOTADDSUB_CARRYSELECT_0":      (0, 2, "CBIT_4"),
            "BOTADDSUB_CARRYSELECT_1":      (0, 2, "CBIT_5"),
            "MODE_8x8":                     (0, 2, "CBIT_6"),
            "A_SIGNED":                     (0, 2, "CBIT_7"),
            "B_SIGNED":                     (0, 3, "CBIT_0")
        },
    "5k_0_15": {
            "TOPOUTPUT_SELECT_1":           (0, 4, "CBIT_3"),
            "TOPADDSUB_LOWERINPUT_0":       (0, 4, "CBIT_4"),
            "TOPADDSUB_LOWERINPUT_1":       (0, 4, "CBIT_5"),
            "TOPADDSUB_UPPERINPUT":         (0, 4, "CBIT_6"),
            "TOPADDSUB_CARRYSELECT_0":      (0, 4, "CBIT_7")
        }
}

# SPRAM data for UltraPlus devices, use icefuzz/tests/fuzz_spram.py
# to generate this
spram_db = { 
    "5k" : {
        (0, 0, 1): {
    		"ADDRESS_0":             (0, 2, "lutff_0/in_1"), 
    		"ADDRESS_10":            (0, 2, "lutff_2/in_0"), 
    		"ADDRESS_11":            (0, 2, "lutff_3/in_0"), 
    		"ADDRESS_12":            (0, 2, "lutff_4/in_0"), 
    		"ADDRESS_13":            (0, 2, "lutff_5/in_0"), 
    		"ADDRESS_1":             (0, 2, "lutff_1/in_1"), 
    		"ADDRESS_2":             (0, 2, "lutff_2/in_1"), 
    		"ADDRESS_3":             (0, 2, "lutff_3/in_1"), 
    		"ADDRESS_4":             (0, 2, "lutff_4/in_1"), 
    		"ADDRESS_5":             (0, 2, "lutff_5/in_1"), 
    		"ADDRESS_6":             (0, 2, "lutff_6/in_1"), 
    		"ADDRESS_7":             (0, 2, "lutff_7/in_1"), 
    		"ADDRESS_8":             (0, 2, "lutff_0/in_0"), 
    		"ADDRESS_9":             (0, 2, "lutff_1/in_0"), 
    		"CHIPSELECT":            (0, 3, "lutff_6/in_1"), 
    		"CLOCK":                 (0, 1, "clk"), 
    		"DATAIN_0":              (0, 1, "lutff_0/in_3"), 
    		"DATAIN_10":             (0, 1, "lutff_2/in_1"), 
    		"DATAIN_11":             (0, 1, "lutff_3/in_1"), 
    		"DATAIN_12":             (0, 1, "lutff_4/in_1"), 
    		"DATAIN_13":             (0, 1, "lutff_5/in_1"), 
    		"DATAIN_14":             (0, 1, "lutff_6/in_1"), 
    		"DATAIN_15":             (0, 1, "lutff_7/in_1"), 
    		"DATAIN_1":              (0, 1, "lutff_1/in_3"), 
    		"DATAIN_2":              (0, 1, "lutff_2/in_3"), 
    		"DATAIN_3":              (0, 1, "lutff_3/in_3"), 
    		"DATAIN_4":              (0, 1, "lutff_4/in_3"), 
    		"DATAIN_5":              (0, 1, "lutff_5/in_3"), 
    		"DATAIN_6":              (0, 1, "lutff_6/in_3"), 
    		"DATAIN_7":              (0, 1, "lutff_7/in_3"), 
    		"DATAIN_8":              (0, 1, "lutff_0/in_1"), 
    		"DATAIN_9":              (0, 1, "lutff_1/in_1"), 
    		"DATAOUT_0":             (0, 1, "slf_op_0"), 
    		"DATAOUT_10":            (0, 2, "slf_op_2"), 
    		"DATAOUT_11":            (0, 2, "slf_op_3"), 
    		"DATAOUT_12":            (0, 2, "slf_op_4"), 
    		"DATAOUT_13":            (0, 2, "slf_op_5"), 
    		"DATAOUT_14":            (0, 2, "slf_op_6"), 
    		"DATAOUT_15":            (0, 2, "slf_op_7"), 
    		"DATAOUT_1":             (0, 1, "slf_op_1"), 
    		"DATAOUT_2":             (0, 1, "slf_op_2"), 
    		"DATAOUT_3":             (0, 1, "slf_op_3"), 
    		"DATAOUT_4":             (0, 1, "slf_op_4"), 
    		"DATAOUT_5":             (0, 1, "slf_op_5"), 
    		"DATAOUT_6":             (0, 1, "slf_op_6"), 
    		"DATAOUT_7":             (0, 1, "slf_op_7"), 
    		"DATAOUT_8":             (0, 2, "slf_op_0"), 
    		"DATAOUT_9":             (0, 2, "slf_op_1"), 
    		"MASKWREN_0":            (0, 3, "lutff_0/in_0"), 
    		"MASKWREN_1":            (0, 3, "lutff_1/in_0"), 
    		"MASKWREN_2":            (0, 3, "lutff_2/in_0"), 
    		"MASKWREN_3":            (0, 3, "lutff_3/in_0"), 
    		"POWEROFF":              (0, 4, "lutff_4/in_3"), 
    		"SLEEP":                 (0, 4, "lutff_2/in_3"), 
    		"SPRAM_EN":              (0, 1, "CBIT_0"), 
    		"STANDBY":               (0, 4, "lutff_0/in_3"), 
    		"WREN":                  (0, 3, "lutff_4/in_1"), 
    	},
    	(0, 0, 2): {
    		"ADDRESS_0":             (0, 2, "lutff_6/in_0"), 
    		"ADDRESS_10":            (0, 3, "lutff_0/in_1"), 
    		"ADDRESS_11":            (0, 3, "lutff_1/in_1"), 
    		"ADDRESS_12":            (0, 3, "lutff_2/in_1"), 
    		"ADDRESS_13":            (0, 3, "lutff_3/in_1"), 
    		"ADDRESS_1":             (0, 2, "lutff_7/in_0"), 
    		"ADDRESS_2":             (0, 3, "lutff_0/in_3"), 
    		"ADDRESS_3":             (0, 3, "lutff_1/in_3"), 
    		"ADDRESS_4":             (0, 3, "lutff_2/in_3"), 
    		"ADDRESS_5":             (0, 3, "lutff_3/in_3"), 
    		"ADDRESS_6":             (0, 3, "lutff_4/in_3"), 
    		"ADDRESS_7":             (0, 3, "lutff_5/in_3"), 
    		"ADDRESS_8":             (0, 3, "lutff_6/in_3"), 
    		"ADDRESS_9":             (0, 3, "lutff_7/in_3"), 
    		"CHIPSELECT":            (0, 3, "lutff_7/in_1"), 
    		"CLOCK":                 (0, 2, "clk"), 
    		"DATAIN_0":              (0, 1, "lutff_0/in_0"), 
    		"DATAIN_10":             (0, 2, "lutff_2/in_3"), 
    		"DATAIN_11":             (0, 2, "lutff_3/in_3"), 
    		"DATAIN_12":             (0, 2, "lutff_4/in_3"), 
    		"DATAIN_13":             (0, 2, "lutff_5/in_3"), 
    		"DATAIN_14":             (0, 2, "lutff_6/in_3"), 
    		"DATAIN_15":             (0, 2, "lutff_7/in_3"), 
    		"DATAIN_1":              (0, 1, "lutff_1/in_0"), 
    		"DATAIN_2":              (0, 1, "lutff_2/in_0"), 
    		"DATAIN_3":              (0, 1, "lutff_3/in_0"), 
    		"DATAIN_4":              (0, 1, "lutff_4/in_0"), 
    		"DATAIN_5":              (0, 1, "lutff_5/in_0"), 
    		"DATAIN_6":              (0, 1, "lutff_6/in_0"), 
    		"DATAIN_7":              (0, 1, "lutff_7/in_0"), 
    		"DATAIN_8":              (0, 2, "lutff_0/in_3"), 
    		"DATAIN_9":              (0, 2, "lutff_1/in_3"), 
    		"DATAOUT_0":             (0, 3, "slf_op_0"), 
    		"DATAOUT_10":            (0, 4, "slf_op_2"), 
    		"DATAOUT_11":            (0, 4, "slf_op_3"), 
    		"DATAOUT_12":            (0, 4, "slf_op_4"), 
    		"DATAOUT_13":            (0, 4, "slf_op_5"), 
    		"DATAOUT_14":            (0, 4, "slf_op_6"), 
    		"DATAOUT_15":            (0, 4, "slf_op_7"), 
    		"DATAOUT_1":             (0, 3, "slf_op_1"), 
    		"DATAOUT_2":             (0, 3, "slf_op_2"), 
    		"DATAOUT_3":             (0, 3, "slf_op_3"), 
    		"DATAOUT_4":             (0, 3, "slf_op_4"), 
    		"DATAOUT_5":             (0, 3, "slf_op_5"), 
    		"DATAOUT_6":             (0, 3, "slf_op_6"), 
    		"DATAOUT_7":             (0, 3, "slf_op_7"), 
    		"DATAOUT_8":             (0, 4, "slf_op_0"), 
    		"DATAOUT_9":             (0, 4, "slf_op_1"), 
    		"MASKWREN_0":            (0, 3, "lutff_4/in_0"), 
    		"MASKWREN_1":            (0, 3, "lutff_5/in_0"), 
    		"MASKWREN_2":            (0, 3, "lutff_6/in_0"), 
    		"MASKWREN_3":            (0, 3, "lutff_7/in_0"), 
    		"POWEROFF":              (0, 4, "lutff_5/in_3"), 
    		"SLEEP":                 (0, 4, "lutff_3/in_3"), 
    		"SPRAM_EN":              (0, 1, "CBIT_1"), 
    		"STANDBY":               (0, 4, "lutff_1/in_3"), 
    		"WREN":                  (0, 3, "lutff_5/in_1"), 
    	},
    	(25, 0, 3): {
    		"ADDRESS_0":             (25, 2, "lutff_0/in_1"), 
    		"ADDRESS_10":            (25, 2, "lutff_2/in_0"), 
    		"ADDRESS_11":            (25, 2, "lutff_3/in_0"), 
    		"ADDRESS_12":            (25, 2, "lutff_4/in_0"), 
    		"ADDRESS_13":            (25, 2, "lutff_5/in_0"), 
    		"ADDRESS_1":             (25, 2, "lutff_1/in_1"), 
    		"ADDRESS_2":             (25, 2, "lutff_2/in_1"), 
    		"ADDRESS_3":             (25, 2, "lutff_3/in_1"), 
    		"ADDRESS_4":             (25, 2, "lutff_4/in_1"), 
    		"ADDRESS_5":             (25, 2, "lutff_5/in_1"), 
    		"ADDRESS_6":             (25, 2, "lutff_6/in_1"), 
    		"ADDRESS_7":             (25, 2, "lutff_7/in_1"), 
    		"ADDRESS_8":             (25, 2, "lutff_0/in_0"), 
    		"ADDRESS_9":             (25, 2, "lutff_1/in_0"), 
    		"CHIPSELECT":            (25, 3, "lutff_6/in_1"), 
    		"CLOCK":                 (25, 1, "clk"), 
    		"DATAIN_0":              (25, 1, "lutff_0/in_3"), 
    		"DATAIN_10":             (25, 1, "lutff_2/in_1"), 
    		"DATAIN_11":             (25, 1, "lutff_3/in_1"), 
    		"DATAIN_12":             (25, 1, "lutff_4/in_1"), 
    		"DATAIN_13":             (25, 1, "lutff_5/in_1"), 
    		"DATAIN_14":             (25, 1, "lutff_6/in_1"), 
    		"DATAIN_15":             (25, 1, "lutff_7/in_1"), 
    		"DATAIN_1":              (25, 1, "lutff_1/in_3"), 
    		"DATAIN_2":              (25, 1, "lutff_2/in_3"), 
    		"DATAIN_3":              (25, 1, "lutff_3/in_3"), 
    		"DATAIN_4":              (25, 1, "lutff_4/in_3"), 
    		"DATAIN_5":              (25, 1, "lutff_5/in_3"), 
    		"DATAIN_6":              (25, 1, "lutff_6/in_3"), 
    		"DATAIN_7":              (25, 1, "lutff_7/in_3"), 
    		"DATAIN_8":              (25, 1, "lutff_0/in_1"), 
    		"DATAIN_9":              (25, 1, "lutff_1/in_1"), 
    		"DATAOUT_0":             (25, 1, "slf_op_0"), 
    		"DATAOUT_10":            (25, 2, "slf_op_2"), 
    		"DATAOUT_11":            (25, 2, "slf_op_3"), 
    		"DATAOUT_12":            (25, 2, "slf_op_4"), 
    		"DATAOUT_13":            (25, 2, "slf_op_5"), 
    		"DATAOUT_14":            (25, 2, "slf_op_6"), 
    		"DATAOUT_15":            (25, 2, "slf_op_7"), 
    		"DATAOUT_1":             (25, 1, "slf_op_1"), 
    		"DATAOUT_2":             (25, 1, "slf_op_2"), 
    		"DATAOUT_3":             (25, 1, "slf_op_3"), 
    		"DATAOUT_4":             (25, 1, "slf_op_4"), 
    		"DATAOUT_5":             (25, 1, "slf_op_5"), 
    		"DATAOUT_6":             (25, 1, "slf_op_6"), 
    		"DATAOUT_7":             (25, 1, "slf_op_7"), 
    		"DATAOUT_8":             (25, 2, "slf_op_0"), 
    		"DATAOUT_9":             (25, 2, "slf_op_1"), 
    		"MASKWREN_0":            (25, 3, "lutff_0/in_0"), 
    		"MASKWREN_1":            (25, 3, "lutff_1/in_0"), 
    		"MASKWREN_2":            (25, 3, "lutff_2/in_0"), 
    		"MASKWREN_3":            (25, 3, "lutff_3/in_0"), 
    		"POWEROFF":              (25, 4, "lutff_4/in_3"), 
    		"SLEEP":                 (25, 4, "lutff_2/in_3"), 
    		"SPRAM_EN":              (25, 1, "CBIT_0"), 
    		"STANDBY":               (25, 4, "lutff_0/in_3"), 
    		"WREN":                  (25, 3, "lutff_4/in_1"), 
    	},
    	(25, 0, 4): {
    		"ADDRESS_0":             (25, 2, "lutff_6/in_0"), 
    		"ADDRESS_10":            (25, 3, "lutff_0/in_1"), 
    		"ADDRESS_11":            (25, 3, "lutff_1/in_1"), 
    		"ADDRESS_12":            (25, 3, "lutff_2/in_1"), 
    		"ADDRESS_13":            (25, 3, "lutff_3/in_1"), 
    		"ADDRESS_1":             (25, 2, "lutff_7/in_0"), 
    		"ADDRESS_2":             (25, 3, "lutff_0/in_3"), 
    		"ADDRESS_3":             (25, 3, "lutff_1/in_3"), 
    		"ADDRESS_4":             (25, 3, "lutff_2/in_3"), 
    		"ADDRESS_5":             (25, 3, "lutff_3/in_3"), 
    		"ADDRESS_6":             (25, 3, "lutff_4/in_3"), 
    		"ADDRESS_7":             (25, 3, "lutff_5/in_3"), 
    		"ADDRESS_8":             (25, 3, "lutff_6/in_3"), 
    		"ADDRESS_9":             (25, 3, "lutff_7/in_3"), 
    		"CHIPSELECT":            (25, 3, "lutff_7/in_1"), 
    		"CLOCK":                 (25, 2, "clk"), 
    		"DATAIN_0":              (25, 1, "lutff_0/in_0"), 
    		"DATAIN_10":             (25, 2, "lutff_2/in_3"), 
    		"DATAIN_11":             (25, 2, "lutff_3/in_3"), 
    		"DATAIN_12":             (25, 2, "lutff_4/in_3"), 
    		"DATAIN_13":             (25, 2, "lutff_5/in_3"), 
    		"DATAIN_14":             (25, 2, "lutff_6/in_3"), 
    		"DATAIN_15":             (25, 2, "lutff_7/in_3"), 
    		"DATAIN_1":              (25, 1, "lutff_1/in_0"), 
    		"DATAIN_2":              (25, 1, "lutff_2/in_0"), 
    		"DATAIN_3":              (25, 1, "lutff_3/in_0"), 
    		"DATAIN_4":              (25, 1, "lutff_4/in_0"), 
    		"DATAIN_5":              (25, 1, "lutff_5/in_0"), 
    		"DATAIN_6":              (25, 1, "lutff_6/in_0"), 
    		"DATAIN_7":              (25, 1, "lutff_7/in_0"), 
    		"DATAIN_8":              (25, 2, "lutff_0/in_3"), 
    		"DATAIN_9":              (25, 2, "lutff_1/in_3"), 
    		"DATAOUT_0":             (25, 3, "slf_op_0"), 
    		"DATAOUT_10":            (25, 4, "slf_op_2"), 
    		"DATAOUT_11":            (25, 4, "slf_op_3"), 
    		"DATAOUT_12":            (25, 4, "slf_op_4"), 
    		"DATAOUT_13":            (25, 4, "slf_op_5"), 
    		"DATAOUT_14":            (25, 4, "slf_op_6"), 
    		"DATAOUT_15":            (25, 4, "slf_op_7"), 
    		"DATAOUT_1":             (25, 3, "slf_op_1"), 
    		"DATAOUT_2":             (25, 3, "slf_op_2"), 
    		"DATAOUT_3":             (25, 3, "slf_op_3"), 
    		"DATAOUT_4":             (25, 3, "slf_op_4"), 
    		"DATAOUT_5":             (25, 3, "slf_op_5"), 
    		"DATAOUT_6":             (25, 3, "slf_op_6"), 
    		"DATAOUT_7":             (25, 3, "slf_op_7"), 
    		"DATAOUT_8":             (25, 4, "slf_op_0"), 
    		"DATAOUT_9":             (25, 4, "slf_op_1"), 
    		"MASKWREN_0":            (25, 3, "lutff_4/in_0"), 
    		"MASKWREN_1":            (25, 3, "lutff_5/in_0"), 
    		"MASKWREN_2":            (25, 3, "lutff_6/in_0"), 
    		"MASKWREN_3":            (25, 3, "lutff_7/in_0"), 
    		"POWEROFF":              (25, 4, "lutff_5/in_3"), 
    		"SLEEP":                 (25, 4, "lutff_3/in_3"), 
    		"SPRAM_EN":              (25, 1, "CBIT_1"), 
    		"STANDBY":               (25, 4, "lutff_1/in_3"), 
    		"WREN":                  (25, 3, "lutff_5/in_1"), 
    	}
    }
}

# This contains the data for extra cells not included
# in any previous databases

extra_cells_db = {
    "5k" : {
        ("HFOSC", (0, 31, 1)) : {
            "CLKHFPU":                      (0, 29, "lutff_0/in_1"),
            "CLKHFEN":                      (0, 29, "lutff_7/in_3"),
            "CLKHF":                        (0, 29, "glb_netwk_4"),
            "CLKHF_FABRIC":                 (0, 28, "slf_op_7"),
            "TRIM0":                        (25, 28, "lutff_4/in_0"),
            "TRIM1":                        (25, 28, "lutff_5/in_0"),
            "TRIM2":                        (25, 28, "lutff_6/in_0"),
            "TRIM3":                        (25, 28, "lutff_7/in_0"),
            "TRIM4":                        (25, 29, "lutff_0/in_3"),
            "TRIM5":                        (25, 29, "lutff_1/in_3"),
            "TRIM6":                        (25, 29, "lutff_2/in_3"),
            "TRIM7":                        (25, 29, "lutff_3/in_3"),
            "TRIM8":                        (25, 29, "lutff_4/in_3"),
            "TRIM9":                        (25, 29, "lutff_5/in_3"),
            "CLKHF_DIV_1":                  (0, 16, "CBIT_4"),
            "CLKHF_DIV_0":                  (0, 16, "CBIT_3"),
            "TRIM_EN":                      (0, 16, "CBIT_5")
        },
        ("LFOSC", (25, 31, 1)) : {
            "CLKLFPU":                      (25, 29, "lutff_0/in_1"),
            "CLKLFEN":                      (25, 29, "lutff_7/in_3"),
            "CLKLF":                        (25, 29, "glb_netwk_5"),
            "CLKLF_FABRIC":                 (25, 29, "slf_op_0")
        },
        ("RGBA_DRV", (0, 30, 0)) : {
            "CURREN":                       (25, 29, "lutff_6/in_3"),
            "RGBLEDEN":                     (0, 30, "lutff_1/in_1"),
            "RGB0PWM":                      (0, 30, "lutff_2/in_1"),
            "RGB1PWM":                      (0, 30, "lutff_3/in_1"),
            "RGB2PWM":                      (0, 30, "lutff_4/in_1"),
            "RGBA_DRV_EN":                  (0, 28, "CBIT_5"),
            "RGB0_CURRENT_0":               (0, 28, "CBIT_6"),
            "RGB0_CURRENT_1":               (0, 28, "CBIT_7"),
            "RGB0_CURRENT_2":               (0, 29, "CBIT_0"),
            "RGB0_CURRENT_3":               (0, 29, "CBIT_1"),
            "RGB0_CURRENT_4":               (0, 29, "CBIT_2"),
            "RGB0_CURRENT_5":               (0, 29, "CBIT_3"),
            "RGB1_CURRENT_0":               (0, 29, "CBIT_4"),
            "RGB1_CURRENT_1":               (0, 29, "CBIT_5"),
            "RGB1_CURRENT_2":               (0, 29, "CBIT_6"),
            "RGB1_CURRENT_3":               (0, 29, "CBIT_7"),
            "RGB1_CURRENT_4":               (0, 30, "CBIT_0"),
            "RGB1_CURRENT_5":               (0, 30, "CBIT_1"),
            "RGB2_CURRENT_0":               (0, 30, "CBIT_2"),
            "RGB2_CURRENT_1":               (0, 30, "CBIT_3"),
            "RGB2_CURRENT_2":               (0, 30, "CBIT_4"),
            "RGB2_CURRENT_3":               (0, 30, "CBIT_5"),
            "RGB2_CURRENT_4":               (0, 30, "CBIT_6"),
            "RGB2_CURRENT_5":               (0, 30, "CBIT_7"),
            "CURRENT_MODE":                 (0, 28, "CBIT_4"),
            
            "RGB0":                         (4, 31, 0),
            "RGB1":                         (5, 31, 0),
            "RGB2":                         (6, 31, 0),

        },
        ("I2C", (0, 31, 0)): {
    		"I2CIRQ":                (0, 30, "slf_op_7"), 
    		"I2CWKUP":               (0, 29, "slf_op_5"), 
    		"I2C_ENABLE_0":          (13, 31, "cbit2usealt_in_0"), 
    		"I2C_ENABLE_1":          (12, 31, "cbit2usealt_in_1"), 
    		"SBACKO":                (0, 30, "slf_op_6"), 
    		"SBADRI0":               (0, 30, "lutff_1/in_0"), 
    		"SBADRI1":               (0, 30, "lutff_2/in_0"), 
    		"SBADRI2":               (0, 30, "lutff_3/in_0"), 
    		"SBADRI3":               (0, 30, "lutff_4/in_0"), 
    		"SBADRI4":               (0, 30, "lutff_5/in_0"), 
    		"SBADRI5":               (0, 30, "lutff_6/in_0"), 
    		"SBADRI6":               (0, 30, "lutff_7/in_0"), 
    		"SBADRI7":               (0, 29, "lutff_2/in_0"), 
    		"SBCLKI":                (0, 30, "clk"), 
    		"SBDATI0":               (0, 29, "lutff_5/in_0"), 
    		"SBDATI1":               (0, 29, "lutff_6/in_0"), 
    		"SBDATI2":               (0, 29, "lutff_7/in_0"), 
    		"SBDATI3":               (0, 30, "lutff_0/in_3"), 
    		"SBDATI4":               (0, 30, "lutff_5/in_1"), 
    		"SBDATI5":               (0, 30, "lutff_6/in_1"), 
    		"SBDATI6":               (0, 30, "lutff_7/in_1"), 
    		"SBDATI7":               (0, 30, "lutff_0/in_0"), 
    		"SBDATO0":               (0, 29, "slf_op_6"), 
    		"SBDATO1":               (0, 29, "slf_op_7"), 
    		"SBDATO2":               (0, 30, "slf_op_0"), 
    		"SBDATO3":               (0, 30, "slf_op_1"), 
    		"SBDATO4":               (0, 30, "slf_op_2"), 
    		"SBDATO5":               (0, 30, "slf_op_3"), 
    		"SBDATO6":               (0, 30, "slf_op_4"), 
    		"SBDATO7":               (0, 30, "slf_op_5"), 
    		"SBRWI":                 (0, 29, "lutff_4/in_0"), 
    		"SBSTBI":                (0, 29, "lutff_3/in_0"), 
    		"SCLI":                  (0, 29, "lutff_2/in_1"), 
    		"SCLO":                  (0, 29, "slf_op_3"), 
    		"SCLOE":                 (0, 29, "slf_op_4"), 
    		"SDAI":                  (0, 29, "lutff_1/in_1"), 
    		"SDAO":                  (0, 29, "slf_op_1"), 
    		"SDAOE":                 (0, 29, "slf_op_2"), 
    		"SDA_INPUT_DELAYED":     (12, 31, "SDA_input_delay"), 
    		"SDA_OUTPUT_DELAYED":    (12, 31, "SDA_output_delay"), 
    	},
    	("I2C", (25, 31, 0)): {
    		"I2CIRQ":                (25, 30, "slf_op_7"), 
    		"I2CWKUP":               (25, 29, "slf_op_5"), 
    		"I2C_ENABLE_0":          (19, 31, "cbit2usealt_in_0"), 
    		"I2C_ENABLE_1":          (19, 31, "cbit2usealt_in_1"), 
    		"SBACKO":                (25, 30, "slf_op_6"), 
    		"SBADRI0":               (25, 30, "lutff_1/in_0"), 
    		"SBADRI1":               (25, 30, "lutff_2/in_0"), 
    		"SBADRI2":               (25, 30, "lutff_3/in_0"), 
    		"SBADRI3":               (25, 30, "lutff_4/in_0"), 
    		"SBADRI4":               (25, 30, "lutff_5/in_0"), 
    		"SBADRI5":               (25, 30, "lutff_6/in_0"), 
    		"SBADRI6":               (25, 30, "lutff_7/in_0"), 
    		"SBADRI7":               (25, 29, "lutff_2/in_0"), 
    		"SBCLKI":                (25, 30, "clk"), 
    		"SBDATI0":               (25, 29, "lutff_5/in_0"), 
    		"SBDATI1":               (25, 29, "lutff_6/in_0"), 
    		"SBDATI2":               (25, 29, "lutff_7/in_0"), 
    		"SBDATI3":               (25, 30, "lutff_0/in_3"), 
    		"SBDATI4":               (25, 30, "lutff_5/in_1"), 
    		"SBDATI5":               (25, 30, "lutff_6/in_1"), 
    		"SBDATI6":               (25, 30, "lutff_7/in_1"), 
    		"SBDATI7":               (25, 30, "lutff_0/in_0"), 
    		"SBDATO0":               (25, 29, "slf_op_6"), 
    		"SBDATO1":               (25, 29, "slf_op_7"), 
    		"SBDATO2":               (25, 30, "slf_op_0"), 
    		"SBDATO3":               (25, 30, "slf_op_1"), 
    		"SBDATO4":               (25, 30, "slf_op_2"), 
    		"SBDATO5":               (25, 30, "slf_op_3"), 
    		"SBDATO6":               (25, 30, "slf_op_4"), 
    		"SBDATO7":               (25, 30, "slf_op_5"), 
    		"SBRWI":                 (25, 29, "lutff_4/in_0"), 
    		"SBSTBI":                (25, 29, "lutff_3/in_0"), 
    		"SCLI":                  (25, 29, "lutff_2/in_1"), 
    		"SCLO":                  (25, 29, "slf_op_3"), 
    		"SCLOE":                 (25, 29, "slf_op_4"), 
    		"SDAI":                  (25, 29, "lutff_1/in_1"), 
    		"SDAO":                  (25, 29, "slf_op_1"), 
    		"SDAOE":                 (25, 29, "slf_op_2"), 
    		"SDA_INPUT_DELAYED":     (19, 31, "SDA_input_delay"), 
    		"SDA_OUTPUT_DELAYED":    (19, 31, "SDA_output_delay"), 
    	},
    	("SPI", (0, 0, 0)): {
    		"MCSNO0":                (0, 21, "slf_op_2"), 
    		"MCSNO1":                (0, 21, "slf_op_4"), 
    		"MCSNO2":                (0, 21, "slf_op_7"), 
    		"MCSNO3":                (0, 22, "slf_op_1"), 
    		"MCSNOE0":               (0, 21, "slf_op_3"), 
    		"MCSNOE1":               (0, 21, "slf_op_5"), 
    		"MCSNOE2":               (0, 22, "slf_op_0"), 
    		"MCSNOE3":               (0, 22, "slf_op_2"), 
    		"MI":                    (0, 22, "lutff_0/in_1"), 
    		"MO":                    (0, 20, "slf_op_6"), 
    		"MOE":                   (0, 20, "slf_op_7"), 
    		"SBACKO":                (0, 20, "slf_op_1"), 
    		"SBADRI0":               (0, 19, "lutff_1/in_1"), 
    		"SBADRI1":               (0, 19, "lutff_2/in_1"), 
    		"SBADRI2":               (0, 20, "lutff_0/in_3"), 
    		"SBADRI3":               (0, 20, "lutff_1/in_3"), 
    		"SBADRI4":               (0, 20, "lutff_2/in_3"), 
    		"SBADRI5":               (0, 20, "lutff_3/in_3"), 
    		"SBADRI6":               (0, 20, "lutff_4/in_3"), 
    		"SBADRI7":               (0, 20, "lutff_5/in_3"), 
    		"SBCLKI":                (0, 20, "clk"), 
    		"SBDATI0":               (0, 19, "lutff_1/in_3"), 
    		"SBDATI1":               (0, 19, "lutff_2/in_3"), 
    		"SBDATI2":               (0, 19, "lutff_3/in_3"), 
    		"SBDATI3":               (0, 19, "lutff_4/in_3"), 
    		"SBDATI4":               (0, 19, "lutff_5/in_3"), 
    		"SBDATI5":               (0, 19, "lutff_6/in_3"), 
    		"SBDATI6":               (0, 19, "lutff_7/in_3"), 
    		"SBDATI7":               (0, 19, "lutff_0/in_1"), 
    		"SBDATO0":               (0, 19, "slf_op_1"), 
    		"SBDATO1":               (0, 19, "slf_op_2"), 
    		"SBDATO2":               (0, 19, "slf_op_3"), 
    		"SBDATO3":               (0, 19, "slf_op_4"), 
    		"SBDATO4":               (0, 19, "slf_op_5"), 
    		"SBDATO5":               (0, 19, "slf_op_6"), 
    		"SBDATO6":               (0, 19, "slf_op_7"), 
    		"SBDATO7":               (0, 20, "slf_op_0"), 
    		"SBRWI":                 (0, 19, "lutff_0/in_3"), 
    		"SBSTBI":                (0, 20, "lutff_6/in_3"), 
    		"SCKI":                  (0, 22, "lutff_1/in_1"), 
    		"SCKO":                  (0, 21, "slf_op_0"), 
    		"SCKOE":                 (0, 21, "slf_op_1"), 
    		"SCSNI":                 (0, 22, "lutff_2/in_1"), 
    		"SI":                    (0, 22, "lutff_7/in_3"), 
    		"SO":                    (0, 20, "slf_op_4"), 
    		"SOE":                   (0, 20, "slf_op_5"), 
    		"SPIIRQ":                (0, 20, "slf_op_2"), 
    		"SPIWKUP":               (0, 20, "slf_op_3"), 
    		"SPI_ENABLE_0":          (7, 0, "cbit2usealt_in_0"), 
    		"SPI_ENABLE_1":          (7, 0, "cbit2usealt_in_1"), 
    		"SPI_ENABLE_2":          (6, 0, "cbit2usealt_in_0"), 
    		"SPI_ENABLE_3":          (6, 0, "cbit2usealt_in_1"), 
    	},
    	("SPI", (25, 0, 1)): {
    		"MCSNO0":                (25, 21, "slf_op_2"), 
    		"MCSNO1":                (25, 21, "slf_op_4"), 
    		"MCSNO2":                (25, 21, "slf_op_7"), 
    		"MCSNO3":                (25, 22, "slf_op_1"), 
    		"MCSNOE0":               (25, 21, "slf_op_3"), 
    		"MCSNOE1":               (25, 21, "slf_op_5"), 
    		"MCSNOE2":               (25, 22, "slf_op_0"), 
    		"MCSNOE3":               (25, 22, "slf_op_2"), 
    		"MI":                    (25, 22, "lutff_0/in_1"), 
    		"MO":                    (25, 20, "slf_op_6"), 
    		"MOE":                   (25, 20, "slf_op_7"), 
    		"SBACKO":                (25, 20, "slf_op_1"), 
    		"SBADRI0":               (25, 19, "lutff_1/in_1"), 
    		"SBADRI1":               (25, 19, "lutff_2/in_1"), 
    		"SBADRI2":               (25, 20, "lutff_0/in_3"), 
    		"SBADRI3":               (25, 20, "lutff_1/in_3"), 
    		"SBADRI4":               (25, 20, "lutff_2/in_3"), 
    		"SBADRI5":               (25, 20, "lutff_3/in_3"), 
    		"SBADRI6":               (25, 20, "lutff_4/in_3"), 
    		"SBADRI7":               (25, 20, "lutff_5/in_3"), 
    		"SBCLKI":                (25, 20, "clk"), 
    		"SBDATI0":               (25, 19, "lutff_1/in_3"), 
    		"SBDATI1":               (25, 19, "lutff_2/in_3"), 
    		"SBDATI2":               (25, 19, "lutff_3/in_3"), 
    		"SBDATI3":               (25, 19, "lutff_4/in_3"), 
    		"SBDATI4":               (25, 19, "lutff_5/in_3"), 
    		"SBDATI5":               (25, 19, "lutff_6/in_3"), 
    		"SBDATI6":               (25, 19, "lutff_7/in_3"), 
    		"SBDATI7":               (25, 19, "lutff_0/in_1"), 
    		"SBDATO0":               (25, 19, "slf_op_1"), 
    		"SBDATO1":               (25, 19, "slf_op_2"), 
    		"SBDATO2":               (25, 19, "slf_op_3"), 
    		"SBDATO3":               (25, 19, "slf_op_4"), 
    		"SBDATO4":               (25, 19, "slf_op_5"), 
    		"SBDATO5":               (25, 19, "slf_op_6"), 
    		"SBDATO6":               (25, 19, "slf_op_7"), 
    		"SBDATO7":               (25, 20, "slf_op_0"), 
    		"SBRWI":                 (25, 19, "lutff_0/in_3"), 
    		"SBSTBI":                (25, 20, "lutff_6/in_3"), 
    		"SCKI":                  (25, 22, "lutff_1/in_1"), 
    		"SCKO":                  (25, 21, "slf_op_0"), 
    		"SCKOE":                 (25, 21, "slf_op_1"), 
    		"SCSNI":                 (25, 22, "lutff_2/in_1"), 
    		"SI":                    (25, 22, "lutff_7/in_3"), 
    		"SO":                    (25, 20, "slf_op_4"), 
    		"SOE":                   (25, 20, "slf_op_5"), 
    		"SPIIRQ":                (25, 20, "slf_op_2"), 
    		"SPIWKUP":               (25, 20, "slf_op_3"), 
    		"SPI_ENABLE_0":          (23, 0, "cbit2usealt_in_0"), 
    		"SPI_ENABLE_1":          (24, 0, "cbit2usealt_in_0"), 
    		"SPI_ENABLE_2":          (23, 0, "cbit2usealt_in_1"), 
    		"SPI_ENABLE_3":          (24, 0, "cbit2usealt_in_1"), 
    	},
    	("LEDDA_IP", (0, 31, 2)): {
    		"LEDDADDR0":             (0, 28, "lutff_4/in_0"), 
    		"LEDDADDR1":             (0, 28, "lutff_5/in_0"), 
    		"LEDDADDR2":             (0, 28, "lutff_6/in_0"), 
    		"LEDDADDR3":             (0, 28, "lutff_7/in_0"), 
    		"LEDDCLK":               (0, 29, "clk"), 
    		"LEDDCS":                (0, 28, "lutff_2/in_0"), 
    		"LEDDDAT0":              (0, 28, "lutff_2/in_1"), 
    		"LEDDDAT1":              (0, 28, "lutff_3/in_1"), 
    		"LEDDDAT2":              (0, 28, "lutff_4/in_1"), 
    		"LEDDDAT3":              (0, 28, "lutff_5/in_1"), 
    		"LEDDDAT4":              (0, 28, "lutff_6/in_1"), 
    		"LEDDDAT5":              (0, 28, "lutff_7/in_1"), 
    		"LEDDDAT6":              (0, 28, "lutff_0/in_0"), 
    		"LEDDDAT7":              (0, 28, "lutff_1/in_0"), 
    		"LEDDDEN":               (0, 28, "lutff_1/in_1"), 
    		"LEDDEXE":               (0, 28, "lutff_0/in_1"), 
    		"LEDDON":                (0, 29, "slf_op_0"), 
    		"PWMOUT0":               (0, 28, "slf_op_4"), 
    		"PWMOUT1":               (0, 28, "slf_op_5"), 
    		"PWMOUT2":               (0, 28, "slf_op_6"), 
    	},
        ("IO_I3C", (25, 27, 0)): {
            "PU_ENB":                (25, 27, "lutff_6/in_0"),
            "WEAK_PU_ENB":           (25, 27, "lutff_4/in_0"),
            "PACKAGE_PIN":           (19, 31, 0)
        },
        ("IO_I3C", (25, 27, 1)): {
            "PU_ENB":                (25, 27, "lutff_7/in_0"),
            "WEAK_PU_ENB":           (25, 27, "lutff_5/in_0"),
            "PACKAGE_PIN":           (19, 31, 1)
        }
    },

    "u4k" : {
        ("SPI", (0, 0, 0)): {
            "MCSNO0":                (0, 3, "slf_op_1"), 
            "MCSNO1":                (0, 3, "slf_op_3"), 
            "MCSNO2":                (0, 3, "slf_op_6"), 
            "MCSNO3":                (0, 4, "slf_op_0"), 
            "MCSNOE0":               (0, 3, "slf_op_2"), 
            "MCSNOE1":               (0, 3, "slf_op_4"), 
            "MCSNOE2":               (0, 3, "slf_op_7"), 
            "MCSNOE3":               (0, 4, "slf_op_1"), 
            "MI":                    (0, 2, "lutff_0/in_1"), 
            "MO":                    (0, 2, "slf_op_5"), 
            "MOE":                   (0, 2, "slf_op_6"), 
            "SBACKO":                (0, 2, "slf_op_0"), 
            "SBADRI0":               (0, 1, "lutff_1/in_1"), 
            "SBADRI1":               (0, 1, "lutff_2/in_1"), 
            "SBADRI2":               (0, 2, "lutff_0/in_3"), 
            "SBADRI3":               (0, 2, "lutff_1/in_3"), 
            "SBADRI4":               (0, 2, "lutff_2/in_3"), 
            "SBADRI5":               (0, 2, "lutff_3/in_3"), 
            "SBADRI6":               (0, 2, "lutff_4/in_3"), 
            "SBADRI7":               (0, 2, "lutff_5/in_3"), 
            "SBCLKI":                (0, 1, "clk"), 
            "SBDATI0":               (0, 1, "lutff_1/in_3"), 
            "SBDATI1":               (0, 1, "lutff_2/in_3"), 
            "SBDATI2":               (0, 1, "lutff_3/in_3"), 
            "SBDATI3":               (0, 1, "lutff_4/in_3"), 
            "SBDATI4":               (0, 1, "lutff_5/in_3"), 
            "SBDATI5":               (0, 1, "lutff_6/in_3"), 
            "SBDATI6":               (0, 1, "lutff_7/in_3"), 
            "SBDATI7":               (0, 1, "lutff_0/in_1"), 
            "SBDATO0":               (0, 1, "slf_op_0"), 
            "SBDATO1":               (0, 1, "slf_op_1"), 
            "SBDATO2":               (0, 1, "slf_op_2"), 
            "SBDATO3":               (0, 1, "slf_op_3"), 
            "SBDATO4":               (0, 1, "slf_op_4"), 
            "SBDATO5":               (0, 1, "slf_op_5"), 
            "SBDATO6":               (0, 1, "slf_op_6"), 
            "SBDATO7":               (0, 1, "slf_op_7"), 
            "SBRWI":                 (0, 1, "lutff_0/in_3"), 
            "SBSTBI":                (0, 2, "lutff_6/in_3"), 
            "SCKI":                  (0, 2, "lutff_1/in_1"), 
            "SCKO":                  (0, 2, "slf_op_7"), 
            "SCKOE":                 (0, 3, "slf_op_0"), 
            "SCSNI":                 (0, 2, "lutff_2/in_1"), 
            "SI":                    (0, 2, "lutff_7/in_3"), 
            "SO":                    (0, 2, "slf_op_3"), 
            "SOE":                   (0, 2, "slf_op_4"), 
            "SPIIRQ":                (0, 2, "slf_op_1"), 
            "SPIWKUP":               (0, 2, "slf_op_2"), 
            "SPI_ENABLE_0":          (7, 0, "cbit2usealt_in_0"), 
            "SPI_ENABLE_1":          (6, 0, "cbit2usealt_in_0"), 
            "SPI_ENABLE_2":          (7, 0, "cbit2usealt_in_1"), 
            "SPI_ENABLE_3":          (6, 0, "cbit2usealt_in_1"), 
        },
        ("SPI", (25, 0, 1)): {
            "MCSNO0":                (25, 3, "slf_op_1"), 
            "MCSNO1":                (25, 3, "slf_op_3"), 
            "MCSNO2":                (25, 3, "slf_op_6"), 
            "MCSNO3":                (25, 4, "slf_op_0"), 
            "MCSNOE0":               (25, 3, "slf_op_2"), 
            "MCSNOE1":               (25, 3, "slf_op_4"), 
            "MCSNOE2":               (25, 3, "slf_op_7"), 
            "MCSNOE3":               (25, 4, "slf_op_1"), 
            "MI":                    (25, 2, "lutff_0/in_1"), 
            "MO":                    (25, 2, "slf_op_5"), 
            "MOE":                   (25, 2, "slf_op_6"), 
            "SBACKO":                (25, 2, "slf_op_0"), 
            "SBADRI0":               (25, 1, "lutff_1/in_1"), 
            "SBADRI1":               (25, 1, "lutff_2/in_1"), 
            "SBADRI2":               (25, 2, "lutff_0/in_3"), 
            "SBADRI3":               (25, 2, "lutff_1/in_3"), 
            "SBADRI4":               (25, 2, "lutff_2/in_3"), 
            "SBADRI5":               (25, 2, "lutff_3/in_3"), 
            "SBADRI6":               (25, 2, "lutff_4/in_3"), 
            "SBADRI7":               (25, 2, "lutff_5/in_3"), 
            "SBCLKI":                (25, 1, "clk"), 
            "SBDATI0":               (25, 1, "lutff_1/in_3"), 
            "SBDATI1":               (25, 1, "lutff_2/in_3"), 
            "SBDATI2":               (25, 1, "lutff_3/in_3"), 
            "SBDATI3":               (25, 1, "lutff_4/in_3"), 
            "SBDATI4":               (25, 1, "lutff_5/in_3"), 
            "SBDATI5":               (25, 1, "lutff_6/in_3"), 
            "SBDATI6":               (25, 1, "lutff_7/in_3"), 
            "SBDATI7":               (25, 1, "lutff_0/in_1"), 
            "SBDATO0":               (25, 1, "slf_op_0"), 
            "SBDATO1":               (25, 1, "slf_op_1"), 
            "SBDATO2":               (25, 1, "slf_op_2"), 
            "SBDATO3":               (25, 1, "slf_op_3"), 
            "SBDATO4":               (25, 1, "slf_op_4"), 
            "SBDATO5":               (25, 1, "slf_op_5"), 
            "SBDATO6":               (25, 1, "slf_op_6"), 
            "SBDATO7":               (25, 1, "slf_op_7"), 
            "SBRWI":                 (25, 1, "lutff_0/in_3"), 
            "SBSTBI":                (25, 2, "lutff_6/in_3"), 
            "SCKI":                  (25, 2, "lutff_1/in_1"), 
            "SCKO":                  (25, 2, "slf_op_7"), 
            "SCKOE":                 (25, 3, "slf_op_0"), 
            "SCSNI":                 (25, 2, "lutff_2/in_1"), 
            "SI":                    (25, 2, "lutff_7/in_3"), 
            "SO":                    (25, 2, "slf_op_3"), 
            "SOE":                   (25, 2, "slf_op_4"), 
            "SPIIRQ":                (25, 2, "slf_op_1"), 
            "SPIWKUP":               (25, 2, "slf_op_2"), 
            "SPI_ENABLE_0":          (24, 0, "cbit2usealt_in_0"), 
            "SPI_ENABLE_1":          (24, 0, "cbit2usealt_in_1"), 
            "SPI_ENABLE_2":          (23, 0, "cbit2usealt_in_0"), 
            "SPI_ENABLE_3":          (23, 0, "cbit2usealt_in_1"), 
        },
        ("I2C", (0, 21, 0)): {
            "I2CIRQ":                (0, 20, "slf_op_7"), 
            "I2CWKUP":               (0, 19, "slf_op_5"), 
            "I2C_ENABLE_0":          (13, 21, "cbit2usealt_in_0"), 
            "I2C_ENABLE_1":          (12, 21, "cbit2usealt_in_1"), 
            "SBACKO":                (0, 20, "slf_op_6"), 
            "SBADRI0":               (0, 20, "lutff_1/in_0"), 
            "SBADRI1":               (0, 20, "lutff_2/in_0"), 
            "SBADRI2":               (0, 20, "lutff_3/in_0"), 
            "SBADRI3":               (0, 20, "lutff_4/in_0"), 
            "SBADRI4":               (0, 20, "lutff_5/in_0"), 
            "SBADRI5":               (0, 20, "lutff_6/in_0"), 
            "SBADRI6":               (0, 20, "lutff_7/in_0"), 
            "SBADRI7":               (0, 19, "lutff_2/in_0"), 
            "SBCLKI":                (0, 20, "clk"), 
            "SBDATI0":               (0, 19, "lutff_5/in_0"), 
            "SBDATI1":               (0, 19, "lutff_6/in_0"), 
            "SBDATI2":               (0, 19, "lutff_7/in_0"), 
            "SBDATI3":               (0, 20, "lutff_0/in_3"), 
            "SBDATI4":               (0, 20, "lutff_5/in_1"), 
            "SBDATI5":               (0, 20, "lutff_6/in_1"), 
            "SBDATI6":               (0, 20, "lutff_7/in_1"), 
            "SBDATI7":               (0, 20, "lutff_0/in_0"), 
            "SBDATO0":               (0, 19, "slf_op_6"), 
            "SBDATO1":               (0, 19, "slf_op_7"), 
            "SBDATO2":               (0, 20, "slf_op_0"), 
            "SBDATO3":               (0, 20, "slf_op_1"), 
            "SBDATO4":               (0, 20, "slf_op_2"), 
            "SBDATO5":               (0, 20, "slf_op_3"), 
            "SBDATO6":               (0, 20, "slf_op_4"), 
            "SBDATO7":               (0, 20, "slf_op_5"), 
            "SBRWI":                 (0, 19, "lutff_4/in_0"), 
            "SBSTBI":                (0, 19, "lutff_3/in_0"), 
            "SCLI":                  (0, 19, "lutff_2/in_1"), 
            "SCLO":                  (0, 19, "slf_op_3"), 
            "SCLOE":                 (0, 19, "slf_op_4"), 
            "SDAI":                  (0, 19, "lutff_1/in_1"), 
            "SDAO":                  (0, 19, "slf_op_1"), 
            "SDAOE":                 (0, 19, "slf_op_2"), 
            "SDA_INPUT_DELAYED":     (12, 21, "SDA_input_delay"), 
            "SDA_OUTPUT_DELAYED":    (12, 21, "SDA_output_delay"), 
        },
        ("I2C", (25, 21, 0)): {
            "I2CIRQ":                (25, 20, "slf_op_7"), 
            "I2CWKUP":               (25, 19, "slf_op_5"), 
            "I2C_ENABLE_0":          (19, 21, "cbit2usealt_in_1"), 
            "I2C_ENABLE_1":          (19, 21, "cbit2usealt_in_0"), 
            "SBACKO":                (25, 20, "slf_op_6"), 
            "SBADRI0":               (25, 20, "lutff_1/in_0"), 
            "SBADRI1":               (25, 20, "lutff_2/in_0"), 
            "SBADRI2":               (25, 20, "lutff_3/in_0"), 
            "SBADRI3":               (25, 20, "lutff_4/in_0"), 
            "SBADRI4":               (25, 20, "lutff_5/in_0"), 
            "SBADRI5":               (25, 20, "lutff_6/in_0"), 
            "SBADRI6":               (25, 20, "lutff_7/in_0"), 
            "SBADRI7":               (25, 19, "lutff_2/in_0"), 
            "SBCLKI":                (25, 20, "clk"), 
            "SBDATI0":               (25, 19, "lutff_5/in_0"), 
            "SBDATI1":               (25, 19, "lutff_6/in_0"), 
            "SBDATI2":               (25, 19, "lutff_7/in_0"), 
            "SBDATI3":               (25, 20, "lutff_0/in_3"), 
            "SBDATI4":               (25, 20, "lutff_5/in_1"), 
            "SBDATI5":               (25, 20, "lutff_6/in_1"), 
            "SBDATI6":               (25, 20, "lutff_7/in_1"), 
            "SBDATI7":               (25, 20, "lutff_0/in_0"), 
            "SBDATO0":               (25, 19, "slf_op_6"), 
            "SBDATO1":               (25, 19, "slf_op_7"), 
            "SBDATO2":               (25, 20, "slf_op_0"), 
            "SBDATO3":               (25, 20, "slf_op_1"), 
            "SBDATO4":               (25, 20, "slf_op_2"), 
            "SBDATO5":               (25, 20, "slf_op_3"), 
            "SBDATO6":               (25, 20, "slf_op_4"), 
            "SBDATO7":               (25, 20, "slf_op_5"), 
            "SBRWI":                 (25, 19, "lutff_4/in_0"), 
            "SBSTBI":                (25, 19, "lutff_3/in_0"), 
            "SCLI":                  (25, 19, "lutff_2/in_1"), 
            "SCLO":                  (25, 19, "slf_op_3"), 
            "SCLOE":                 (25, 19, "slf_op_4"), 
            "SDAI":                  (25, 19, "lutff_1/in_1"), 
            "SDAO":                  (25, 19, "slf_op_1"), 
            "SDAOE":                 (25, 19, "slf_op_2"), 
            "SDA_INPUT_DELAYED":     (19, 21, "SDA_input_delay"), 
            "SDA_OUTPUT_DELAYED":    (19, 21, "SDA_output_delay"), 
        },
        ("HFOSC", (0, 21, 1)) : {
            "CLKHFPU":                      (0, 19, "lutff_0/in_1"),
            "CLKHFEN":                      (0, 19, "lutff_7/in_3"),
            "CLKHF":                        (0, 19, "glb_netwk_4"),
            "CLKLF_FABRIC":                 (0, 18, "slf_op_7"),
            "CLKHF_DIV_1":                  (0, 16, "CBIT_4"),
            "CLKHF_DIV_0":                  (0, 16, "CBIT_3")
        },
        ("LFOSC", (25, 21, 1)) : {
            "CLKLFPU":                      (25, 19, "lutff_0/in_1"),
            "CLKLFEN":                      (25, 19, "lutff_7/in_3"),
            "CLKLF":                        (25, 19, "glb_netwk_5"),
            "CLKLF_FABRIC":                 (25, 19, "slf_op_0")
        },
        ("SMCCLK", (25, 3, 0)) : {
            "CLK":                          (25, 3, "slf_op_5")
        },
        ("LED_DRV_CUR", (25, 21, 2)) : {
            "LED_DRV_CUR_EN":               (25, 19, "CBIT_5"),
            "EN":                           (25, 19, "lutff_6/in_3"),
        },
        ("RGB_DRV", (0, 21, 3)) : {
            "RGB_DRV_EN":                   (0, 18, "CBIT_5"),
            "RGB0_CURRENT_0":               (0, 18, "CBIT_6"),
            "RGB0_CURRENT_1":               (0, 18, "CBIT_7"),
            "RGB0_CURRENT_2":               (0, 19, "CBIT_0"),
            "RGB0_CURRENT_3":               (0, 19, "CBIT_1"),
            "RGB0_CURRENT_4":               (0, 19, "CBIT_2"),
            "RGB0_CURRENT_5":               (0, 19, "CBIT_3"),
            "RGB1_CURRENT_0":               (0, 19, "CBIT_4"),
            "RGB1_CURRENT_1":               (0, 19, "CBIT_5"),
            "RGB1_CURRENT_2":               (0, 19, "CBIT_6"),
            "RGB1_CURRENT_3":               (0, 19, "CBIT_7"),
            "RGB1_CURRENT_4":               (0, 20, "CBIT_0"),
            "RGB1_CURRENT_5":               (0, 20, "CBIT_1"),
            "RGB2_CURRENT_0":               (0, 20, "CBIT_2"),
            "RGB2_CURRENT_1":               (0, 20, "CBIT_3"),
            "RGB2_CURRENT_2":               (0, 20, "CBIT_4"),
            "RGB2_CURRENT_3":               (0, 20, "CBIT_5"),
            "RGB2_CURRENT_4":               (0, 20, "CBIT_6"),
            "RGB2_CURRENT_5":               (0, 20, "CBIT_7"),
            "RGBLEDEN":                     (0, 20, "lutff_1/in_1"),
            "RGB0PWM":                      (0, 20, "lutff_2/in_1"),
            "RGB1PWM":                      (0, 20, "lutff_3/in_1"),
            "RGB2PWM":                      (0, 20, "lutff_4/in_1"),
            "RGB0":                         (13, 21, 0),
            "RGB1":                         (12, 21, 0),
            "RGB2":                         (8, 21, 0)
        },
    }
}

iotile_full_db = parse_db(iceboxdb.database_io_txt)
logictile_db = parse_db(iceboxdb.database_logic_txt, "1k")
logictile_5k_db = parse_db(iceboxdb.database_logic_txt, "5k")
logictile_8k_db = parse_db(iceboxdb.database_logic_txt, "8k")
logictile_384_db = parse_db(iceboxdb.database_logic_txt, "384")
rambtile_db = parse_db(iceboxdb.database_ramb_txt, "1k")
ramttile_db = parse_db(iceboxdb.database_ramt_txt, "1k")
rambtile_8k_db = parse_db(iceboxdb.database_ramb_8k_txt, "8k")
ramttile_8k_db = parse_db(iceboxdb.database_ramt_8k_txt, "8k")

ipcon_5k_db = parse_db(iceboxdb.database_ipcon_5k_txt, "5k")
dsp0_5k_db = parse_db(iceboxdb.database_dsp0_5k_txt, "5k")
dsp1_5k_db = parse_db(iceboxdb.database_dsp1_5k_txt, "5k")

#This bit doesn't exist in DB because icecube won't ever set it,
#but it exists
dsp1_5k_db.append([["B4[7]"], "IpConfig", "CBIT_5"])


dsp2_5k_db = parse_db(iceboxdb.database_dsp2_5k_txt, "5k")
dsp3_5k_db = parse_db(iceboxdb.database_dsp3_5k_txt, "5k")

dsp3_5k_db.append([["B2[7]"], "IpConfig", "CBIT_3"])   # for u4k HFOSC.CLKHF_DIV
dsp3_5k_db.append([["B5[7]"], "IpConfig", "CBIT_4"])


#Add missing LC_ bits to DSP and IPCon databases
for db_to_fix in [ipcon_5k_db, dsp0_5k_db, dsp1_5k_db, dsp2_5k_db, dsp3_5k_db]:
    for entry in db_to_fix:
        if len(entry) >= 2 and entry[1].startswith("LC_"):
            for lentry in logictile_5k_db:
                if len(lentry) >= 2 and lentry[1] == entry[1]:
                    entry[0] = lentry[0]

iotile_l_db = list()
iotile_r_db = list()
iotile_t_db = list()
iotile_b_db = list()

for entry in iotile_full_db:
    if entry[1] == "buffer" and entry[2].startswith("IO_L."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_l_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_R."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_r_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_T."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_t_db.append(new_entry)
    elif entry[1] == "buffer" and entry[2].startswith("IO_B."):
        new_entry = entry[:]
        new_entry[2] = new_entry[2][5:]
        iotile_b_db.append(new_entry)
    else:
        iotile_l_db.append(entry)
        iotile_r_db.append(entry)
        iotile_t_db.append(entry)
        iotile_b_db.append(entry)

logictile_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_db.append([["B1[50]"], "CarryInSet"])

logictile_5k_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_5k_db.append([["B1[50]"], "CarryInSet"])

logictile_8k_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_8k_db.append([["B1[50]"], "CarryInSet"])

logictile_384_db.append([["B1[49]"], "buffer", "carry_in", "carry_in_mux"])
logictile_384_db.append([["B1[50]"], "CarryInSet"])

# The 5k series has a couple of extra IO configuration bits. Add them in to a copy of the db here
iotile_t_5k_db = list(iotile_t_db)
iotile_t_5k_db.append([["B14[15]"], "IoCtrl", "padeb_test_1"])
iotile_t_5k_db.append([["B15[14]"], "IoCtrl", "padeb_test_0"])
iotile_t_5k_db.append([["B7[10]"], "IoCtrl", "cf_bit_32"])
iotile_t_5k_db.append([["B6[10]"], "IoCtrl", "cf_bit_33"])
iotile_t_5k_db.append([["B7[15]"], "IoCtrl", "cf_bit_34"])
iotile_t_5k_db.append([["B6[15]"], "IoCtrl", "cf_bit_35"])
iotile_t_5k_db.append([["B13[10]"], "IoCtrl", "cf_bit_36"])
iotile_t_5k_db.append([["B12[10]"], "IoCtrl", "cf_bit_37"])
iotile_t_5k_db.append([["B13[15]"], "IoCtrl", "cf_bit_38"])
iotile_t_5k_db.append([["B12[15]"], "IoCtrl", "cf_bit_39"])
iotile_t_5k_db.append([["B10[3]"], "IpConfig", "cbit2usealt_in_0"])
iotile_t_5k_db.append([["B12[2]"], "IpConfig", "cbit2usealt_in_1"])
iotile_t_5k_db.append([["B12[3]"], "IpConfig", "SDA_input_delay"])
iotile_t_5k_db.append([["B15[3]"], "IpConfig", "SDA_output_delay"])

iotile_b_5k_db = list(iotile_b_db)
iotile_b_5k_db.append([["B14[15]"], "IoCtrl", "padeb_test_1"])
iotile_b_5k_db.append([["B15[14]"], "IoCtrl", "padeb_test_0"])
iotile_b_5k_db.append([["B7[10]"], "IoCtrl", "cf_bit_32"])
iotile_b_5k_db.append([["B6[10]"], "IoCtrl", "cf_bit_33"])
iotile_b_5k_db.append([["B7[15]"], "IoCtrl", "cf_bit_34"])
iotile_b_5k_db.append([["B6[15]"], "IoCtrl", "cf_bit_35"])
iotile_b_5k_db.append([["B13[10]"], "IoCtrl", "cf_bit_36"])
iotile_b_5k_db.append([["B12[10]"], "IoCtrl", "cf_bit_37"])
iotile_b_5k_db.append([["B13[15]"], "IoCtrl", "cf_bit_38"])
iotile_b_5k_db.append([["B12[15]"], "IoCtrl", "cf_bit_39"])
iotile_b_5k_db.append([["B10[3]"], "IpConfig", "cbit2usealt_in_0"])
iotile_b_5k_db.append([["B12[2]"], "IpConfig", "cbit2usealt_in_1"])
iotile_b_5k_db.append([["B12[3]"], "IpConfig", "SDA_input_delay"])
iotile_b_5k_db.append([["B15[3]"], "IpConfig", "SDA_output_delay"])

for db in [iotile_l_db, iotile_r_db, iotile_t_db, iotile_b_db, iotile_t_5k_db, iotile_b_5k_db, logictile_db, logictile_5k_db, logictile_8k_db, logictile_384_db, rambtile_db, ramttile_db, rambtile_8k_db, ramttile_8k_db, dsp0_5k_db, dsp1_5k_db, dsp2_5k_db, dsp3_5k_db, ipcon_5k_db]:
    for entry in db:
        if entry[1] in ("buffer", "routing"):
            entry[2] = netname_normalize(entry[2],
                                         ramb=(db == rambtile_db),
                                         ramt=(db == ramttile_db),
                                         ramb_8k=(db == rambtile_8k_db),
                                         ramt_8k=(db == ramttile_8k_db))
            entry[3] = netname_normalize(entry[3],
                                         ramb=(db == rambtile_db),
                                         ramt=(db == ramttile_db),
                                         ramb_8k=(db == rambtile_8k_db),
                                         ramt_8k=(db == ramttile_8k_db))
    unique_entries = dict()
    while db:
        entry = db.pop()
        key = " ".join(entry[1:]) + str(entry)
        unique_entries[key] = entry
    for key in sorted(unique_entries):
        db.append(unique_entries[key])

if __name__ == "__main__":
    run_checks()
