#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
subleq.py - simulate a subleq OISC to execute a subleq program.
Credit for input/output logic goes to https://rosettacode.org/wiki/Subleq#Python

TODO:
  We don't know the data type of the value to print, assumed string for now.
  - One solution would be to just print(hex(mem[r1]))
  - Another solution would be to have the subleq programmer indicate
    what to print by setting r2 == -1 (.word) or r2 == -2 (.string), e.g:
    if r2 == -1:
        print(mem[r1], end='')
    else: if r2 == -2:
        print(chr(mem[r1]), end='')
"""

import sys
from typing import List


def subleq(mem: List[int]):
    """ subleq VM """
    pc = 0
    while pc != -1:
        # load registers with contents of next three memory addresses
        r1 = mem[pc]
        r2 = mem[pc + 1]
        r3 = mem[pc + 2]

        if r1 == -1:
            # input into memory location pointed to by r2
            mem[r2] = ord(sys.stdin.read(1)[0])
            pc += 3
        elif r2 == -1:
            # Output from memory location pointed to by r1.
            print(chr(mem[r1]), end='')
            pc += 3
        else:
            # execute subleq instruction
            mem[r2] -= mem[r1]
            if mem[r2] <= 0:
                pc = r3
            else:
                pc += 3


def main():
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as file:
            program = file.read().split()
            # convert to list of ints for processing
            subleq([int(i) for i in program])
    except IndexError:
        basename = sys.argv[0].split("/")[-1]
        print(f"usage: {basename} filename")
        sys.exit(1)
    except FileNotFoundError:
        print(f"can't open file: {sys.argv[1]}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == '__main__':
    main()
