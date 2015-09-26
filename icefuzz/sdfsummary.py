#!/usr/bin/env python3

import fileinput
import re

intext = []
for line in fileinput.input():
    line = re.sub("//.*", "", line)
    intext.append(line)

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

sdfdata, _ = parse_sdf("".join(intext), 0)

def generalize_instances(expr):
    if type(expr) is list:
        if len(expr) == 2 and expr[0] == "INSTANCE":
            expr[1] = "*"
        for child in expr:
            generalize_instances(child)

generalize_instances(sdfdata)

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

sdfdata = uniquify_cells(sdfdata)
# dump_sdf(sdfdata)

iopaths = dict()

for cell in sdfdata:
    if cell[0] != "CELL":
        continue

    celltype = None
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

            iopaths.setdefault(celltype, set())

        if stmt[0] == "DELAY":
            assert stmt[1][0] == "ABSOLUTE"
            for iopath in stmt[1][1:]:
                assert iopath[0] == "IOPATH"
                iopaths[celltype].add(sdf_to_string(iopath))

        if stmt[0] == "TIMINGCHECK":
            for iopath in stmt[1:]:
                iopaths[celltype].add(sdf_to_string(iopath))

convert = lambda text: int(text) if text.isdigit() else text.lower()
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
alphanum_key_list = lambda l: [len(l)] + [ alphanum_key(s) for s in l ]

for celltype in sorted(iopaths, key=alphanum_key):
    print("CELL %s" % celltype)
    path_list = list()
    path_list_lens = list()
    for iopath in iopaths[celltype]:
        iopath = iopath.replace("(posedge ", "posedge:")
        iopath = iopath.replace("(negedge ", "negedge:")
        iopath = iopath.replace("(", "")
        iopath = iopath.replace(")", "")
        iopath = iopath.split()
        for i in range(len(iopath)):
            if i < len(path_list_lens):
                path_list_lens[i] = max(path_list_lens[i], len(iopath[i]))
            else:
                path_list_lens.append(len(iopath[i]))
        path_list.append(iopath)

    for iopath in sorted(path_list, key=alphanum_key_list):
        for i in range(len(iopath)):
            print("%s%-*s" % ("  " if i != 0 else "", path_list_lens[i] if i != len(iopath)-1 else 0, iopath[i]), end="")
        print()
    print()

