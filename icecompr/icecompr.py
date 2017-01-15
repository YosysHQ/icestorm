#!/usr/bin/env python3
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

def make_int_bits(value, nbits):
    bits = list()
    for i in range(nbits-1, -1, -1):
        bits.append((value & (1 << i)) != 0)
    return bits

def ice_compress_bits(inbits):
    outbits = list()
    outbits += make_int_bits(0x49434543, 32)
    outbits += make_int_bits(0x4f4d5052, 32)

    deltas = list()
    numzeros = 0

    for bit in inbits:
        if bit:
            deltas.append(numzeros)
            numzeros = 0
        else:
            numzeros += 1

    i = 0
    while i < len(deltas):
        raw_len = 0
        compr_len = 0
        best_compr_raw_diff = -1
        best_compr_raw_idx = -1
        best_compr_raw_len = -1

        for j in range(len(deltas) - i):
            delta = deltas[i+j]
            raw_len += delta + 1

            if delta < 4:
                compr_len += 3
            elif delta < 32:
                compr_len += 7
            elif delta < 256:
                compr_len += 11
            else:
                compr_len += 26

            if compr_len - raw_len < max(best_compr_raw_diff - 4, 0) or raw_len > 64:
                break

            if compr_len - raw_len > best_compr_raw_diff:
                best_compr_raw_diff = compr_len - raw_len
                best_compr_raw_idx = j
                best_compr_raw_len = raw_len

        if best_compr_raw_diff > 9:
            outbits.append(False)
            outbits.append(False)
            outbits.append(False)
            outbits.append(True)
            outbits += make_int_bits(best_compr_raw_len-1, 6)

            for j in range(0, best_compr_raw_idx+1):
                delta = deltas[i+j]
                for k in range(delta):
                    outbits.append(False)
                if j < best_compr_raw_idx:
                    outbits.append(True)

            i += best_compr_raw_idx + 1
            continue

        delta = deltas[i]
        i += 1

        if delta < 4:
            outbits.append(True)
            outbits += make_int_bits(delta, 2)
        elif delta < 32:
            outbits.append(False)
            outbits.append(True)
            outbits += make_int_bits(delta, 5)
        elif delta < 256:
            outbits.append(False)
            outbits.append(False)
            outbits.append(True)
            outbits += make_int_bits(delta, 8)
        else:
            outbits.append(False)
            outbits.append(False)
            outbits.append(False)
            outbits.append(False)
            outbits.append(True)
            outbits += make_int_bits(delta, 23)

    outbits.append(False)
    outbits.append(False)
    outbits.append(False)
    outbits.append(False)
    outbits.append(False)
    outbits += make_int_bits(numzeros, 23)

    return outbits

def ice_compress_bytes(inbytes):
    inbits = list()
    for byte in inbytes:
        for i in range(7, -1, -1):
            inbits.append((byte & (1 << i)) != 0)

    outbits = ice_compress_bits(inbits)

    outbytes = list()
    for i in range(0, len(outbits), 8):
        byte = 0
        for k in range(i, min(i+8, len(outbits))):
            if outbits[k]: byte |= 1 << (7-(k-i))
        outbytes.append(byte)

    return bytes(outbytes)

# ------------------------------------------------------
# Usage example:
# python3 icecompr.py < example_8k.bin > example_8k.compr

if __name__ == '__main__':
    import sys
    inbytes = sys.stdin.buffer.read()
    outbytes = ice_compress_bytes(inbytes)
    sys.stdout.buffer.write(outbytes)

