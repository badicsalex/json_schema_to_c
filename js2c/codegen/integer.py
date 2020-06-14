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

from .base import Generator


class IntegerGeneratorBase(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "default",
    )

    minimum = None
    maximum = None
    exclusiveMinimum = None
    exclusiveMaximum = None
    default = None

    def __init__(self, schema, name, settings, generator_factory):
        super().__init__(schema, name, settings, generator_factory)
        if self.minimum is not None and self.minimum >= 0:
            self.c_type = "uint64_t"
            self.parser_fn = "builtin_parse_unsigned"
            self.default_suffix = "ULL"
            if self.minimum == 0:
                self.minimum = None
        else:
            self.c_type = "int64_t"
            self.parser_fn = "builtin_parse_signed"
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

    @classmethod
    def generate_range_check(cls, check_number, out_var_name, check_operator, out_file):
        if check_number is None:
            return
        out_file.print("if (!((*{}) {} {}))".format(out_var_name, check_operator, check_number))
        with out_file.code_block():
            # Roll back the token, as the value was not actually correct
            out_file.print("parse_state->current_token -=1;")
            cls.generate_logged_error(
                [
                    "Integer %li out of range. It must be {} {}.".format(check_operator, check_number),
                    "(*{})".format(out_var_name)
                ],
                out_file
            )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if({}(parse_state, {}, {}, {}, {}))"
            .format(
                self.parser_fn,
                'true' if self.number_allowed else 'false',
                'true' if self.string_allowed else 'false',
                self.radix,
                out_var_name
            )
        )
        with out_file.code_block():
            out_file.print("return true;")
        self.generate_range_check(self.minimum, out_var_name, ">=", out_file)
        self.generate_range_check(self.maximum, out_var_name, "<=", out_file)
        self.generate_range_check(self.exclusiveMinimum, out_var_name, ">", out_file)
        self.generate_range_check(self.exclusiveMaximum, out_var_name, "<", out_file)

    def has_default_value(self):
        return self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        out_file.print("{} = {}{};".format(out_var_name, self.default, self.default_suffix))

    def max_token_num(self):
        return 1


class IntegerGenerator(IntegerGeneratorBase):
    def __init__(self, schema, name, settings, generator_factory):
        super().__init__(schema, name, settings, generator_factory)
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

    def __init__(self, schema, name, settings, generator_factory):
        # minimum might be in the schema if this constructor is called by IntegerStringAnyOfGenerator
        if 'minimum' not in schema and schema['pattern'] in self.UNSIGNED_PATTERNS:
            schema['minimum'] = 0
        super().__init__(schema, name, settings, generator_factory)
        if self.c_type == 'uint64_t':
            pattern_set = self.UNSIGNED_PATTERNS
        else:
            pattern_set = self.SIGNED_PATTERNS

        if self.pattern not in pattern_set:
            valid_patterns = ", ".join('"{}"'.format(p) for p in pattern_set)
            raise ValueError(
                'Pattern "{}" is not a valid pattern for this value range. Valid patterns are: {}'
                .format(self.pattern, valid_patterns)
            )
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
    def __init__(self, schema, name, settings, generator_factory):
        combined_schema = schema['anyOf'][0]
        combined_schema.update(schema['anyOf'][1])
        combined_schema['type'] = 'string'
        super().__init__(combined_schema, name, settings, generator_factory)

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
