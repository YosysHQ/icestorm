#!/usr/bin/env python3
import os

device_class = os.getenv("ICEDEVICE")

with open("../icebox/iceboxdb.py", "w") as f:
    files = [ "database_io", "database_logic", "database_ramb", "database_ramt"]
    for device_class in ["5k", "8k"]:
      files.append("database_ramb_" + device_class)
      files.append("database_ramt_" + device_class)
    for i in files:
        print('%s_txt = """' % i, file=f)
        with open("%s.txt" % i, "r") as fi:
            for line in fi:
                print(line, end="", file=f)
        print('"""', file=f)
