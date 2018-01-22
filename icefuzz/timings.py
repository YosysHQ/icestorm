#!/usr/bin/env python3

import getopt, sys, re

ignore_cells = set([
    "ADTTRIBUF", "DL", "GIOBUG", "LUT_MUX", "MUX4",
    "PLL40_2_FEEDBACK_PATH_DELAY", "PLL40_2_FEEDBACK_PATH_EXTERNAL",
    "PLL40_2_FEEDBACK_PATH_PHASE_AND_DELAY", "PLL40_2_FEEDBACK_PATH_SIMPLE",
    "PLL40_2F_FEEDBACK_PATH_DELAY", "PLL40_2F_FEEDBACK_PATH_EXTERNAL",
    "PLL40_2F_FEEDBACK_PATH_PHASE_AND_DELAY", "PLL40_2F_FEEDBACK_PATH_SIMPLE",
    "PLL40_FEEDBACK_PATH_DELAY", "PLL40_FEEDBACK_PATH_EXTERNAL",
    "PLL40_FEEDBACK_PATH_PHASE_AND_DELAY", "PLL40_FEEDBACK_PATH_SIMPLE",
    "PRE_IO_PIN_TYPE", "sync_clk_enable", "TRIBUF"
])

database = dict()
sdf_inputs = list()
txt_inputs = list()
output_mode = "txt"
label = "unknown"
edgefile = None

def usage():
    print("""
Usage: python3 timings.py [options] [sdf_file..]

    -t filename
        read TXT file

    -l label
        label for HTML file title

    -h edgefile
        output HTML, use specified edge file

    -s
        output SDF (not TXT) format
""")
    sys.exit(0)


try:
    opts, args = getopt.getopt(sys.argv[1:], "t:l:h:s")
except:
    usage()

for o, a in opts:
    if o == "-t":
        txt_inputs.append(a)
    elif o == "-l":
        label = a
    elif o == "-h":
        output_mode = "html"
        edgefile = a
    elif o == "-s":
        output_mode = "sdf"
    else:
        usage()

sdf_inputs += args


convert = lambda text: int(text) if text.isdigit() else text.lower()
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
alphanum_key_list = lambda l: [len(l)] + [ alphanum_key(s) for s in l ]


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


def rewrite_celltype(celltype):
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
            if match:
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
            if match:
                celltype = "Span12Mux_%c%d" % (match.group(2), int(match.group(1)))

    return celltype


def add_entry(celltype, entry):
    entry = sdf_to_string(entry)
    entry = entry.replace("(posedge ", "posedge:")
    entry = entry.replace("(negedge ", "negedge:")
    entry = entry.replace("(", "")
    entry = entry.replace(")", "")
    entry = entry.split()
    if celltype.count("FEEDBACK") == 0 and entry[0] == "IOPATH" and entry[2].startswith("PLLOUT"):
        entry[3] = "*:*:*"
        entry[4] = "*:*:*"
    database[celltype].add(tuple(entry))


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

        for stmt in cell:
            if stmt[0] == "CELLTYPE":
                celltype = rewrite_celltype(stmt[1][1:-1])
                if celltype == "SB_MAC16":
                    try:
                        with open(filename.replace(".sdf", ".dsp"), "r") as dspf:
                            celltype = dspf.readline().strip()
                    except:
                        break
                database.setdefault(celltype, set())

            if stmt[0] == "DELAY":
                assert stmt[1][0] == "ABSOLUTE"
                for entry in stmt[1][1:]:
                    assert entry[0] == "IOPATH"
                    add_entry(celltype, entry)

            if stmt[0] == "TIMINGCHECK":
                for entry in stmt[1:]:
                    add_entry(celltype, entry)


###########################################
# Parse TXT input files

for filename in txt_inputs:
    print("### reading TXT file %s" % filename, file=sys.stderr)
    with open(filename, "r") as f:
        celltype = None
        for line in f:
            line = line.split()
            if len(line) > 1:
                if line[0] == "CELL":
                    celltype = rewrite_celltype(line[1])
                    database.setdefault(celltype, set())
                else:
                    add_entry(celltype, line)


###########################################
# Filter database

for celltype in ignore_cells:
    if celltype in database:
        del database[celltype]


###########################################
# Create SDF output

if output_mode == "sdf":
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

if output_mode == "txt":
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


###########################################
# Create HTML output

