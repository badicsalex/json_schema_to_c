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
from .base import Generator, CType


class StringType(CType):
    def __init__(self, type_name, description, max_length):
        super().__init__(type_name, description)
        self.max_length = max_length

    def generate_type_declaration_impl(self, out_file):
        out_file.print_with_docstring(
            "typedef char {}[{}];".format(self.type_name, self.max_length + 1), self.description
        )
        out_file.print("")

    def __eq__(self, other):
        return (
            super().__eq__(other) and
            self.max_length == other.max_length
        )


class StringGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minLength",
        "maxLength",
        "default",
        "js2cParseFunction",
    )

    minLength = 0
    maxLength = None
    default = None
    js2cParseFunction = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        assert 'enum' not in schema, "Enums should be generated with EnumGenerator"

        if self.maxLength is None:
            raise ValueError("Strings must have maxLength")

        if self.default is not None and len(self.default) > self.maxLength:
            raise ValueError("String default value longer than maxLength")

        if self.default is not None and len(self.default) < self.minLength:
            print("MinLength", self.minLength)
            raise ValueError("String default value shorter than minLength")

        if self.js2cParseFunction is not None:
            self.c_type = CType(self.js2cType, self.description)
        else:
            self.c_type = StringType(self.type_name, self.description, self.maxLength)
        self.c_type = parameters.type_cache.try_get_cached(self.c_type)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'string'

    def generate_custom_parser_call(self, src, src_length, out_var_name, out_file):
        out_file.print("const char *error = NULL;")
        out_file.print(
            "if ({}({}, {}, {}, &error))"
            .format(self.js2cParseFunction, src, src_length, out_var_name)
        )
        with out_file.code_block():
            self.generate_logged_error([
                "Error parsing '%s', value=\\\"%.*s\\\": %s",
                "parse_state->current_key",
                src_length,
                src,
                "error ? error : \"error calling {}\"".format(self.js2cParseFunction),
            ], out_file)

    def generate_parser_call(self, out_var_name, out_file):
        if self.js2cParseFunction is not None:
            out_file.print(
                "if (builtin_check_current_string(parse_state, {}, {}))"
                .format(self.minLength, self.maxLength)
            )
            with out_file.code_block():
                out_file.print("return true;")

            self.generate_custom_parser_call(
                "CURRENT_STRING(parse_state)",
                "CURRENT_STRING_LENGTH(parse_state)",
                out_var_name,
                out_file
            )
            out_file.print("parse_state->current_token += 1;")
        else:
            out_file.print(
                "if (builtin_parse_string(parse_state, {}[0], {}, {}))"
                .format(out_var_name, self.minLength, self.maxLength)
            )
            with out_file.code_block():
                out_file.print("return true;")

    def has_default_value(self):
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        if self.js2cDefault is not None:
            out_file.print(
                'strncpy({dst}, {src}, {size});'.format(
                    dst=out_var_name,
                    src=self.js2cDefault,
                    size=self.maxLength + 1,
                )
            )
        elif self.js2cParseFunction is not None:
            # The custom parser call has to be in its own code block, because
            # it declares a variable, and there are places where this is generated
            # multiple times into the same scope.
            with out_file.code_block(standalone=True):
                self.generate_custom_parser_call(
                    '"{}"'.format(self.default),
                    str(len(self.default)),
                    "&{}".format(out_var_name),
                    out_file
                )
        else:
            out_file.print(
                'memcpy({dst}, "{src}", {size});'.format(
                    dst=out_var_name,
                    src=self.default,
                    size=len(self.default) + 1
                )
            )

    def max_token_num(self):
        return 1
