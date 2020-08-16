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
from .base import Generator, CType


class FloatGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "default",
    )

    minimum = None
    maximum = None
    exclusiveMinimum = None
    exclusiveMaximum = None
    default = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.c_type = CType("double", self.description)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'number'

    @classmethod
    def generate_range_check(cls, check_number, out_var_name, check_operator, out_file):
        if check_number is None:
            return
        out_file.print("if (!((*{}) {} {}))".format(out_var_name, check_operator, check_number))
        with out_file.code_block():
            # Roll back the token, as the value was not actually correct
            out_file.print("parse_state->current_token -= 1;")
            cls.generate_logged_error(
                [
                    "Floating point value %.15g in '%s' out of range. It must be {} {}.".format(check_operator, check_number),
                    "(*{})".format(out_var_name),
                    "parse_state->current_key",
                ],
                out_file
            )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if (builtin_parse_double(parse_state, {}))"
            .format(
                out_var_name
            )
        )
        with out_file.code_block():
            out_file.print("return true;")
        self.generate_range_check(self.minimum, out_var_name, ">=", out_file)
        self.generate_range_check(self.maximum, out_var_name, "<=", out_file)
        self.generate_range_check(self.exclusiveMinimum, out_var_name, ">", out_file)
        self.generate_range_check(self.exclusiveMaximum, out_var_name, "<", out_file)

    def has_default_value(self):
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        out_file.print("{} = {};".format(out_var_name, self.default))

    def max_token_num(self):
        return 1
