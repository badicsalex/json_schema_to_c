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
from typing import Optional
from .base import Generator


class ArrayGenerator(Generator):
    minItems: int = 0
    maxItems: Optional[int] = None

    def __init__(self, schema, name, args, generator_factory):
        super().__init__(schema, name, args, generator_factory)
        if self.maxItems is None:
            raise ValueError("Arrays must have maxItems")

        self.item_generator = generator_factory.get_generator_for(
            schema["items"],
            "{}_item".format(name),
            args
        )
        self.c_type = "{}_t".format(self.name)

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'array'

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if(parse_{}(parse_state, {}))"
            .format(self.name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def generate_type_declaration(self, out_file, *, force=False):
        _ = force  # basically (void)force

        self.item_generator.generate_type_declaration(out_file)

        out_file.print("typedef struct {}_s ".format(self.name) + "{")
        with out_file.indent():
            out_file.print_with_docstring("uint64_t n;", "The number of elements in the array")
            self.item_generator.generate_field_declaration(
                "items[{}]".format(self.maxItems), out_file
            )
        out_file.print("}} {};".format(self.c_type))
        out_file.print("")

    def generate_range_checks(self, out_file):
        out_file.print("if (n > {})".format(self.maxItems))
        with out_file.code_block():
            self.generate_logged_error(
                ["Array {} too large. Length: %i. Maximum length: {}.".format(self.name, self.maxItems), "n"],
                out_file
            )
        if self.minItems:
            out_file.print("if (n < {})".format(self.minItems))
            with out_file.code_block():
                self.generate_logged_error(
                    ["Array {} too small. Length: %i. Minimum length: {}.".format(self.name, self.minItems), "n"],
                    out_file
                )

    def generate_parser_bodies(self, out_file):
        self.item_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{}(parse_state_t* parse_state, {}* out)".format(self.name, self.c_type))
        with out_file.code_block():
            out_file.print("if(check_type(parse_state, JSMN_ARRAY))")
            with out_file.code_block():
                out_file.print("return true;")
            out_file.print("int i;")
            out_file.print("const int n = parse_state->tokens[parse_state->current_token].size;")
            self.generate_range_checks(out_file)
            out_file.print("out->n = n;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (i = 0; i < n; ++ i)")
            with out_file.code_block():
                self.item_generator.generate_parser_call(
                    "&out->items[i]",
                    out_file
                )
            out_file.print("return false;")
        out_file.print("")

    def has_default_value(self):
        return self.minItems == 0

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        out_file.print("{}.n = 0;".format(out_var_name))

    def max_token_num(self):
        return self.maxItems * self.item_generator.max_token_num() + 1
