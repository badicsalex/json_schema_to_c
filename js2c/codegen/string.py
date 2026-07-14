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
from typing import Any

from .base import Generator, CType, SchemaError, GeneratorInitParameters
from .code_block_printer import CodeBlockPrinter


class StringType(CType):
    def __init__(self, type_name: str, description: str | None, max_length: int) -> None:
        super().__init__(type_name, description)
        self.max_length = max_length

    def generate_type_declaration_impl(self, out_file: CodeBlockPrinter) -> None:
        out_file.print_with_docstring(
            f"typedef char {self.type_name}[{self.max_length + 1}];", self.description
        )
        out_file.print("")

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, StringType) and
            self.max_length == other.max_length
        )


class StringGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minLength",
        "maxLength",
        "default",
    )

    minLength: int = 0
    maxLength: int | None = None
    default: str | None = None

    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        super().__init__(schema, parameters)
        assert 'enum' not in schema, "Enums should be generated with EnumGenerator"
        assert 'const' not in schema, "Consts should be generated with ConstGenerator"

        if self.maxLength is None:
            raise SchemaError(self, "Strings must have maxLength")

        if self.default is not None and len(self.default) > self.maxLength:
            raise SchemaError(self, "String default value longer than maxLength")

        if self.default is not None and len(self.default) < self.minLength:
            raise SchemaError(self, "String default value shorter than minLength")

        if self.js2cParseFunction is not None:
            if self.js2cType is None:
                raise SchemaError(self, "js2cParseFunction needs js2cType, as its output type cannot be guessed")
            self.c_type = CType(self.js2cType, self.description)
        else:
            self.c_type = StringType(self.type_name, self.description, self.maxLength)
        self.c_type = parameters.type_cache.try_get_cached(self.c_type, self.path_in_schema)

    @classmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        return schema.get('type') == 'string'

    def generate_parser_call(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        if self.js2cParseFunction is not None:
            length_check = \
                f"builtin_check_current_string(parse_state, {self.minLength}, {self.maxLength})"
            with out_file.if_block(length_check):
                out_file.print("return true;")

            self.generate_custom_parser_call(
                f"CURRENT_STRING(parse_state), CURRENT_STRING_LENGTH(parse_state), {out_var_name}",
                "%.*s",
                ["CURRENT_STRING_LENGTH(parse_state)", "CURRENT_STRING(parse_state)"],
                out_file
            )
            out_file.print("parse_state->current_token += 1;")
        else:
            length_check = \
                f"builtin_parse_string(parse_state, {out_var_name}[0], {self.minLength}, {self.maxLength})"
            with out_file.if_block(length_check):
                out_file.print("return true;")

    def has_default_value(self) -> bool:
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        assert self.has_default_value(), "Caller is responsible for checking this."
        assert self.maxLength is not None, "__init__ rejects a string without maxLength."
        if self.js2cDefault is not None:
            out_file.print(
                f'strncpy({out_var_name}, {self.js2cDefault}, {self.maxLength + 1});'
            )
            return
        # has_default_value() holds without js2cDefault, so default is set.
        assert self.default is not None
        if self.js2cParseFunction is not None:
            # The custom parser call has to be in its own code block, because
            # it declares a variable, and there are places where this is generated
            # multiple times into the same scope.
            with out_file.code_block(standalone=True):
                self.generate_custom_parser_call(
                    f'"{self.default}", {len(self.default)}, &{out_var_name}',
                    "%.*s",
                    [str(len(self.default)), f'"{self.default}"'],
                    out_file
                )
        else:
            out_file.print(
                f'memcpy({out_var_name}, "{self.default}", {len(self.default) + 1});'
            )

    def max_token_num(self) -> int:
        return 1
