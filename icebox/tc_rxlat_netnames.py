# Test case for `icebox_hlc2asc': Does net name translation work correctly?
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
from icebox_asc2hlc import translate_netname
from icebox_hlc2asc import untranslate_netname

def test_netname_translation(ic):
    sys.stderr.write("testing backward netname translation "
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

        netname = translate_netname(group[0][0], group[0][1],
                                    ic.max_x - 1, ic.max_y - 1, group[0][2])
        if netname in netnames:
            failed = True
            print("duplicate netname: %s" % netname)
        netnames.add(netname)

        for x, y, net in group:
            s = untranslate_netname(x, y, ic.max_x - 1, ic.max_y - 1, netname)
            if s != net:
                failed = True
                print("%-20s %s -> %s" % ("%d %d %s" % (x, y, net), netname, s))

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
