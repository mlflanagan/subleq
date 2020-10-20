#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
asm.py - assemble a subleq program into an executable file for subleq.py.
mlf 2020-10-20

TODO: input/output
"""

import sys
from typing import List


def is_int(s: str) -> bool:
    """
    is_int: Check to see if parameter s is an int.
    :param s: string that may be an int.
    :return: True if s is integer, False if not
    """
    retval = True
    try:
        int(s)
    except ValueError:
        retval = False
    return retval


class Assembler:
    def __init__(self, program: List[str]):
        self.program: List[str] = program
        self.symbol_table: dict = {}
        self.tokens: List[str] = []
        self.prev_token: str = ""
        self.intermediate_output: List[List[str]] = []
        self.memory_location: int = 0
        self.assembled_code: List[str] = self.parse()

    def unget_token(self, token: str) -> None:
        """
        unget_token: store current token for next step in parsing
        :param token: current token
        :return: None
        """
        self.prev_token = token

    def get_token(self) -> str:
        """
        get_token: If there is a value in prev_token, return it, otherwise
        return the next token in the stream.  Return empty string if at end
        of stream.
        :return: token
        """
        if self.prev_token:
            token = self.prev_token
            self.prev_token = ""
        else:
            try:
                token = next(self.tokens)
            except StopIteration:
                token = ""
        return token

    def parse_line(self, line: str) -> List[str]:
        """
        parse_line: parse a single line of subleq source code.
        Called in the first pass.
        :param line: a string representing the line of subleq
        source code to parse.
        :return: parsed_line - a list of strings representing
        the intermediate code.
        """
        parsed_line: List[str] = []
        self.tokens = iter(line.split())
        state = 'START'
        while state != 'HALT':
            if state == 'START':
                token = self.get_token()
                if token[-1] == ':':
                    # we have either a data definition, e.g., Z: 0
                    # or a goto target, e.g., L1: a b
                    label = token[:-1]
                    self.symbol_table[label] = self.symbol_table.get(
                        label,
                        self.memory_location)
                    state = 'GET-1ST-ARG'
                elif token == "subleq":
                    # ignore "subleq" keyword
                    state = 'GET-1ST-ARG'
                else:
                    # this must the first arg
                    self.unget_token(token)
                    state = 'GET-1ST-ARG'
            elif state == 'GET-1ST-ARG':
                # the "a" in an instruction like subleq a b addr
                token = self.get_token()
                if token == "" or token[0] == ';':
                    raise ValueError(f"need at least one arg: {self.tokens}")
                else:
                    parsed_line.append(token)
                    self.memory_location += 1
                    state = 'GET-2ND-ARG'
            elif state == 'GET-2ND-ARG':
                # the "b" in an instruction like subleq a b addr
                token = self.get_token()
                if token == "" or token[0] == ';':
                    state = 'HALT'
                else:
                    parsed_line.append(token)
                    self.memory_location += 1
                    state = 'GET-3RD-ARG'
            elif state == 'GET-3RD-ARG':
                # the address to jump to if b - a <= 0
                token = self.get_token()
                if token == "" or token[0] == ';':
                    # reached eol, implied address is next memory location
                    parsed_line.append(str(self.memory_location + 1))
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

    def parse(self) -> List[str]:
        """
        parse: parse a file of subleq source code
        :return: list of ints representing the assembled code
        """
        # first pass - build symbol table
        for line in self.program:
            line = line.strip()
            if line == '' or line[0] == ';':
                continue
            parsed_line = self.parse_line(line)
            self.intermediate_output.append(parsed_line)

        # second pass - replace symbols with defined memory locations
        final_output: List[str] = []
        for line in self.intermediate_output:
            for symbol in line:
                if is_int(symbol):
                    final_output.append(symbol)
                else:
                    if symbol in self.symbol_table:
                        final_output.append(str(self.symbol_table[symbol]))
                    else:
                        raise ValueError(f"undefined symbol: {symbol}")

        return final_output


def main():
    try:
        filename = sys.argv[1]
        name, ext = filename.split(".")
        with open(filename, 'r') as inf, open(name + ".asm", 'w') as outf:
            assembler: Assembler = Assembler(inf.readlines())
            # create a space separated string for writelines
            output = [str(i) for i in assembler.assembled_code]
            outf.writelines(' '.join(output))
    except IndexError:
        basename = sys.argv[0].split("/")[-1]
        print(f"usage: {basename} filename")
        sys.exit(1)
    except FileNotFoundError:
        print(f"can't open file: {sys.argv[1]}")
        sys.exit(1)


if __name__ == '__main__':
    main()
