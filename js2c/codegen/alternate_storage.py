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
from .base import Generator, CType, SchemaError


class RawJsonType(CType):
    def __init__(self, type_name, description):
        super().__init__(type_name, description)

    def generate_type_declaration_impl(self, out_file):
        out_file.print("typedef struct " + self.type_name.removesuffix("_t") + " {")
        with out_file.indent():
            out_file.print_with_docstring("size_t index;", "The byte position of the raw JSON segment in the input text")
            out_file.print_with_docstring("size_t length;", "The length of the raw JSON segment in the input text")
        out_file.print("}} {};".format(self.type_name))
        out_file.print("")


class AlternateStorageGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "js2cStorageFormat",
    )
    js2cStorageFormat = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)

        allowed_values = ["void", "raw"]
        allowed_values_str = ", ".join([f"'{v}'" for v in allowed_values])
        if self.js2cStorageFormat not in allowed_values:
            raise SchemaError(self, f"js2cStorageFormat has unsupported value: got '{self.js2cStorageFormat}', but the only allowed values are: {allowed_values_str}")

        match self.js2cStorageFormat:
            case "void": self.c_type = None
            case "raw":
                self.type_name = parameters.base_name + '_json_ref_t'
                self.c_type = RawJsonType(self.type_name, self.description)

    @classmethod
    def can_parse_schema(cls, schema):
        return "js2cStorageFormat" in schema

    def generate_parser_call(self, out_var_name, out_file, on_err="return true;"):
        if self.js2cStorageFormat == "raw":
            out_file.print(f"{out_var_name.removeprefix('&')}.index = (size_t) CURRENT_TOKEN(parse_state).start;")
            out_file.print(f"{out_var_name.removeprefix('&')}.length = (size_t) CURRENT_TOKEN(parse_state).end - CURRENT_TOKEN(parse_state).start;")

        with out_file.if_block("builtin_skip(parse_state)"):
            out_file.print(on_err)

    def generate_parser_bodies(self, out_file):
        return

    def has_default_value(self):
        return False

    def max_token_num(self):
        return 0  # FIXME not sure about that
