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

from .base import Generator, CType, SchemaError
from .code_block_printer import CodeBlockPrinter


class IntegerType(CType):
    __slots__ = ()
    SIGNED_TYPES = ["int64_t", "int32_t", "int16_t", "int8_t"]
    UNSIGNED_TYPES = ["uint64_t", "uint32_t", "uint16_t", "uint8_t"]

    def __init__(self, generator, type_name, description):
        if type_name not in self.SIGNED_TYPES + self.UNSIGNED_TYPES:
            raise SchemaError(generator, "Unsupported integer type: " + type_name)
        super().__init__(type_name, description)

    def is_unsigned(self):
        return self.type_name in self.UNSIGNED_TYPES


class IntegerGeneratorBase(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "default",
        "js2cParseFunction",
        "js2cParseType",
    )

    minimum = None
    maximum = None
    exclusiveMinimum = None
    exclusiveMaximum = None
    default = None
    js2cParseFunction = None
    js2cParseType = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        if self.js2cType is not None:
            c_type_name = self.js2cType
        else:
            if self.minimum is not None and self.minimum >= 0:
                c_type_name = "uint64_t"
            else:
                c_type_name = "int64_t"

        if self.js2cParseFunction is not None:
            if self.js2cParseType is None:
                self.js2cParseType = "int64_t"
            self.c_intermediary_type = CType(self.js2cParseType, self.description)
            self.c_type = CType(c_type_name, self.description)
        else:
            self.c_type = self.c_intermediary_type = IntegerType(self, c_type_name, self.description)

        if (self.js2cParseFunction is not None and self.minimum >= 0) or self.c_intermediary_type.is_unsigned():
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
        self.radix = None

    @property
    @abstractmethod
    def string_allowed(self):
        pass

    @property
    @abstractmethod
    def number_allowed(self):
        pass

    def generate_range_check(self, check_number: int, out_var_printf_macro: str, check_operator: str, inverted_check_operator: str, out_file: CodeBlockPrinter, on_err: str | list[str]):
        # pylint: disable=too-many-arguments
        if check_number is None:
            return
        with out_file.if_block(f"int_parse_tmp {inverted_check_operator} ({self.c_intermediary_type}) {check_number}{self.default_suffix}"):
            # Roll back the token, as the value was not actually correct
            out_file.print("parse_state->current_token -= 1;")
            self.generate_logged_error(
                [
                    "Integer %\" {} \" in '%s' out of range. It must be {} {}."
                    .format(out_var_printf_macro, check_operator, check_number),
                    "int_parse_tmp",
                    "parse_state->current_key",
                ],
                out_file,
                exit_statement=on_err
            )

    def generate_custom_parser_call(self, in_value, out_var_name, out_file, on_err):
        out_file.print("const char *error = NULL;")
        out_file.require_section(self.js2cParseFunction)
        with out_file.if_block(f"{self.js2cParseFunction}({in_value}, {out_var_name}, &error)"):
            self.generate_logged_error([
                f"Error parsing '%s', value=\\\"%\" {self.parsed_type_printf_macro} \"\\\": %s",
                "parse_state->current_key",
                in_value,
                f'error != NULL ? error : "error calling {self.js2cParseFunction}"',
            ], out_file, exit_statement=on_err)

    def generate_parser_call(self, out_var_name, out_file, on_err="return true;"):
        out_file.print(f"{self.parsed_type} int_parse_tmp = 0;")
        out_file.require_section(self.parser_fn)
        parser_call = "{}(parse_state, {}, {}, {}, &int_parse_tmp)".format(
            self.parser_fn,
            'true' if self.number_allowed else 'false',
            'true' if self.string_allowed else 'false',
            self.radix
        )
        with out_file.if_block(parser_call):
            out_file.print(on_err)
        self.generate_range_check(self.minimum, self.parsed_type_printf_macro, ">=", "<", out_file, on_err)
        self.generate_range_check(self.maximum, self.parsed_type_printf_macro, "<=", ">", out_file, on_err)
        self.generate_range_check(self.exclusiveMinimum, self.parsed_type_printf_macro, ">", "<=", out_file, on_err)
        self.generate_range_check(self.exclusiveMaximum, self.parsed_type_printf_macro, "<", ">=", out_file, on_err)
        if self.js2cParseFunction:
            self.generate_custom_parser_call("int_parse_tmp", out_var_name, out_file, on_err)
        else:
            out_file.print(f"*{out_var_name} = int_parse_tmp;")

    def has_default_value(self):
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        default_value = f"({self.c_intermediary_type}) {self.default}{self.default_suffix}"
        if self.js2cParseFunction:
            self.generate_custom_parser_call(default_value, "&" + out_var_name, out_file, on_err="return true;")
        else:
            out_file.print(f"{out_var_name} = {default_value};")


class IntegerGenerator(IntegerGeneratorBase):
    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.radix = 10

    @property
    def string_allowed(self):
        return False

    @property
    def number_allowed(self):
        return True

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'integer'


class NumericStringGenerator(IntegerGenerator):
    JSON_FIELDS = IntegerGenerator.JSON_FIELDS + (
        "pattern",
    )
    pattern = None

    UNSIGNED_PATTERNS = {
        '[0-9]+': 10,
        '[0-9a-fA-F]+': 16,
        '(0x|0X)?[0-9a-fA-F]+': 16,
        '(0[0-7]+|[0-9]+|0[xX][0-9a-fA-F]+)': 0,
    }
    SIGNED_PATTERNS = {'[+-]?' + k: v for k, v in UNSIGNED_PATTERNS.items()}

    def __init__(self, schema, parameters):
        # minimum might be in the schema if this constructor is called by IntegerStringAnyOfGenerator
        if 'minimum' not in schema and schema['pattern'] in self.UNSIGNED_PATTERNS:
            schema['minimum'] = 0
        super().__init__(schema, parameters)
        if self.c_type.is_unsigned():
            pattern_set = self.UNSIGNED_PATTERNS
        else:
            pattern_set = self.SIGNED_PATTERNS

        if self.pattern not in pattern_set:
            valid_patterns = ", ".join('"{}"'.format(p) for p in pattern_set)
            raise SchemaError(self, f'Pattern "{self.pattern}" is not a valid pattern for this value range. Valid patterns are: {valid_patterns}')
        self.radix = pattern_set[self.pattern]
        if isinstance(self.default, str):
            self.default = int(self.default, self.radix)

    @property
    def string_allowed(self):
        return True

    @property
    def number_allowed(self):
        return False

    @classmethod
    def can_parse_schema(cls, schema):
        if schema.get('type') != 'string':
            return False
        if schema.get('js2cParseFunction') is not None:
            return False
        return schema.get('pattern') in cls.UNSIGNED_PATTERNS or schema.get('pattern') in cls.SIGNED_PATTERNS


class IntegerStringAnyOfGenerator(NumericStringGenerator):
    def __init__(self, schema, parameters):
        combined_schema = schema['anyOf'][0]
        combined_schema.update(schema['anyOf'][1])
        combined_schema['type'] = 'string'
        super().__init__(combined_schema, parameters)

    @classmethod
    def can_parse_schema(cls, schema):
        if "anyOf" not in schema or len(schema['anyOf']) != 2:
            return False
        return set((schema['anyOf'][0]['type'], schema['anyOf'][1]['type'])) == set(('integer', 'string'))

    @property
    def string_allowed(self):
        return True

    @property
    def number_allowed(self):
        return True
