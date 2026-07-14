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
from abc import abstractmethod

from typing import Any

from .base import Generator, CType, SchemaError, GeneratorInitParameters
from .code_block_printer import CodeBlockPrinter


class IntegerType(CType):
    __slots__ = ()
    SIGNED_TYPES = ["int64_t", "int32_t", "int16_t", "int8_t"]
    UNSIGNED_TYPES = ["uint64_t", "uint32_t", "uint16_t", "uint8_t"]

    def __init__(self, generator: Generator, type_name: str, description: str | None) -> None:
        if type_name not in self.SIGNED_TYPES + self.UNSIGNED_TYPES:
            raise SchemaError(generator, f"Unsupported integer type: {type_name}")
        super().__init__(type_name, description)

    def is_unsigned(self) -> bool:
        return self.type_name in self.UNSIGNED_TYPES


class IntegerGeneratorBase(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "default",
    )

    minimum: int | None = None
    maximum: int | None = None
    exclusiveMinimum: int | None = None
    exclusiveMaximum: int | None = None
    # NumericStringGenerator reparses a string default into an int.
    default: int | str | None = None

    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        super().__init__(schema, parameters)
        non_negative = self.minimum is not None and self.minimum >= 0
        if self.js2cType is not None:
            c_type_name = self.js2cType
        else:
            c_type_name = "uint64_t" if non_negative else "int64_t"

        if self.js2cParseFunction is not None:
            # js2cType is whatever the custom parser outputs, so it can't tell us the parse type; the
            # full parsed integer is handed to it, unsigned when the schema constrains it non-negative.
            self.c_type = CType(c_type_name, self.description)
            unsigned = non_negative
        else:
            self.c_type = IntegerType(self, c_type_name, self.description)
            unsigned = self.c_type.is_unsigned()

        if unsigned:
            self.parser_fn = "builtin_parse_unsigned"
            self.parsed_type = "uint64_t"
            self.parsed_type_printf_macro = "PRIu64"
            self.default_suffix = "ULL"
            if self.minimum == 0:
                self.minimum = None
        else:
            self.parser_fn = "builtin_parse_signed"
            self.parsed_type = "int64_t"
            self.parsed_type_printf_macro = "PRIi64"
            self.default_suffix = "LL"
        # Set by the subclass: a plain integer has no radix of its own.
        self.radix: int | None = None

    @property
    @abstractmethod
    def string_allowed(self) -> bool:
        pass

    @property
    @abstractmethod
    def number_allowed(self) -> bool:
        pass

    def generate_range_check(
        self,
        check_number: int | None,
        out_var_printf_macro: str,
        check_operator: str,
        inverted_check_operator: str,
        out_file: CodeBlockPrinter,
    ) -> None:
        # pylint: disable=too-many-arguments
        if check_number is None:
            return
        with out_file.if_block(f"int_parse_tmp {inverted_check_operator} {check_number}{self.default_suffix}"):
            # Roll back the token, as the value was not actually correct
            out_file.print("parse_state->current_token -= 1;")
            self.generate_logged_error(
                [
                    f"Integer %\" {out_var_printf_macro} \" in '%s' out of range. It must be {check_operator} {check_number}.",
                    "int_parse_tmp",
                    "parse_state->current_key",
                ],
                out_file
            )

    def generate_parser_call(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        out_file.print(f"{self.parsed_type} int_parse_tmp;")
        number_allowed = 'true' if self.number_allowed else 'false'
        string_allowed = 'true' if self.string_allowed else 'false'
        parser_call = (
            f"{self.parser_fn}(parse_state, {number_allowed}, {string_allowed}, {self.radix}, &int_parse_tmp)"
        )
        with out_file.if_block(parser_call):
            out_file.print("return true;")
        self.generate_range_check(self.minimum, self.parsed_type_printf_macro, ">=", "<", out_file)
        self.generate_range_check(self.maximum, self.parsed_type_printf_macro, "<=", ">", out_file)
        self.generate_range_check(self.exclusiveMinimum, self.parsed_type_printf_macro, ">", "<=", out_file)
        self.generate_range_check(self.exclusiveMaximum, self.parsed_type_printf_macro, "<", ">=", out_file)
        if self.js2cParseFunction is not None:
            # The value was already parsed and current_token advanced past it, so point back at it
            # for a correct error position, then restore.
            out_file.print("parse_state->current_token -= 1;")
            self.generate_custom_parser_call(
                f"int_parse_tmp, {out_var_name}",
                f'%" {self.parsed_type_printf_macro} "',
                ["int_parse_tmp"],
                out_file
            )
            out_file.print("parse_state->current_token += 1;")
        else:
            out_file.print(f"*{out_var_name} = int_parse_tmp;")

    def has_default_value(self) -> bool:
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name: str, out_file: CodeBlockPrinter) -> None:
        if self.generate_js2c_default_value(out_var_name, out_file):
            return
        if self.js2cParseFunction is not None:
            # Cast to the parsed type so it matches both the parse function's argument and the
            # printf macro used if it reports an error.
            default_value = f"({self.parsed_type}) {self.default}{self.default_suffix}"
            self.generate_custom_parser_call(
                f"{default_value}, &{out_var_name}",
                f'%" {self.parsed_type_printf_macro} "',
                [default_value],
                out_file
            )
        else:
            out_file.print(f"{out_var_name} = {self.default}{self.default_suffix};")

    def max_token_num(self) -> int:
        return 1


