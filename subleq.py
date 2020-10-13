#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" subleq
"""


def subleq(mem):
    """ subleq VM """
    try:
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
    except KeyboardInterrupt:
        print("Interrupted")


def mov():
    """ mov a, b
    """
    mem = [
        # code
        14, 14,  3,  # 0 -  2: b = b - b = 0 (set b to zero)
        13, 12,  6,  # 3 -  5: Z = Z - a
        12, 14,  9,  # 6 -  8: b = b - Z
        12, 12, -1,  # 9 - 11: Z = Z - Z = 0 (reset Z to zero and halt)

        # data
        0, 7, 0,  # 12 - 14: Z, a, b
    ]
    subleq(mem)


def negate_manual_assembly():
    """ b = not a; in this test a = 7 so b = not a = -8
    """
    mem = [
        # code
        7,  8,  3,  # 0 - 2: negate a (b = -a) like so: b = b - a = 0 - 7 = -7
        9,  8, -1,  # 3 - 5: inc b (b -= -1) like so: b = b - 1 = -7 - 1 = -8
        # data
        0,  7,  0,  # 6 - 8: Z, a, b
        1,  0,  0,  # 9 - 11: 1 (a constant)
    ]
    subleq(mem)


def inc():
    """ inc a
    """
    mem = [
        # code
        9,  7,  3,  # 0 - 2: a = a - (-1) = 0 - (-1) = 1
        0,  0, -1,  # 3 - 5: halt
        # data
        0,  0,  0,  # 6 - 8: Z, a, b
       -1,  0,  0,  # 9 - 11: -1 (a constant)

    ]
    subleq(mem)


def jmp():
    """ jmp
    """
    mem = [
        # code
        9,  9,  6,  # 0 - 2: a = a - (-1) = 0 - (-1) = 1
        0,  0,  6,  # 3 - 5: jump over this line
        9,  9, -1,  # 6 - 8: execute this line (halt)
        # data
        0,  0,  0,  # 9 - 11: Z, a, b
       -1,  0,  0,  # 12 - 14: -1 (a constant)

    ]
    subleq(mem)


def negate():
    """not - this version was assembled by the assembler
    """
    mem = [8, 9, 3, 6, 9, -1, 1, 0, 7, 0]
    subleq(mem)


if __name__ == '__main__':
    # mov()
    # negate()
    # inc()
    # jmp()
    negate()
