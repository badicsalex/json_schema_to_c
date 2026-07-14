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
    # can_parse_schema() requires it, so the JSON_FIELDS loop always sets it.
    const: str | int

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.c_type = None  # no type to store, "const" is just for validation

        if not isinstance(self.const, str) and not isinstance(self.const, int):
            raise SchemaError(self, "JS2C supports only strings and integers for const")

        if "type" in schema:
            schema_type = schema["type"]
            if isinstance(self.const, str) and schema_type != "string":
                raise SchemaError(self, f"Const type mismatch, expected 'string', got '{schema_type}'")
            if isinstance(self.const, int) and schema_type != "number":
                raise SchemaError(self, f"Const type mismatch, expected 'number', got '{schema_type}'")

    @classmethod
    def can_parse_schema(cls, schema):
        return "const" in schema

    def generate_parser_call(self, out_var_name, out_file):
        parser_call = f"parse_{self.parser_name}(parse_state)"
        with out_file.if_block(parser_call):
            out_file.print("return true;")

    def generate_parser_bodies(self, out_file):
        out_file.print(f"static bool parse_{self.parser_name}(parse_state_t *parse_state)")
        error = [f"Invalid const value in '%s', expected: {self.const}", "parse_state->current_key"]
        with out_file.code_block():
            if isinstance(self.const, str):
                with out_file.if_block("check_type(parse_state, JSMN_STRING)"):
                    out_file.print("return true;")
                with out_file.if_block(f'!current_string_is(parse_state, "{self.const}")'):
                    self.generate_logged_error(error, out_file)
                out_file.print("parse_state->current_token += 1;")
            else:
                with out_file.if_block("check_type(parse_state, JSMN_PRIMITIVE)"):
                    out_file.print("return true;")
                out_file.print("int64_t val;")
                with out_file.if_block("builtin_parse_signed(parse_state, true, false, 10, &val)"):
                    out_file.print("return true;")
                with out_file.if_block(f"val != {self.const}"):
                    # builtin_parse_signed already consumed the token; step back so the error points at it.
                    out_file.print("parse_state->current_token -= 1;")
                    self.generate_logged_error(error, out_file)
            out_file.print("return false;")
        out_file.print("")

    def max_token_num(self):
        return 1
