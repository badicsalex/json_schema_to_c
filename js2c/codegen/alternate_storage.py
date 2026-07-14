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
from typing import Any

from .base import Generator, CType, SchemaError, GeneratorInitParameters
from .code_block_printer import CodeBlockPrinter


class RawJsonType(CType):
    def generate_type_declaration_impl(self, out_file: CodeBlockPrinter) -> None:
        out_file.print(f"typedef struct {self.type_name}_s {{")
        with out_file.indent():
            out_file.print_with_docstring("size_t index;", "Byte offset of the value in the input JSON")
            out_file.print_with_docstring("size_t length;", "Length of the value in the input JSON")
        out_file.print(f"}} {self.type_name};")
        out_file.print("")


class AlternateStorageGenerator(Generator):
    # Reserved js2cType values that store a value differently instead of naming a C type.
    STORAGE_FORMATS = ("void", "raw")

    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        super().__init__(schema, parameters)
        # A void stores nothing, and a raw is a reference into the input text, so neither has
        # anything a default could name.
        if self.js2cDefault is not None:
            raise SchemaError(self, "A void or raw js2cType cannot have a js2cDefault")
        if self.js2cType == "raw":
            self.type_name = parameters.base_name + "_json_ref_t"
            self.c_type = parameters.type_cache.try_get_cached(RawJsonType(self.type_name, self.description), self.path_in_schema)
        else:
            self.c_type = None

    @classmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        return schema.get("js2cType") in cls.STORAGE_FORMATS

    def generate_parser_call(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        if self.js2cType == "raw":
            out_var = out_var_name.removeprefix("&")
            out_file.print(f"{out_var}.index = (size_t) CURRENT_TOKEN(parse_state).start;")
            out_file.print(
                f"{out_var}.length = (size_t) (CURRENT_TOKEN(parse_state).end - CURRENT_TOKEN(parse_state).start);"
            )
        with out_file.if_block("builtin_skip(parse_state)"):
            out_file.print("return true;")

    def generate_set_default_value(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        raise AssertionError("has_default_value() is always false: a void or raw cannot have a js2cDefault.")

    def max_token_num(self) -> int:
        # A skipped value is at least one token; composite values need extra token headroom
        # (--allow-additional-properties), as their structure isn't declared here.
        return 1
