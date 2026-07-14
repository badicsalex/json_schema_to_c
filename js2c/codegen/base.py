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
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, NamedTuple

from ..settings import Settings
from .code_block_printer import CodeBlockPrinter

if TYPE_CHECKING:
    # Both import this module, so they can only be named in annotations.
    from .generator_factory import GeneratorFactory
    from .type_cache import TypeCache

# Names that can't be used as C identifiers: keywords, plus the stdbool.h macros.
C_RESERVED = frozenset((
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long",
    "register", "restrict", "return", "short", "signed", "sizeof", "static", "struct",
    "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
    "bool", "true", "false",
))


class SchemaError(ValueError):
    def __init__(self, generator_or_path: Generator | str, message: str) -> None:
        if isinstance(generator_or_path, str):
            path = generator_or_path
        else:
            path = generator_or_path.path_in_schema
        if not path:
            path = '<root>'
        super().__init__(f"Schema error in '{path}': {message}")


class GeneratorInitParameters(NamedTuple):
    path_in_schema: str
    base_name: str
    parser_name: str
    type_name: str
    settings: Settings
    generator_factory: type[GeneratorFactory]
    type_cache: TypeCache

    def with_suffix(self, path_in_schema: str, type_name: str, suffix: str) -> GeneratorInitParameters:
        return GeneratorInitParameters(
            self.path_in_schema + "." + path_in_schema,
            self.base_name,
            f"{self.parser_name}_{suffix}",
            f'{type_name.removesuffix("_t")}_{suffix}_t',
            self.settings,
            self.generator_factory,
            self.type_cache,
        )


class Generator(ABC):
    JSON_FIELDS: tuple[str, ...] = (
        "description",
        "js2cDefault",
        "js2cType",
        "js2cParseFunction",
    )

    # A const stores nothing, so it stays None.
    c_type: CType | None = None
    description: str | None = None
    # Pasted into the C code as-is, so any scalar whose str() is a C expression.
    js2cDefault: str | int | float | None = None
    js2cType: str | None = None
    js2cParseFunction: str | None = None

    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        for attr in self.JSON_FIELDS:
            if attr in schema:
                setattr(self, attr, schema[attr])

        self.path_in_schema = parameters.path_in_schema
        self.settings = parameters.settings
        self.parser_name = parameters.parser_name

        # js2cDefault is pasted into the C code as-is, so anything whose str() is not a C
        # expression ends up in the output verbatim. bool is checked first, being an int.
        if self.js2cDefault is not None and (
                isinstance(self.js2cDefault, bool) or not isinstance(self.js2cDefault, (str, int, float))):
            raise SchemaError(self, "js2cDefault must be a string, an integer or a float, as it is pasted into the C code as-is")

        self.type_name: str
        if self.js2cType is not None:
            self.type_name = self.js2cType
        elif "$id" in schema:
            self.type_name = schema["$id"].removeprefix("#") + "_t"
        else:
            self.type_name = parameters.type_name

    @abstractmethod
    def generate_parser_call(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        pass

    @abstractmethod
    def max_token_num(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        pass

    def generate_parser_bodies(self, out_file: CodeBlockPrinter) -> None:
        pass

    def has_default_value(self) -> bool:
        return self.js2cDefault is not None

    def generate_js2c_default_value(self, out_var_name: str, out_file: CodeBlockPrinter) -> bool:
        """Emit js2cDefault, if the schema set one. Returns whether it did."""
        assert self.has_default_value(), "Caller is responsible for checking this."
        if self.js2cDefault is None:
            return False
        out_file.print(f"{out_var_name} = {self.js2cDefault};")
        return True

    def generate_set_default_value(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        emitted = self.generate_js2c_default_value(out_var_name, out_file)
        assert emitted, "A generator with any other source of defaults must override this."

    def generate_custom_parser_call(
        self,
        call_args: str,
        value_format: str,
        value_args: Sequence[str],
        out_file: CodeBlockPrinter,
    ) -> None:
        # call_args are the js2cParseFunction arguments before the trailing &error; value_format and
        # value_args describe how the offending value is printed in the error message.
        out_file.print("const char *error = NULL;")
        with out_file.if_block(f"{self.js2cParseFunction}({call_args}, &error)"):
            self.generate_logged_error(
                [
                    f"Error parsing '%s', value=\\\"{value_format}\\\": %s",
                    "parse_state->current_key",
                    *value_args,
                    f'error ? error : "error calling {self.js2cParseFunction}"',
                ],
                out_file,
            )

    @classmethod
    def generate_logged_error(cls, log_message: str | Sequence[str], out_file: CodeBlockPrinter) -> None:
        if isinstance(log_message, str):
            out_file.print(f'TRY_LOG_ERROR(CURRENT_TOKEN(parse_state).start, "{log_message}", parse_state->current_key)')
        else:
            assert len(log_message) > 1, "Use a simple string, not a 1 element array."
            log_args = ", ".join(log_message[1:])
            out_file.print(
                f'TRY_LOG_ERROR(CURRENT_TOKEN(parse_state).start, "{log_message[0]}", {log_args})'
            )
        out_file.print("return true;")


class CType():
    def __init__(self, type_name: str, description: str | None) -> None:
        self.type_name = type_name
        self.description = description
        self.declaration_generated = False

    def __str__(self) -> str:
        return self.type_name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def generate_field_declaration(self, field_name: str, out_file: CodeBlockPrinter) -> None:
        out_file.print_with_docstring(
            f"{self.type_name} {field_name};", self.description
        )

    def generate_type_declaration(self, out_file: CodeBlockPrinter) -> None:
        if self.declaration_generated:
            return
        self.generate_type_declaration_impl(out_file)
        self.declaration_generated = True

    def generate_type_declaration_impl(self, out_file: CodeBlockPrinter) -> None:
        # Simple types (e.g. uint64_t) should already be declared
        pass

    def __eq__(self, other: object) -> bool:
        # Description deliberately left out. It will be the same type
        # The main use-case is documenting a description differently on different
        # parts of the JSON. The main result here will be a wrong docstring on the type,
        # which is an OK trade-off.
        return self.__class__ == other.__class__ and self.type_name == other.type_name
