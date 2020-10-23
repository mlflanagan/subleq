#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests

instruction statement format: [Label:] [subleq] a b [address] [; comment]
data statement format: label: <.byte byte | .string ascii string> [; comment]

Example instruction statements
    ; whole line is a comment
    loop: subleq Z b 6 ; trailing comment
    loop: subleq Z b
    loop: Z b 6
    loop: Z b
    subleq Z b 6
    subleq Z b
    Z b 6
    Z b
    Z

Example data statements
    b: .byte 0
    Z: .byte 0
    hello: .string "Hello, world!"
"""

import unittest

from sasm import Assembler


class TestFirstPass(unittest.TestCase):
    def setUp(self) -> None:
        self.assembler: Assembler = Assembler([])

    # ------------------------------------------------------------------------------
    # INSTRUCTION STATEMENTS
    # ------------------------------------------------------------------------------
    def test_full_form_without_comment(self):
        # full form of instruction statement without comment
        assert self.assembler.parse_statement("loop: subleq Z b 6") == ['Z', 'b', '6']

    def test_implied_address(self):
        assert self.assembler.parse_statement("loop: subleq Z b") == ['Z', 'b', '3']

    def test_implied_2nd_arg_implied_address(self):
        assert self.assembler.parse_statement("loop: subleq Z") == ['Z', 'Z', '3']

    def test_implied_subleq_keyword(self):
        assert self.assembler.parse_statement("loop: Z b 6") == ['Z', 'b', '6']

    def test_implied_subleq_implied_address(self):
        assert self.assembler.parse_statement("loop: Z b") == ['Z', 'b', '3']

    def test_implied_subleq_implied_2nd_arg_implied_address(self):
        assert self.assembler.parse_statement("loop: Z") == ['Z', 'Z', '3']

    def test_no_label(self):
        assert self.assembler.parse_statement("subleq Z b 6") == ['Z', 'b', '6']

    def test_no_label_implied_address(self):
        assert self.assembler.parse_statement("subleq Z b") == ['Z', 'b', '3']

    def test_no_label_implied_2nd_arg_implied_address(self):
        assert self.assembler.parse_statement("subleq Z") == ['Z', 'Z', '3']

    def test_no_label_implied_subleq_keyword(self):
        assert self.assembler.parse_statement("Z b 6") == ['Z', 'b', '6']

    def test_no_label_implied_subleq_implied_address(self):
        assert self.assembler.parse_statement("Z b") == ['Z', 'b', '3']

    def test_no_label_implied_subleq_implied_2nd_arg_implied_address(self):
        assert self.assembler.parse_statement("Z") == ['Z', 'Z', '3']

    # ------------------------------------------------------------------------------
    # DATA STATEMENTS
    # ------------------------------------------------------------------------------
    def test_single_byte_data(self):
        assert self.assembler.parse_statement("Z: .word 0") == ['0']

    # string data statement
    def test_string_data(self):
        assert self.assembler.parse_statement("hello: .string \"Hello, world!\"") == [
            '72', '101', '108', '108', '111', '44', '32',
            '119', '111', '114', '108', '100', '33', '0']

    def tearDown(self) -> None:
        self.assembler = None


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.assembler: Assembler = Assembler([])

    def test_blank_line(self):
        # this actually gets tested by the setUp method
        self.assembler.parse([""])
        assert self.assembler.final_output == []

    def test_comment_line(self):
        self.assembler.parse(["; this is a comment line"])
        assert self.assembler.final_output == []

    def test_full_form_with_comment(self):
        # note! must define Z and b vars for this test to work,
        # otherwise it fails with ValueError
        self.assembler.parse(
            ["loop: subleq Z b 6 ; this is an embedded comment", "Z: .word 7", "b: .word 11"])
        assert self.assembler.final_output == ['3', '4', '6', '7', '11']

    def tearDown(self) -> None:
        self.assembler = None


if __name__ == '__main__':
    # prevent unittest from sorting class methods alphabetically
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()

    # To run only the tests in the specified classes:
    # suites_list = []
    # for test_class in [TestParser]:  # run only the TestParser tests
    #     suites_list.append(unittest.TestLoader().loadTestsFromTestCase(test_class))
    # results = unittest.TextTestRunner(verbosity=3).run(unittest.TestSuite(suites_list))
