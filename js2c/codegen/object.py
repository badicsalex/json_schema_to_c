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
import collections

from .base import Generator


class ObjectGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "required",
        "additionalProperties",
    )
    required = ()
    additionalProperties = True

    def __init__(self, schema, name, args, generator_factory):
        super().__init__(schema, name, args, generator_factory)
        self.fields = collections.OrderedDict()
        for field_name, field_schema in schema['properties'].items():
            self.fields[field_name] = generator_factory.get_generator_for(
                field_schema,
                "{}_{}".format(name, field_name),
                args,
            )
        self.c_type = "{}_t".format(self.name)
        if self.additionalProperties and not self.args.additional_properties_allowed:
            raise ValueError(
                "Either use the --allow-additional-properties command line argument, or set "
                "additionalProperties to false on all object types."
            )

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'object'

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if(parse_{}(parse_state, {}))"
            .format(self.name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def generate_type_declaration(self, out_file, *, force=False):
        _ = force  # This is python's way of saying (void)force

        for field_name, field_generator in self.fields.items():
            field_generator.generate_type_declaration(out_file)

        out_file.print("typedef struct {}_s ".format(self.name) + "{")
        with out_file.indent():
            for field_name, field_generator in self.fields.items():
                field_generator.generate_field_declaration(
                    field_name,
                    out_file
                )
        out_file.print("}} {};".format(self.c_type))
        out_file.print("")

    def generate_seen_flags(self, out_file):
        for field_name in self.fields:
            out_file.print("bool seen_{} = false;".format(field_name))

    def generate_default_field_setting(self, out_file):
        for field_name, field_generator in self.fields.items():
            if not field_generator.has_default_value():
                continue
            out_file.print("if (!seen_{})".format(field_name))
            with out_file.code_block():
                field_generator.generate_set_default_value(
                    "out->{}".format(field_name),
                    out_file
                )

    def generate_required_checks(self, out_file):
        for field_name, field_generator in self.fields.items():
            if field_generator.has_default_value():
                continue
            if field_name not in self.required:
                raise ValueError(
                    "All fields must either be required or have a default value ({})"
                    .format(field_name)
                )
            out_file.print("if (!seen_{}) ".format(field_name))
            with out_file.code_block():
                self.generate_logged_error("Missing required field in {}: {}".format(self.name, field_name), out_file)

    def generate_field_parsers(self, out_file):
        for field_name, field_generator in self.fields.items():
            out_file.print('if (current_string_is(parse_state, "{}"))'.format(field_name))
            with out_file.code_block():
                out_file.print("if(seen_{}) ".format(field_name))
                with out_file.code_block():
                    self.generate_logged_error("Duplicate field definition in {}: {}".format(self.name, field_name), out_file)
                out_file.print("seen_{} = true;".format(field_name))
                out_file.print("parse_state->current_token += 1;")
                field_generator.generate_parser_call(
                    "&out->{}".format(field_name),
                    out_file
                )
            out_file.print("else")
        with out_file.code_block():
            if self.args.additional_properties_allowed:
                out_file.print("parse_state->current_token += 1;")
                out_file.print("builtin_skip(parse_state);")
            else:
                self.generate_logged_error(["Unknown field in {}: %.*s".format(self.name), "CURRENT_STRING_FOR_ERROR(parse_state)"], out_file)

    def generate_parser_bodies(self, out_file):
        for field_generator in self.fields.values():
            field_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{}(parse_state_t* parse_state, {}* out)".format(self.name, self.c_type))
        with out_file.code_block():
            out_file.print("if(check_type(parse_state, JSMN_OBJECT))")
            with out_file.code_block():
                out_file.print("return true;")

            self.generate_seen_flags(out_file)

            out_file.print("const uint64_t n = parse_state->tokens[parse_state->current_token].size;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (uint64_t i = 0; i < n; ++ i)")
            with out_file.code_block():
                self.generate_field_parsers(out_file)

            self.generate_required_checks(out_file)
            self.generate_default_field_setting(out_file)
            out_file.print("return false;")
        out_file.print("")

    def has_default_value(self):
        return len(self.required) == 0 and all(field_generator.has_default_value() for field_generator in self.fields.values())

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        for field_name, field_generator in self.fields.items():
            field_generator.generate_set_default_value(
                "{}.{}".format(out_var_name, field_name),
                out_file
            )

    def max_token_num(self):
        return sum(1 + field_generator.max_token_num() for field_generator in self.fields.values()) + 1
