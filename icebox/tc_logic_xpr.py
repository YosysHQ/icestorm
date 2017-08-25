# Test case for `icebox_asc2hlc' and `icebox_hlc2asc': Does conversion
#   from LUT strings to logic expressions and back work correctly?
# Copyright (C) 2017 Roland Lutz
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys
import icebox
from icebox_asc2hlc import lut_to_logic_expression
from icebox_hlc2asc import logic_expression_to_lut

def main():
    sys.stderr.write("testing conversion from LUT strings "
                     "to logic expressions and back")

    for i in range(65536):
        if i % 4096 == 0:
            sys.stderr.write(".")
            sys.stderr.flush()

        lut = bin(i)[2:].zfill(16)
        s = lut_to_logic_expression(lut, ('a', 'b', 'c', 'd'))
        l = logic_expression_to_lut(s, ('a', 'b', 'c', 'd'))

        if l != lut:
            sys.stderr.write("\nERROR at LUT  = %s\n" % lut)
            sys.stderr.write("stringified   = %s\n" % s)
            sys.stderr.write("resulting LUT = %s\n" % l)
            sys.exit(1)

    sys.stderr.write("\n")

if __name__ == '__main__':
    main()
