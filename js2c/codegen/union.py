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
import re

from .base import Generator, CType, GeneratorInitParameters
from .code_block_printer import CodeBlockPrinter
from .enum import EnumType
from .type_cache import TypeCache


# Return the longest prefix of all list elements.
# from https://stackoverflow.com/a/6718435 (CC BY-SA 3.0)
def commonprefix(m):
    if not m: return ''
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


class UnionType(CType):
    def __init__(self, type_name: str, description: str, option_types: list[CType], type_cache: TypeCache):
        super().__init__(type_name, description)
        self.option_types = option_types

        # try to infer nice option names
        prefix_len = len(commonprefix([t.type_name for t in self.option_types]))
        self.option_names = [re.sub("_t$", "", t.type_name[prefix_len:]) for t in self.option_types]
        if any([n[0].isdigit() for n in self.option_names]):
            self.option_names = ["option_" + n for n in self.option_names]

        type_name_base = re.sub("_t$", "", self.type_name)
        self.inner_enum_type = EnumType(
            type_name_base + "_type_t",
            "Key indicating which union option is used",
            ["{}_{}".format(type_name_base, n).upper() for n in self.option_names],
        )
        self.inner_enum_type = type_cache.try_get_cached(self.inner_enum_type)


    def generate_type_declaration_impl(self, out_file: CodeBlockPrinter):
        for option_type in self.option_types:
            option_type.generate_type_declaration(out_file)

        self.inner_enum_type.generate_type_declaration_impl(out_file)

        out_file.print("typedef struct {}_s ".format(self.type_name) + "{")
        with out_file.indent():
            self.inner_enum_type.generate_field_declaration("type", out_file)
            out_file.print("union {")
            with out_file.indent():
                for option_type, option_name in zip(self.option_types, self.option_names):
                    option_type.generate_field_declaration(option_name, out_file)
            out_file.print("};")
        out_file.print("}} {};".format(self.type_name))
        out_file.print("")

    def __eq__(self, other):
        return (
            super().__eq__(other) and
            self.option_types == other.option_types
        )


class UnionGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS

    def __init__(self, schema, parameters: GeneratorInitParameters):
        super().__init__(schema, parameters)

        self.option_generators: list[Generator] = [
            parameters.generator_factory.get_generator_for(
                option,
                parameters.with_suffix("anyOf_{}".format(i), self.type_name, "option_{}".format(i)),
            )
            for i, option in enumerate(schema["anyOf"])
        ]

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

    def generate_parser_call(self, out_var_name: str, out_file: CodeBlockPrinter, on_err="return true;"):
        parser_call = "parse_{}(parse_state, {})".format(self.parser_name, out_var_name)
        with out_file.if_block(parser_call):
            out_file.print(on_err)

    def generate_parser_bodies(self, out_file: CodeBlockPrinter):
        for option_generator in self.option_generators:
            option_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{}(parse_state_t *parse_state, {} *out)".format(self.parser_name, self.c_type))
        with out_file.code_block():
            out_file.print("bool missing_value = true;")
            out_file.print("uint64_t saved_token = parse_state->current_token;")
            out_file.print("const char *saved_key = parse_state->current_key;")
            restore_ctx = ("parse_state->current_token = saved_token;",
                           "parse_state->current_key = saved_key;",
                           "break;")
            for option_generator, option_name, enum_label in zip(self.option_generators, self.c_type.option_names, self.c_type.inner_enum_type.enum_labels):
                with out_file.if_block("missing_value"):
                    out_file.print("do")
                    with out_file.code_block():
                        option_generator.generate_parser_call("&out->" + option_name, out_file, on_err=restore_ctx)
                        out_file.print("out->type = {};".format(enum_label))
                        out_file.print("missing_value = false;")
                    out_file.print("while(0);")

            with out_file.if_block("missing_value"):
                self.generate_logged_error(
                    [
                        "Invalid anyOf/oneOf value in '%s': could not match any schema",
                        "parse_state->current_key"
                    ],
                    out_file)

            out_file.print("return false;")
        out_file.print("")

    def max_token_num(self):
        return sum([option.max_token_num() for option in self.option_generators]) + 1
