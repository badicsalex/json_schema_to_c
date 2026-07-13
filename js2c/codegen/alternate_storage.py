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
from .base import Generator, CType


class RawJsonType(CType):
    def generate_type_declaration_impl(self, out_file):
        out_file.print("typedef struct {}_s ".format(self.type_name) + "{")
        with out_file.indent():
            out_file.print_with_docstring("size_t index;", "Byte offset of the value in the input JSON")
            out_file.print_with_docstring("size_t length;", "Length of the value in the input JSON")
        out_file.print("}} {};".format(self.type_name))
        out_file.print("")


class AlternateStorageGenerator(Generator):
    # Reserved js2cType values that store a value differently instead of naming a C type.
    STORAGE_FORMATS = ("void", "raw")

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        if self.js2cType == "raw":
            self.type_name = parameters.base_name + "_json_ref_t"
            self.c_type = parameters.type_cache.try_get_cached(RawJsonType(self.type_name, self.description))
        else:
            self.c_type = None

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get("js2cType") in cls.STORAGE_FORMATS

    def generate_parser_call(self, out_var_name, out_file):
        if self.js2cType == "raw":
            out_var = out_var_name.removeprefix("&")
            out_file.print("{}.index = (size_t) CURRENT_TOKEN(parse_state).start;".format(out_var))
            out_file.print(
                "{}.length = (size_t) (CURRENT_TOKEN(parse_state).end - CURRENT_TOKEN(parse_state).start);"
                .format(out_var)
            )
        with out_file.if_block("builtin_skip(parse_state)"):
            out_file.print("return true;")

    def max_token_num(self):
        # A skipped value is at least one token; composite values need extra token headroom
        # (--allow-additional-properties), as their structure isn't declared here.
        return 1
