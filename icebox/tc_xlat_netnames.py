# Test case for `icebox_asc2hlc': Does net name translation work correctly?
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
from icebox_asc2hlc import translate_netname

def test_netname_translation(ic):
    sys.stderr.write("testing forward netname translation "
                     "for the `%s' device...\n" % ic.device)
    all_tiles = set()
    for x in range(ic.max_x + 1):
        for y in range(ic.max_y + 1):
            if ic.tile(x, y) is not None:
                all_tiles.add((x, y))

    netnames = set()
    failed = False

    for group in ic.group_segments(all_tiles, connect_gb = False):
        is_span = set(net.startswith('sp') for x, y, net in group)
        assert len(is_span) == 1
        if True not in is_span:
            # only span nets are interesting here
            continue

        s = set()
        for seg in group:
            s.add(translate_netname(seg[0], seg[1],
                                    ic.max_x - 1, ic.max_y - 1, seg[2]))
        if len(s) != 1:
            failed = True
            print("translated netnames don't match")
            for seg in group:
                print("%d %d %s" % seg, "->",
                      translate_netname(seg[0], seg[1],
                                        ic.max_x - 1, ic.max_y - 1, seg[2]))
            print()

        for dulpicate_netname in netnames.intersection(s):
            failed = True
            print("duplicate netname: %s" % dulpicate_netname)
            for seg in group:
                print("%d %d %s" % seg, "->",
                      translate_netname(seg[0], seg[1],
                                        ic.max_x - 1, ic.max_y - 1, seg[2]))
            print()

        netnames.update(s)

    if failed:
        sys.stderr.write("ERROR\n")
        sys.exit(1)

def main():
    ic = icebox.iceconfig()
    ic.setup_empty_384()
    test_netname_translation(ic)

    ic = icebox.iceconfig()
    ic.setup_empty_1k()
    test_netname_translation(ic)

    ic = icebox.iceconfig()
    ic.setup_empty_8k()
    test_netname_translation(ic)

if __name__ == '__main__':
    main()
