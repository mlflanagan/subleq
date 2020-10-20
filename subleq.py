#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
subleq.py - simulate a subleq OISC to execute a subleq program.
mlf 2020-10-20

TODO: input/output
"""

import sys
from typing import List


def subleq(mem: List[int]):
    """ subleq VM """
    pc = 0
    while pc != -1:
        r1 = mem[pc]
        r2 = mem[pc + 1]
        r3 = mem[pc + 2]
        mem[r2] -= mem[r1]
        if mem[r2] <= 0:
            pc = r3
        else:
            pc += 3


def main():
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as file:
            mem = file.read().split()
            # convert to list of ints
            subleq([int(i) for i in mem])
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
