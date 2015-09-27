#!/usr/bin/env python3

import getopt, sys, re

database = dict()
sdf_inputs = list()
txt_inputs = list()
output_sdf = False


def usage():
    print("""
Usage: python3 timings.py [options] [sdf_file..]

    -t filename
        read TXT file

    -s
        output SDF (not TXT) format
""")
    sys.exit(0)


try:
    opts, args = getopt.getopt(sys.argv[1:], "t:s")
except:
    usage()

for o, a in opts:
    if o == "-t":
        txt_inputs.append(a)
    elif o == "-s":
        output_sdf = True
    else:
        usage()

sdf_inputs += args


def skip_whitespace(text, cursor):
    while cursor < len(text) and text[cursor] in [" ", "\t", "\r", "\n"]:
        cursor += 1
    return cursor


def parse_sdf(text, cursor):
    cursor = skip_whitespace(text, cursor)

    if cursor < len(text) and text[cursor] == "(":
        expr = []
        cursor += 1
        while cursor < len(text) and text[cursor] != ")":
            child, cursor = parse_sdf(text, cursor)
            expr.append(child)
            cursor = skip_whitespace(text, cursor)
        return expr, cursor+1

    if cursor < len(text) and text[cursor] == '"':
        expr = '"'
        cursor += 1
        while cursor < len(text) and text[cursor] != '"':
            expr += text[cursor]
            cursor += 1
        return expr + '"', cursor+1

    expr = ""
    while cursor < len(text) and text[cursor] not in [" ", "\t", "\r", "\n", "(", ")"]:
        expr += text[cursor]
        cursor += 1
    return expr, cursor


def sdf_to_string(expr):
    if type(expr) is list:
        tokens = []
        tokens.append("(")
        first_child = True
        for child in expr:
            if not first_child:
                tokens.append(" ")
            tokens.append(sdf_to_string(child))
            first_child = False
        tokens.append(")")
        return "".join(tokens)
    else:
        return expr


def dump_sdf(expr, indent=""):
    if type(expr) is list:
        if len(expr) > 0 and expr[0] in ["IOPATH", "SETUP", "HOLD", "CELLTYPE", "INSTANCE", "SDFVERSION",
                "DESIGN", "DATE", "VENDOR", "DIVIDER", "TIMESCALE", "RECOVERY", "REMOVAL"]:
            print(indent + sdf_to_string(expr))
        else:
            print("%s(%s" % (indent, expr[0] if len(expr) > 0 else ""))
            for child in expr[1:]:
                dump_sdf(child, indent + "  ")
            print("%s)" % indent)
    else:
        print("%s%s" % (indent, expr))


def generalize_instances(expr):
    if type(expr) is list:
        if len(expr) == 2 and expr[0] == "INSTANCE":
            expr[1] = "*"
        for child in expr:
            generalize_instances(child)


def list_to_tuple(expr):
    if type(expr) is list:
        tup = []
        for child in expr:
            tup.append(list_to_tuple(child))
        return tuple(tup)
    return expr


def uniquify_cells(expr):
    cache = set()
    filtered_expr = []

    for child in expr:
        t = list_to_tuple(child)
        if t not in cache:
            filtered_expr.append(child)
            cache.add(t)

    return filtered_expr


###########################################
# Parse SDF input files

