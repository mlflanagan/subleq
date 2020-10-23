#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
from typing import List


def is_int(s: str) -> bool:
    retval = True
    try:
        int(s)
    except ValueError:
        retval = False
    return retval


class Assembler:
    def __init__(self, program: List[str]):
        self.tokens: iter = []
        self.prev_token: str = ""
        self.first_arg: str = ""
        self.symbol_table: dict = {}
        self.memory_location: int = 0
        self.final_output: List[str] = []
        # parse the program
        self.parse(program)

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

    def parse_statement(self, statement: str) -> List[str]:
        """
        first_pass to build symbol table
        :param statement: the line of subleq code to parse
        :return: parsed_line - a list of strings with tokens
        """
        parsed_line: List[str] = []
        # - The regex pattern "[^"]*" matches a simple quoted string.
        # - "(?:\\.|[^"])*" matches a quoted string and skips over escaped quotes because \\. consumes two characters: a backslash and any character.
        # - [^\s,"] matches a non-delimiter.
        # - Combining patterns 2 and 3 inside (?: | )+ matches a sequence of non-delimiters and quoted strings, which is the desired result.
        #
        # Reference: https://stackoverflow.com/a/16710842
        self.tokens = iter(re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', statement))

        state = 'START'
        while state != 'HALT':
            if state == 'START':
                token = self.get_token()
                if token[-1] == ':':
                    self.unget_token(token)
                    state = 'GET-LABEL'
                elif token == "subleq":
                    # no need for a dedicated 'get-subleq' state, just ignore the 'subleq' keyword
                    state = 'GET-1ST-ARG'
                elif token == '.word':
                    # ignore the '.word' keyword
                    state = 'GET-BYTE-DATA'
                elif token == '.string':
                    # ignore the '.string' keyword
                    state = 'GET-STRING-DATA'
                else:
                    # assume this is the first arg
                    self.unget_token(token)
                    state = 'GET-1ST-ARG'
            elif state == 'GET-LABEL':
                # save memory location of label to symbol table
                label = self.get_token()[:-1]
                self.symbol_table[label] = self.symbol_table.get(label, self.memory_location)
                state = 'START'
            elif state == 'GET-1ST-ARG':
                # the "a" in an instruction like subleq Z b addr
                token = self.get_token()
                if token == "":
                    raise ValueError("Missing first arg")
                parsed_line.append(token)
                self.memory_location += 1
                # TODO: fix this hack
                self.first_arg = token
                state = 'GET-2ND-ARG'
            elif state == 'GET-2ND-ARG':
                # the "b" in an instruction like subleq Z b addr
                token = self.get_token()
                if token == "":
                    # handle implied 2nd arg - TODO: fix this hack
                    token = self.first_arg
                parsed_line.append(token)
                self.memory_location += 1
                state = 'GET-ADDRESS'
            elif state == 'GET-ADDRESS':
                # the address to jump to if b - Z <= 0
                token = self.get_token()
                if token == "":
                    # reached eol, implied address is next memory location
                    parsed_line.append(str(self.memory_location + 1))
                else:
                    parsed_line.append(token)
                self.memory_location += 1
                # ignore anything after 3rd arg
                state = 'HALT'
            elif state == 'GET-BYTE-DATA':
                token = self.get_token()
                if token == "":
                    raise ValueError("Missing byte data")
                parsed_line.append(token)
                self.memory_location += 1
                state = 'HALT'
            elif state == 'GET-STRING-DATA':
                token = self.get_token()
                # string must begin and end with double quotes (see regex above)
                if token[0] not in ["'", '"'] or token[-1] not in ["'", '"']:
                    raise ValueError("Missing quotes from string")
                # remove quotes
                token = token[1:-1]
                # read token char by char
                for ch in token:
                    parsed_line.append(str(ord(ch)))
                    self.memory_location += 1
                # add null value to mark end of string
                parsed_line.append('0')
                self.memory_location += 1
                state = 'HALT'
            else:
                raise ValueError(f"unknown state: {state}")

        return parsed_line

    def parse(self, program: List[str]) -> None:
        # first pass - build symbol table
        intermediate_output: List[List[str]] = []
        for statement in program:
            # remove trailing comments, if any
            statement = statement.split(';')[0]

            # ignore blank lines and comment lines
            statement = statement.strip()
            if statement == '' or statement[0] == ';':
                continue

            # parse this statement
            output = self.parse_statement(statement)
            intermediate_output.append(output)

        # second pass - replace symbols with memory locations
        self.final_output: List[str] = []
        for statement in intermediate_output:
            for symbol in statement:
                if is_int(symbol):
                    self.final_output.append(symbol)
                else:
                    if symbol in self.symbol_table:
                        self.final_output.append(str(self.symbol_table[symbol]))
                    else:
                        # this should never happen
                        raise ValueError(f"undefined symbol: {symbol}")


def main():
    try:
        filename = sys.argv[1]
        name, ext = filename.split(".")
        with open(filename, 'r') as infile, open(name + ".sasm", 'w') as outfile:
            assembler: Assembler = Assembler(infile.readlines())
            # create a space separated string for writelines
            output = [str(i) for i in assembler.final_output]
            outfile.writelines(' '.join(output))
    except IndexError:
        basename = sys.argv[0].split("/")[-1]
        print(f"usage: {basename} filename")
        sys.exit(1)
    except FileNotFoundError:
        print(f"can't open file: {sys.argv[1]}")
        sys.exit(1)


if __name__ == '__main__':
    main()
