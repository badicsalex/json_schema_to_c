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
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from .base import Generator, CType


class BoolGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "default",
    )
    default = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        if self.default is not None and not isinstance(self.default, bool):
            raise TypeError("Boolean types should have a boolean as a default")
        self.c_type = CType("bool", self.description)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'boolean'

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if (builtin_parse_bool(parse_state, {}))"
            .format(out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def has_default_value(self):
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        out_file.print(
            "{} = {};".format(
                out_var_name,
                'true' if self.default else 'false'
            )
        )

    def max_token_num(self):
        return 1