for filename in sdf_inputs:
    print("### reading SDF file %s" % filename, file=sys.stderr)

    intext = []
    with open(filename, "r") as f:
        for line in f:
            line = re.sub("//.*", "", line)
            intext.append(line)

    sdfdata, _ = parse_sdf("".join(intext), 0)
    generalize_instances(sdfdata)
    sdfdata = uniquify_cells(sdfdata)

    for cell in sdfdata:
        if cell[0] != "CELL":
            continue

        celltype = None

        def add_entry(entry):
            entry = sdf_to_string(entry)
            entry = entry.replace("(posedge ", "posedge:")
            entry = entry.replace("(negedge ", "negedge:")
            entry = entry.replace("(", "")
            entry = entry.replace(")", "")
            entry = entry.split()
            database[celltype].add(tuple(entry))

        for stmt in cell:
            if stmt[0] == "CELLTYPE":
                celltype = stmt[1][1:-1]

                if celltype.startswith("PRE_IO_PIN_TYPE_"):
                    celltype = "PRE_IO_PIN_TYPE"

                if celltype.startswith("Span4Mux"):
                    if celltype == "Span4Mux":
                        celltype = "Span4Mux_v4"
                    elif celltype == "Span4Mux_v":
                        celltype = "Span4Mux_v4"
                    elif celltype == "Span4Mux_h":
                        celltype = "Span4Mux_h4"
                    else:
                        match = re.match("Span4Mux_s(.*)_(h|v)", celltype)
                        celltype = "Span4Mux_%c%d" % (match.group(2), int(match.group(1)))

                if celltype.startswith("Span12Mux"):
                    if celltype == "Span12Mux":
                        celltype = "Span12Mux_v12"
                    elif celltype == "Span12Mux_v":
                        celltype = "Span12Mux_v12"
                    elif celltype == "Span12Mux_h":
                        celltype = "Span12Mux_h12"
                    else:
                        match = re.match("Span12Mux_s(.*)_(h|v)", celltype)
                        celltype = "Span12Mux_%c%d" % (match.group(2), int(match.group(1)))

                database.setdefault(celltype, set())

            if stmt[0] == "DELAY":
                assert stmt[1][0] == "ABSOLUTE"
                for entry in stmt[1][1:]:
                    assert entry[0] == "IOPATH"
                    add_entry(entry)

            if stmt[0] == "TIMINGCHECK":
                for entry in stmt[1:]:
                    add_entry(entry)


###########################################
# Parse TXT input files

for filename in txt_inputs:
    print("### reading TXT file %s" % filename, file=sys.stderr)
    with open(filename, "r") as f:
        celltype = None
        for line in f:
            line = line.split()
            if len(len) > 1:
                if line[0] == "CELL":
                    celltype = line[1]
                else:
                    database[celltype].add(tuple(line))


###########################################
# Create SDF output

convert = lambda text: int(text) if text.isdigit() else text.lower()
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
alphanum_key_list = lambda l: [len(l)] + [ alphanum_key(s) for s in l ]

if output_sdf:
    print("(DELAYFILE")
    print("  (SDFVERSION \"3.0\")")
    print("  (TIMESCALE 1ps)")

    def format_entry(entry):
        text = []
        for i in range(len(entry)):
            if i > 2:
                text.append("(%s)" % entry[i])
            elif entry[i].startswith("posedge:"):
                text.append("(posedge %s)" % entry[i].replace("posedge:", ""))
            elif entry[i].startswith("negedge:"):
                text.append("(negedge %s)" % entry[i].replace("negedge:", ""))
            else:
                text.append(entry[i])
        return " ".join(text)

    for celltype in sorted(database, key=alphanum_key):
        print("  (CELL")
        print("    (CELLTYPE \"%s\")" % celltype)
        print("    (INSTANCE *)")

        delay_abs_entries = list()
        timingcheck_entries = list()
        for entry in sorted(database[celltype], key=alphanum_key_list):
            if entry[0] == "IOPATH":
                delay_abs_entries.append(entry)
            else:
                timingcheck_entries.append(entry)

        if len(delay_abs_entries) != 0:
            print("    (DELAY")
            print("      (ABSOLUTE")
            for entry in delay_abs_entries:
                print("        (%s)" % format_entry(entry))
            print("      )")
            print("    )")

        if len(timingcheck_entries) != 0:
            print("    (TIMINGCHECK")
            for entry in timingcheck_entries:
                print("      (%s)" % format_entry(entry))
            print("    )")

        print("  )")

    print(")")


###########################################
# Create TXT output

else:
    for celltype in sorted(database, key=alphanum_key):
        print("CELL %s" % celltype)
        entries_lens = list()
        for entry in database[celltype]:
            for i in range(len(entry)):
                if i < len(entries_lens):
                    entries_lens[i] = max(entries_lens[i], len(entry[i]))
                else:
                    entries_lens.append(len(entry[i]))
        for entry in sorted(database[celltype], key=alphanum_key_list):
            for i in range(len(entry)):
                print("%s%-*s" % ("  " if i != 0 else "", entries_lens[i] if i != len(entry)-1 else 0, entry[i]), end="")
            print()
        print()

