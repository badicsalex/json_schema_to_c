#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2020 Alex Badics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from typing import Optional

from .base import Generator


class NumberGenerator(Generator):
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    exclusiveMinimum: Optional[int] = None
    exclusiveMaximum: Optional[int] = None
    default: Optional[int] = None

    def __init__(self, schema, name, generators):
        super().__init__(schema, name, generators)
        if self.minimum is not None and self.minimum >= 0:
            self.c_type = "uint64_t"
            self.parser_fn = "builtin_parse_unsigned"
            self.default_suffix = "ULL"
            if self.minimum == 0:
                self.minimum = None
        else:
            self.c_type = "int64_t"
            self.parser_fn = "builtin_parse_signed"
            self.default_suffix = "LL"

    @classmethod
    def generate_range_check(cls, check_number, out_var_name, check_operator, out_file):
        if check_number is None:
            return
        out_file.print("if (!((*{}) {} {}))".format(out_var_name, check_operator, check_number))
        with out_file.code_block():
            # Roll back the token, as the value was not actually correct
            out_file.print("parse_state->current_token -=1;")
            cls.generate_logged_error(
                [
                    "Integer %li out of range. It must be {} {}.".format(check_operator, check_number),
                    "(*{})".format(out_var_name)
                ],
                out_file
            )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if({}(parse_state, {}))"
            .format(self.parser_fn, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")
        self.generate_range_check(self.minimum, out_var_name, ">=", out_file)
        self.generate_range_check(self.maximum, out_var_name, "<=", out_file)
        self.generate_range_check(self.exclusiveMinimum, out_var_name, ">", out_file)
        self.generate_range_check(self.exclusiveMaximum, out_var_name, "<", out_file)

    def has_default_value(self):
        return self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        out_file.print("{} = {}{};".format(out_var_name, self.default, self.default_suffix))

    def max_token_num(self):
        return 1
