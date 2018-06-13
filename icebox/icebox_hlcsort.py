#!/usr/bin/env python3
import sys

top_levels = []
f = open(sys.argv[1])

current_block_stack = [top_levels]
while len(current_block_stack) > 0:
    line = f.readline()
    if not line:
        break

    if '#' in line:
        continue

    if '{' in line:
        new_block = []
        current_block_stack[-1].append(new_block)
        current_block_stack.append(new_block)

    if line.strip():
        current_block_stack[-1].append(line)

    if '}' in line or not line:
        assert len(current_block_stack) > 1 or not line, current_block_stack
        old_block = current_block_stack.pop(-1)
        sorted_block = [old_block[0],] + sorted(old_block[1:-1], key=lambda x: repr(x)) + [old_block[-1],]
        old_block.clear()
        old_block.extend(sorted_block)

top_levels = list(sorted(top_levels, key=lambda x: repr(x)))

output_stack = [top_levels]
while len(output_stack) > 0:
    if len(output_stack[0]) == 0:
        output_stack.pop(0)
        continue
    if type(output_stack[0][0]) == list:
        output_stack.insert(0, output_stack[0].pop(0))
        continue
    print(output_stack[0].pop(0), end='')
