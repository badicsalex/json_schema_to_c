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
import os.path

from .base import Generator, CType, SchemaError, C_RESERVED
from .enum import EnumType


class UnionType(CType):
    def __init__(self, type_name, description, option_types, type_cache):
        super().__init__(type_name, description)
        self.option_types = option_types

        # Name the members after the option type names, minus their common prefix and the _t suffix.
        prefix_len = len(os.path.commonprefix([t.type_name for t in option_types]))
        self.option_names = [t.type_name[prefix_len:].removesuffix("_t") for t in option_types]
        if any(name[0].isdigit() or name in C_RESERVED for name in self.option_names):
            self.option_names = ["option_" + name for name in self.option_names]

        type_name_base = self.type_name.removesuffix("_t")
        self.tag_type = EnumType(
            type_name_base + "_type_t",
            "Tag telling which union member is set",
            [f"{type_name_base}_{name}".upper() for name in self.option_names],
        )
        self.tag_type = type_cache.try_get_cached(self.tag_type)

    def generate_type_declaration_impl(self, out_file):
        for option_type in self.option_types:
            option_type.generate_type_declaration(out_file)
        self.tag_type.generate_type_declaration(out_file)

        out_file.print(f"typedef struct {self.type_name}_s {{")
        with out_file.indent():
            self.tag_type.generate_field_declaration("type", out_file)
            out_file.print("union {")
            with out_file.indent():
                for option_type, option_name in zip(self.option_types, self.option_names):
                    option_type.generate_field_declaration(option_name, out_file)
            out_file.print("};")
        out_file.print(f"}} {self.type_name};")
        out_file.print("")

    def __eq__(self, other):
        return super().__eq__(other) and self.option_types == other.option_types


class UnionGenerator(Generator):
    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.option_generators = [
            parameters.generator_factory.get_generator_for(
                option,
                parameters.with_suffix(f"anyOf_{i}", self.type_name, f"option_{i}"),
            )
            for i, option in enumerate(schema["anyOf"])
        ]
        for option in self.option_generators:
            if option.c_type is None:
                raise SchemaError(self, "anyOf options must store a value, so a const cannot be one")
        self.c_type = UnionType(
            self.type_name,
            self.description,
            [option.c_type for option in self.option_generators],
            parameters.type_cache,
        )
        self.c_type = parameters.type_cache.try_get_cached(self.c_type)

    @classmethod
    def can_parse_schema(cls, schema):
        return "anyOf" in schema

    def generate_parser_call(self, out_var_name, out_file):
        with out_file.if_block(f"parse_{self.parser_name}(parse_state, {out_var_name})"):
            out_file.print("return true;")

    def generate_parser_bodies(self, out_file):
        option_parsers = []
        for i, option_generator in enumerate(self.option_generators):
            option_generator.generate_parser_bodies(out_file)
            # Give each option a bool-returning parser, so a failed attempt can be caught at the call
            # site (rewind and try the next) without threading a failure action through every generator.
            option_parser = f"parse_{self.parser_name}_try_{i}"
            out_file.print(f"static bool {option_parser}(parse_state_t *parse_state, {option_generator.c_type} *out)")
            with out_file.code_block():
                option_generator.generate_parser_call("out", out_file)
                out_file.print("return false;")
            out_file.print("")
            option_parsers.append(option_parser)

        out_file.print(f"static bool parse_{self.parser_name}(parse_state_t *parse_state, {self.c_type} *out)")
        with out_file.code_block():
            # Each option runs on a copy, so a failed attempt leaves parse_state untouched, and its
            # errors (an expected failure) are muted just on that copy.
            out_file.print("parse_state_t attempt = *parse_state;")
            out_file.print("attempt.inhibit_errors = true;")
            for i, (option_parser, option_name, enum_label) in enumerate(zip(option_parsers, self.c_type.option_names, self.c_type.tag_type.enum_labels)):
                if i != 0:
                    out_file.print("else")
                retry = "" if i == 0 else "attempt = *parse_state, attempt.inhibit_errors = true, "
                with out_file.if_block(f"{retry}!{option_parser}(&attempt, &out->{option_name})"):
                    out_file.print(f"out->type = {enum_label};")
            out_file.print("else")
            with out_file.code_block():
                self.generate_logged_error(
                    ["Invalid anyOf value in '%s': no option matched", "parse_state->current_key"],
                    out_file)
            out_file.print("parse_state->current_token = attempt.current_token;")
            out_file.print("return false;")
        out_file.print("")

    def max_token_num(self):
        # Only one option's value ends up in the document, so the worst case is the largest option.
        return max(option.max_token_num() for option in self.option_generators)