if output_mode == "html":
    print("<h1>IceStorm Timing Model: %s</h1>" % label)

    edge_celltypes = set()
    source_by_sink_desc = dict()
    sink_by_source_desc = dict()

    with open(edgefile, "r") as f:
        for line in f:
            source, sink = line.split()
            source_cell, source_port = source.split(".")
            sink_cell, sink_port = sink.split(".")

            source_cell = rewrite_celltype(source_cell)
            sink_cell = rewrite_celltype(sink_cell)

            assert source_cell not in ignore_cells
            assert sink_cell not in ignore_cells

            if source_cell in ["GND", "VCC"]:
                continue

            source_by_sink_desc.setdefault(sink_cell, set())
            sink_by_source_desc.setdefault(source_cell, set())

            source_by_sink_desc[sink_cell].add((sink_port, source_cell, source_port))
            sink_by_source_desc[source_cell].add((source_port, sink_cell, sink_port))

            edge_celltypes.add(source_cell)
            edge_celltypes.add(sink_cell)

    print("<div style=\"-webkit-column-count: 3; -moz-column-count: 3; column-count: 3;\"><ul style=\"margin:0\">")
    for celltype in sorted(database, key=alphanum_key):
        if celltype not in edge_celltypes:
            print("### ignoring unused cell type %s" % celltype, file=sys.stderr)
        else:
            print("<li><a href=\"#%s\">%s</a></li>" % (celltype, celltype))
    print("</ul></div>")

    for celltype in sorted(database, key=alphanum_key):
        if celltype not in edge_celltypes:
            continue

        print("<p><hr></p>")
        print("<h2><a name=\"%s\">%s</a></h2>" % (celltype, celltype))

        if celltype in source_by_sink_desc:
            print("<h3>Sources driving this cell type:</h3>")
            print("<table width=\"600\" border>")
            print("<tr><th>Input Port</th><th>Source Cell</th><th>Source Port</th></tr>")
            for entry in sorted(source_by_sink_desc[celltype], key=alphanum_key_list):
                print("<tr><td>%s</td><td><a href=\"#%s\">%s</a></td><td>%s</td></tr>" % (entry[0], entry[1], entry[1], entry[2]))
            print("</table>")

        if celltype in sink_by_source_desc:
            print("<h3>Sinks driven by this cell type:</h3>")
            print("<table width=\"600\" border>")
            print("<tr><th>Output Port</th><th>Sink Cell</th><th>Sink Port</th></tr>")
            for entry in sorted(sink_by_source_desc[celltype], key=alphanum_key_list):
                print("<tr><td>%s</td><td><a href=\"#%s\">%s</a></td><td>%s</td></tr>" % (entry[0], entry[1], entry[1], entry[2]))
            print("</table>")

        delay_abs_entries = list()
        timingcheck_entries = list()
        for entry in sorted(database[celltype], key=alphanum_key_list):
            if entry[0] == "IOPATH":
                delay_abs_entries.append(entry)
            else:
                timingcheck_entries.append(entry)

        if len(delay_abs_entries) > 0:
            print("<h3>Propagation Delays:</h3>")
            print("<table width=\"800\" border>")
            print("<tr><th rowspan=\"2\">Input Port</th><th rowspan=\"2\">Output Port</th>")
            print("<th colspan=\"3\">Low-High Transition</th><th colspan=\"3\">High-Low Transition</th></tr>")
            print("<tr><th>Min</th><th>Typ</th><th>Max</th><th>Min</th><th>Typ</th><th>Max</th></tr>")
            for entry in delay_abs_entries:
                print("<tr><td>%s</td><td>%s</td>" % (entry[1].replace(":", " "), entry[2].replace(":", " ")), end="")
                print("<td>%s</td><td>%s</td><td>%s</td>" % tuple(entry[3].split(":")), end="")
                print("<td>%s</td><td>%s</td><td>%s</td>" % tuple(entry[4].split(":")), end="")
                print("</tr>")
            print("</table>")

        if len(timingcheck_entries) > 0:
            print("<h3>Timing Checks:</h3>")
            print("<table width=\"800\" border>")
            print("<tr><th rowspan=\"2\">Check Type</th><th rowspan=\"2\">Input Port</th>")
            print("<th rowspan=\"2\">Output Port</th><th colspan=\"3\">Timing</th></tr>")
            print("<tr><th>Min</th><th>Typ</th><th>Max</th></tr>")
            for entry in timingcheck_entries:
                print("<tr><td>%s</td><td>%s</td><td>%s</td>" % (entry[0], entry[1].replace(":", " "), entry[2].replace(":", " ")), end="")
                print("<td>%s</td><td>%s</td><td>%s</td>" % tuple(entry[3].split(":")), end="")
                print("</tr>")
            print("</table>")
