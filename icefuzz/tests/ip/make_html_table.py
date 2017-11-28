#!/usr/bin/env python3
import ast, sys

data = ""
with open(sys.argv[1], 'r') as f:
    data = f.read()
    
ip_dat = ast.literal_eval("{\n" + data + "}")

def is_cbit(ident):
    if "_ENABLE" in ident or "DELAYED" in ident:
        return True
    else:
        return False

def is_bus(ident):
    return ident.startswith("SB")

ips = sorted(ip_dat)
print ("<table class=\"cstab\">\n<tr><th>Signal</th>", end='')
for ip in ips:
    t, loc = ip
    x, y, z = loc
    print("<th>%s<br/>(%d, %d, %d)</th>" % (t, x, y, z), end='')
print ("</tr>")

# TODO: could group busses?
for print_t in ["SB", "G", "CBIT"]:
    for n in sorted(ip_dat[ips[0]]):
        if is_bus(n) != (print_t == "SB"):
            continue
        if is_cbit(n) != (print_t == "CBIT"):
            continue
        print("<tr>", end='')
        em_o = ""
        em_c = ""
        if is_cbit(n):
            em_o = "<em>"
            em_c = "</em>"
        print("<td>%s%s%s</td>" % (em_o, n, em_c), end='')
        for ip in ips:
            entry = ip_dat[ip][n]
            x, y, name = entry
            print("<td>%s(%d, %d, %s)%s</td>" % (em_o, x, y, name, em_c), end='')
        print("</tr>")
print ("</table>")
