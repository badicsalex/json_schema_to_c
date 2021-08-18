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
import collections

from .base import Generator, CType


class ObjectType(CType):
    def __init__(self, type_name, description, fields):
        super().__init__(type_name, description)
        assert isinstance(fields, collections.OrderedDict), \
            "fields must be an OrderedDict, as we depend on the field order check of == in __eq__"
        self.fields = fields

    def generate_type_declaration_impl(self, out_file):
        for field_name, field_generator in self.fields.items():
            field_generator.generate_type_declaration(out_file)

        out_file.print("typedef struct {}_s ".format(self.type_name) + "{")
        with out_file.indent():
            for field_name, field_generator in self.fields.items():
                field_generator.generate_field_declaration(
                    field_name,
                    out_file
                )
        out_file.print("}} {};".format(self.type_name))
        out_file.print("")

    def __eq__(self, other):
        return (
            super().__eq__(other) and
            self.fields == other.fields
        )


class ObjectGenerator(Generator):
    JSON_FIELDS = Generator.JSON_FIELDS + (
        "required",
        "additionalProperties",
    )
    required = ()
    additionalProperties = True

    def __init__(self, schema, parameters):
        super().__init__(schema, parameters)
        self.fields = collections.OrderedDict()
        for field_name, field_schema in schema['properties'].items():
            self.fields[field_name] = parameters.generator_factory.get_generator_for(
                field_schema,
                parameters.with_suffix(self.type_name, field_name),
            )
        self.c_type = ObjectType(
            self.type_name,
            self.description,
            collections.OrderedDict((k, v.c_type) for k, v in self.fields.items())
        )
        self.c_type = parameters.type_cache.try_get_cached(self.c_type)

        if self.additionalProperties and not self.settings.allow_additional_properties:
            raise ValueError(
                "Either use the --allow-additional-properties command line argument, or set "
                "additionalProperties to false on all object types."
            )

    @classmethod
    def can_parse_schema(cls, schema):
        return schema.get('type') == 'object'

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if (parse_{}(parse_state, {}))"
            .format(self.parser_name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

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
            out_file.print("if (!seen_{})".format(field_name))
            with out_file.code_block():
                self.generate_logged_error("Missing required field in '%s': {}".format(field_name), out_file)

    def generate_key_children_check(self, out_file):
        out_file.print("if (CURRENT_TOKEN(parse_state).size > 1)")
        with out_file.code_block():
            self.generate_logged_error(
                [
                    "Missing separator between values in '%s', after key: %.*s",
                    "parse_state->current_key",
                    "CURRENT_STRING_FOR_ERROR(parse_state)"
                ],
                out_file
            )

        out_file.print("if (CURRENT_TOKEN(parse_state).size < 1)")
        with out_file.code_block():
            self.generate_logged_error(
                [
                    "Missing value in '%s', after key: %.*s",
                    "parse_state->current_key",
                    "CURRENT_STRING_FOR_ERROR(parse_state)"
                ],
                out_file
            )

    def generate_field_parsers(self, out_file):
        self.generate_key_children_check(out_file)
        for field_name, field_generator in self.fields.items():
            out_file.print('if (current_string_is(parse_state, "{}"))'.format(field_name))
            with out_file.code_block():
                out_file.print("if (seen_{})".format(field_name))
                with out_file.code_block():
                    self.generate_logged_error("Duplicate field definition in '%s': {}".format(field_name), out_file)
                out_file.print("seen_{} = true;".format(field_name))
                out_file.print("parse_state->current_token += 1;")
                out_file.print("const char* saved_key = parse_state->current_key;")
                out_file.print("parse_state->current_key = \"{}\";".format(field_name))
                field_generator.generate_parser_call(
                    "&out->{}".format(field_name),
                    out_file
                )
                out_file.print("parse_state->current_key = saved_key;")
            out_file.print("else")
        with out_file.code_block():
            if self.settings.allow_additional_properties:
                out_file.print("parse_state->current_token += 1;")
                out_file.print("builtin_skip(parse_state);")
            else:
                self.generate_logged_error(["Unknown field in '%s': %.*s", "parse_state->current_key", "CURRENT_STRING_FOR_ERROR(parse_state)"], out_file)

    def generate_parser_bodies(self, out_file):
        for field_generator in self.fields.values():
            field_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{}(parse_state_t *parse_state, {} *out)".format(self.parser_name, self.c_type))
        with out_file.code_block():
            out_file.print("if (check_type(parse_state, JSMN_OBJECT))")
            with out_file.code_block():
                out_file.print("return true;")

            self.generate_seen_flags(out_file)

            out_file.print("const int object_start_token = parse_state->current_token;")
            out_file.print("const uint64_t n = parse_state->tokens[parse_state->current_token].size;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (uint64_t i = 0; i < n; ++i)")
            with out_file.code_block():
                self.generate_field_parsers(out_file)

            # This little magic is needed because both required checks and default setting
            # use CURRENT_TOKEN, which may be past the token list by now, and also we want
            # to report the issue at the start of the object.
            out_file.print("const int saved_current_token = parse_state->current_token;")
            out_file.print("parse_state->current_token = object_start_token;")

            self.generate_required_checks(out_file)
            self.generate_default_field_setting(out_file)

            out_file.print("parse_state->current_token = saved_current_token;")

            out_file.print("return false;")
        out_file.print("")

    def has_default_value(self):
        if super().has_default_value():
            return True
        return len(self.required) == 0 and all(field_generator.has_default_value() for field_generator in self.fields.values())

    def generate_set_default_value(self, out_var_name, out_file):
        if super().generate_set_default_value(out_var_name, out_file):
            return
        for field_name, field_generator in self.fields.items():
            field_generator.generate_set_default_value(
                "{}.{}".format(out_var_name, field_name),
                out_file
            )

    def max_token_num(self):
        return sum(1 + field_generator.max_token_num() for field_generator in self.fields.values()) + 1
