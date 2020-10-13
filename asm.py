#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
from typing import List

"""
TODO: input/output
"""


def is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


class Assembler:
    def __init__(self, program):
        self.program = program
        self.symbol_table = {}
        self.tokens = []
        self.prev_token = ""
        self.intermediate_output = []
        self.memory_location = 0
        self.parse()

    def get_token(self) -> str:
        try:
            token = next(self.tokens)
        except StopIteration:
            token = ""
        return token

    def parse_line(self, line: str) -> List[str]:
        """
        minuend: The quantity from which another quantity is to be subtracted.
        subtrahend: A quantity to be subtracted from another quantity.
        Example: subleq a b ; b = b - a
            b is the minuend
            a is the subtrahend
        So in subleq logic, first arg = subtrahend and 2nd arg = minuend.
        """
        parsed_line = []
        self.tokens = iter(line.split())
        state = 'START'
        while state != 'HALT':
            if state == 'START':
                token = self.get_token()
                # this should never happen
                # if token[0] == ';':
                #     # embedded comment, ignore rest of line
                #     state = 'HALT'
                if token[-1] == ':':
                    # label, e.g.:
                    # Z: 0 (data definition) or
                    # L1: a b (target of goto)
                    label = token[:-1]
                    # add label and address to symbol table
                    self.symbol_table[label] = self.symbol_table.get(
                        label,
                        self.memory_location)
                    state = 'GET-SUBTRAHEND'
                elif token == "subleq":
                    # ignore "subleq" word
                    state = 'GET-SUBTRAHEND'
                else:
                    # this is subtrahend
                    parsed_line.append(token)
                    self.memory_location += 1
                    state = 'GET-MINUEND'
            elif state == 'GET-SUBTRAHEND':
                # get first arg
                token = self.get_token()
                if token == "" or token[0] == ';':
                    raise ValueError(f"need at least one arg: {self.tokens}")
                else:
                    parsed_line.append(token)
                    self.memory_location += 1
                    state = 'GET-MINUEND'
            elif state == 'GET-MINUEND':
                # get 2nd arg
                token = self.get_token()
                if token == "" or token[0] == ';':
                    state = 'HALT'
                else:
                    parsed_line.append(token)
                    self.memory_location += 1
                    state = 'GET-ADDRESS'
            elif state == 'GET-ADDRESS':
                # get 3rd arg
                token = self.get_token()
                if token == "" or token[0] == ';':
                    # end of line, make implicit address explicit to next line
                    parsed_line.append(self.memory_location + 1)
                    self.memory_location += 1
                    state = 'HALT'
                else:
                    parsed_line.append(token)
                    self.memory_location += 1
                    # ignore anything after 3rd arg
                    state = 'HALT'
            else:
                raise ValueError(f"unknown state: {state}")

        return parsed_line

    def parse(self) -> None:
        # first pass - build symbol table
        for line in self.program:
            line = line.strip()
            if line == '' or line[0] == ';':
                continue
            parsed_line = self.parse_line(line)
            self.intermediate_output.append(parsed_line)
        print(f"symbol table = {self.symbol_table}")
        print(f"intermediate output: {self.intermediate_output}")

        # second pass - replace symbols with defined memory locations
        final_output: list = []
        for line in self.intermediate_output:
            for symbol in line:
                if is_int(symbol):
                    final_output.append(int(symbol))
                else:
                    if symbol in self.symbol_table:
                        final_output.append(self.symbol_table[symbol])
                    else:
                        raise ValueError(f"undefined symbol: {symbol}")

        print(f"final output: {final_output}")


def main(args: list) -> None:
    with open(args[0], 'r') as file:
        Assembler(file.readlines())


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except IndexError:
        print(f"usage: {os.path.basename(sys.argv[0])} filename")
        sys.exit(1)
