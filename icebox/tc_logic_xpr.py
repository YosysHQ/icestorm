# Test case for `icebox_asc2hlc' and `icebox_hlc2asc': Does conversion
#   from LUT strings to logic expressions and back work correctly?
# Copyright (C) 2017 Roland Lutz
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
