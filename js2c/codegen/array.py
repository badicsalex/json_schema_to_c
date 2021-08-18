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
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from .base import Generator, CType


class ArrayType(CType):
    def __init__(self, type_name, description, item_type, max_items):
        super().__init__(type_name, description)
        self.item_type = item_type
        self.max_items = max_items

    def generate_type_declaration_impl(self, out_file):
        self.item_type.generate_type_declaration(out_file)

        out_file.print("typedef struct {}_s ".format(self.type_name) + "{")
        with out_file.indent():
            out_file.print_with_docstring("uint64_t n;", "The number of elements in the array")
            self.item_type.generate_field_declaration(
                "items[{}]".format(self.max_items), out_file
            )
        out_file.print("}} {};".format(self.type_name))
        out_file.print("")

    def __eq__(self, other):
        return (
            super().__eq__(other) and
            self.max_items == other.max_items and
            self.item_type == other.item_type
        )


class ArrayGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "minItems",
        "maxItems",
    )
    minItems = 0
    maxItems = None

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        if self.maxItems is None:
            raise ValueError("Arrays must have maxItems")

        self.item_generator = parameters.generator_factory.get_generator_for(
            schema["items"],
            parameters.with_suffix(self.type_name, "item"),
        )
        self.c_type = ArrayType(
            self.type_name,
            self.description,
            self.item_generator.c_type,
            self.maxItems
        )
        self.c_type = parameters.type_cache.try_get_cached(self.c_type)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'array'

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if (parse_{}(parse_state, {}))"
            .format(self.parser_name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def generate_range_checks(self, out_file):
        out_file.print("if (n > {})".format(self.maxItems))
        with out_file.code_block():
            self.generate_logged_error(
                ["Array '%s' too large. Length: %i. Maximum length: {}.".format(self.maxItems), "parse_state->current_key", "n"],
                out_file
            )
        if self.minItems:
            out_file.print("if (n < {})".format(self.minItems))
            with out_file.code_block():
                self.generate_logged_error(
                    ["Array '%s' too small. Length: %i. Minimum length: {}.".format(self.minItems), "parse_state->current_key", "n"],
                    out_file
                )

    def generate_parser_bodies(self, out_file):
        self.item_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{}(parse_state_t *parse_state, {} *out)".format(self.parser_name, self.c_type))
        with out_file.code_block():
            out_file.print("if (check_type(parse_state, JSMN_ARRAY))")
            with out_file.code_block():
                out_file.print("return true;")
            out_file.print("const int n = parse_state->tokens[parse_state->current_token].size;")
            self.generate_range_checks(out_file)
            out_file.print("out->n = n;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (int i = 0; i < n; ++i)")
            with out_file.code_block():
                self.item_generator.generate_parser_call(
                    "&out->items[i]",
                    out_file
                )
            out_file.print("return false;")
        out_file.print("")

    def has_default_value(self):
        return super().has_default_value() or self.minItems == 0

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        out_file.print("{}.n = 0;".format(out_var_name))

    def max_token_num(self):
        return self.maxItems * self.item_generator.max_token_num() + 1
