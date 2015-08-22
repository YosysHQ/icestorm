#!/usr/bin/env python3

with open("../icebox/iceboxdb.py", "w") as f:
    for i in [ "database_io", "database_logic", "database_ramb", "database_ramt", "database_ramb_8k", "database_ramt_8k" ]:
        print('%s_txt = """' % i, file=f)
        with open("%s.txt" % i, "r") as fi:
            for line in fi:
                print(line, end="", file=f)
        print('"""', file=f)

