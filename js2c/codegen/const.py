#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2025 MaiaSpace SAS
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
from .base import Generator, SchemaError


class ConstGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "const",
    )
    const = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.c_type = None  # no type to store, "const" is just for validation

        if not isinstance(self.const, str) and not isinstance(self.const, int):
            raise SchemaError(self, "JS2C supports only strings and integers for const")

        if "type" in schema:
            if isinstance(self.const, str) and schema["type"] != "string":
                raise SchemaError(self, "Const type mismatch, expected 'string', got '{}'".format(schema["type"]))
            if isinstance(self.const, int) and schema["type"] != "number":
                raise SchemaError(self, "Const type mismatch, expected 'number', got '{}'".format(schema["type"]))

    @classmethod
    def can_parse_schema(cls, schema):
        return "const" in schema

    def generate_parser_call(self, out_var_name, out_file, on_err="return true;"):
        parser_call = "parse_{}(parse_state)".format(self.parser_name)
        with out_file.if_block(parser_call):
            out_file.print(on_err)

    def generate_parser_bodies(self, out_file):
        out_file.print("static bool parse_{}(parse_state_t *parse_state)".format(self.parser_name))
        with out_file.code_block():
            if isinstance(self.const, str):
                with out_file.if_block("check_type(parse_state, JSMN_STRING)"):
                    out_file.print("return true;")
                not_match = '!current_string_is(parse_state, "{}")'.format(self.const)
            else:
                with out_file.if_block("check_type(parse_state, JSMN_PRIMITIVE)"):
                    out_file.print("return true;")
                out_file.print("int64_t val;")
                out_file.print("builtin_parse_signed(parse_state, true, false, 10, &val);")
                not_match = "val != " + str(self.const)

            with out_file.if_block(not_match):
                self.generate_logged_error(
                    [
                        "Invalid const value in '%s', expected: " + str(self.const),
                        "parse_state->current_key",
                    ],
                    out_file)

            out_file.print("parse_state->current_token += 1;")
            out_file.print("return false;")
        out_file.print("")

    def max_token_num(self):
        return 1