class IntegerGenerator(IntegerGeneratorBase):
    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        super().__init__(schema, parameters)
        self.radix = 10

    @property
    def string_allowed(self) -> bool:
        return False

    @property
    def number_allowed(self) -> bool:
        return True

    @classmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        return schema.get('type') == 'integer'


class NumericStringGenerator(IntegerGenerator):
    JSON_FIELDS = IntegerGenerator.JSON_FIELDS + (
        "pattern",
    )
    pattern: str | None = None

    UNSIGNED_PATTERNS = {
        '[0-9]+': 10,
        '[0-9a-fA-F]+': 16,
        '(0x|0X)?[0-9a-fA-F]+': 16,
        '(0[0-7]+|[0-9]+|0[xX][0-9a-fA-F]+)': 0,
    }
    SIGNED_PATTERNS = {'[+-]?' + k: v for k, v in UNSIGNED_PATTERNS.items()}

    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        # minimum might be in the schema if this constructor is called by IntegerStringAnyOfGenerator
        if 'minimum' not in schema and schema['pattern'] in self.UNSIGNED_PATTERNS:
            schema['minimum'] = 0
        super().__init__(schema, parameters)
        # can_parse_schema() rejects js2cParseFunction, so the base built an IntegerType.
        assert isinstance(self.c_type, IntegerType)
        if self.c_type.is_unsigned():
            pattern_set = self.UNSIGNED_PATTERNS
        else:
            pattern_set = self.SIGNED_PATTERNS

        if self.pattern not in pattern_set:
            valid_patterns = ", ".join(f'"{p}"' for p in pattern_set)
            raise SchemaError(
                self,
                f'Pattern "{self.pattern}" is not a valid pattern for this value range. Valid patterns are: {valid_patterns}'
            )
        self.radix = pattern_set[self.pattern]
        if isinstance(self.default, str):
            self.default = int(self.default, self.radix)

    @property
    def string_allowed(self) -> bool:
        return True

    @property
    def number_allowed(self) -> bool:
        return False

    @classmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        if schema.get('type') != 'string':
            return False
        if schema.get('js2cParseFunction') is not None:
            return False
        return schema.get('pattern') in cls.UNSIGNED_PATTERNS or schema.get('pattern') in cls.SIGNED_PATTERNS


class IntegerStringAnyOfGenerator(NumericStringGenerator):
    def __init__(self, schema: dict[str, Any], parameters: GeneratorInitParameters) -> None:
        combined_schema = schema['anyOf'][0]
        combined_schema.update(schema['anyOf'][1])
        combined_schema['type'] = 'string'
        super().__init__(combined_schema, parameters)

    @classmethod
    def can_parse_schema(cls, schema: dict[str, Any]) -> bool:
        if "anyOf" not in schema or len(schema['anyOf']) != 2:
            return False
        return set((schema['anyOf'][0].get('type'), schema['anyOf'][1].get('type'))) == set(('integer', 'string'))

    @property
    def string_allowed(self) -> bool:
        return True

    @property
    def number_allowed(self) -> bool:
        return True
