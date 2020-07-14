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
import re

from .base import Generator


class EnumGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "enum",
        "default",
        "convertLabelsToSnakeCase",
    )
    enum = None
    default = None
    convertLabelsToSnakeCase = True

    SANITIZE_RE = re.compile("[^A-Za-z0-9_]")
    CAMEL_CASE_RE = re.compile(
        "("
        "(?<=[a-z])(?=[A-Z])|"
        "(?<=[0-9])(?=[a-zA-Z])|"
        "(?<=[a-zA-Z])(?=[0-9])"
        ")"
    )

    def __init__(self, schema, name, settings, generator_factory):
        super().__init__(schema, name, settings, generator_factory)
        self.c_type = "{}_t".format(self.name)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'string' and 'enum' in schema

    def convert_enum_label(self, enum_label):
        if self.convertLabelsToSnakeCase:
            enum_label = self.CAMEL_CASE_RE.sub(r"_", enum_label)
            enum_label = enum_label.upper()
        prefixed = "{}_{}".format(self.name.upper(), enum_label)
        sanitized = self.SANITIZE_RE.sub("_", prefixed)
        return sanitized

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if (parse_{}(parse_state, {}))"
            .format(self.name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def generate_type_declaration(self, out_file, *, force=False):
        _ = force  # This is python's way of saying (void)force

        out_file.print("typedef enum {}_e".format(self.name) + "{")
        with out_file.indent():
            for enum_label in self.enum[:-1]:
                out_file.print("{},".format(self.convert_enum_label(enum_label)))
            out_file.print("{}".format(self.convert_enum_label(self.enum[-1])))
        out_file.print("}} {};".format(self.c_type))
        out_file.print("")

    def generate_parser_bodies(self, out_file):
        out_file.print("static bool parse_{}(parse_state_t *parse_state, {} *out)".format(self.name, self.c_type))
        with out_file.code_block():
            out_file.print("if (check_type(parse_state, JSMN_STRING))")
            with out_file.code_block():
                out_file.print("return true;")

            for enum_label in self.enum:
                out_file.print('if (current_string_is(parse_state, "{}"))'.format(enum_label))
                with out_file.code_block():
                    out_file.print("*out = {};".format(self.convert_enum_label(enum_label)))
                out_file.print("else")
            with out_file.code_block():
                self.generate_logged_error(["Unknown enum value in '%s': %.*s", "parse_state->current_key", "CURRENT_STRING_FOR_ERROR(parse_state)"], out_file)

            out_file.print("parse_state->current_token += 1;")
            out_file.print("return false;")
        out_file.print("")

    def has_default_value(self):
        return super().has_default_value() or self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        out_file.print("{} = {};".format(out_var_name, self.convert_enum_label(self.default)))

    def max_token_num(self):
        return 1
