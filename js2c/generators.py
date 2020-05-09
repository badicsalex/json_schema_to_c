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
import os
import re
from typing import get_type_hints, Optional, List

from abc import ABC, abstractmethod

from .utils import CodeBlockPrinter

DIR_OF_THIS_FILE = os.path.dirname(__file__)

NOTE_FOR_GENERATED_FILES = """
/* This file was generated by JSON Schema to C.
 * Any changes made to it will be lost on regeneration. */
"""


class NoDefaultValue(Exception):
    pass


class Generator(ABC):
    description: str = ''

    def __init__(self, schema, name, generators):
        _ = generators  # used only by subclasses
        self.name = name
        for attr in get_type_hints(self.__class__):
            if attr in schema:
                setattr(self, attr, schema[attr])

    @abstractmethod
    def generate_field_declaration(self, field_name, out_file):
        pass

    @abstractmethod
    def generate_parser_call(self, out_var_name, out_file):
        pass

    def generate_type_declaration(self, out_file, *, force=False):
        if force:
            out_file.print("typedef ")
            self.generate_field_declaration(self.name + "_t", out_file)

    def generate_parser_bodies(self, out_file):
        pass

    @classmethod
    def has_default_value(cls):
        return False

    def generate_set_default_value(self, out_var_name, out_file):
        raise NoDefaultValue("Default values not supported for {}".format(self.__class__.__name__))

    @classmethod
    def generate_logged_error(cls, log_message, out_file):
        if isinstance(log_message, str):
            out_file.print("LOG_ERROR(CURRENT_TOKEN(parse_state).start, \"{}\")".format(log_message))
        else:
            assert len(log_message) > 1, "Use a simple string, not a 1 element array."
            out_file.print(
                "LOG_ERROR(CURRENT_TOKEN(parse_state).start, \"{}\", {})"
                .format(
                    log_message[0],
                    ", ".join(log_message[1:]),
                )
            )
        out_file.print("return true;")


class StringGenerator(Generator):
    minLength: int = 0
    maxLength: Optional[int] = None
    default: Optional[str] = None

    def __init__(self, schema, name, generators):
        super().__init__(schema, name, generators)
        if self.maxLength is None:
            raise ValueError("Strings must have maxLength")

        if self.default is not None and len(self.default) > self.maxLength:
            raise ValueError("String default value longer than maxLength")

        if self.default is not None and len(self.default) < self.minLength:
            print("MinLength", self.minLength)
            raise ValueError("String default value shorter than minLength")

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "char {}[{}];".format(field_name, self.maxLength + 1), self.description
        )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if(builtin_parse_string(parse_state, {}[0], {}, {}))"
            .format(out_var_name, self.minLength, self.maxLength)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def has_default_value(self):
        return self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        out_file.print(
            'memcpy({dst}, "{src}", {size});'.format(
                dst=out_var_name,
                src=self.default,
                size=len(self.default) + 1
            )
        )


class NumberGenerator(Generator):
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    exclusiveMinimum: Optional[int] = None
    exclusiveMaximum: Optional[int] = None
    default: Optional[int] = None

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "int64_t {};".format(field_name), self.description
        )

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
            "if(builtin_parse_number(parse_state, {}))"
            .format(out_var_name)
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
        out_file.print("{} = {};".format(out_var_name, self.default))


class BoolGenerator(Generator):
    default: Optional[bool] = None

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "bool {};".format(field_name), self.description
        )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if(builtin_parse_bool(parse_state, {}))"
            .format(out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def has_default_value(self):
        return self.default is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        out_file.print(
            "{} = {};".format(
                out_var_name,
                'true' if self.default else 'false'
            )
        )


class ObjectGenerator(Generator):
    required: List[int] = []
    additionalProperties: bool = True

    def __init__(self, schema, name, generators):
        super().__init__(schema, name, generators)
        self.fields = {}
        for field_name, field_schema in schema['properties'].items():
            generator_class = generators[field_schema['type']]
            self.fields[field_name] = generator_class(
                field_schema,
                "{}_{}".format(name, field_name),
                generators,
            )

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "{}_t {};".format(self.name, field_name), self.description
        )

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
        out_file.print("}} {}_t;".format(self.name))
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
            self.generate_logged_error(["Unknown field in {}: %.*s".format(self.name), "CURRENT_STRING_FOR_ERROR(parse_state)"], out_file)

    def generate_parser_bodies(self, out_file):
        if self.additionalProperties:
            raise ValueError(
                "Object types must have additionalProperties set to false"
            )

        for field_generator in self.fields.values():
            field_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{name}(parse_state_t* parse_state, {name}_t* out)".format(name=self.name))
        with out_file.code_block():
            out_file.print("if(check_type(parse_state, JSMN_OBJECT))")
            with out_file.code_block():
                out_file.print("return true;")

            out_file.print("uint64_t i;")
            self.generate_seen_flags(out_file)

            out_file.print("const uint64_t n = parse_state->tokens[parse_state->current_token].size;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (i = 0; i < n; ++ i)")
            with out_file.code_block():
                self.generate_field_parsers(out_file)

            self.generate_required_checks(out_file)
            self.generate_default_field_setting(out_file)
            out_file.print("return false;")
        out_file.print("")


class ArrayGenerator(Generator):
    minItems: int = 0
    maxItems: Optional[int] = None

    def __init__(self, schema, name, generators):
        super().__init__(schema, name, generators)
        if self.maxItems is None:
            raise ValueError("Arrays must have maxItems")
        item_generator_class = generators[schema["items"]["type"]]
        self.item_generator = item_generator_class(
            schema["items"],
            "{}_item".format(name),
            generators
        )

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "{}_t {};".format(self.name, field_name), self.description
        )

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
        out_file.print("}} {}_t;".format(self.name))
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

        out_file.print("static bool parse_{name}(parse_state_t* parse_state, {name}_t* out)".format(name=self.name))
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


GENERATORS = {
    "string": StringGenerator,
    "integer": NumberGenerator,
    "boolean": BoolGenerator,
    "object": ObjectGenerator,
    "array": ArrayGenerator,
}


def generate_root_parser(schema, out_file):
    out_file.print("bool json_parse_{id}(const char* json_string, {id}_t* out)".format(id=schema['$id']))
    with out_file.code_block():
        out_file.print("parse_state_t parse_state_var;")
        out_file.print("parse_state_t* parse_state = &parse_state_var;")
        out_file.print("if(builtin_parse_json_string(parse_state, json_string))")
        with out_file.code_block():
            out_file.print("return true;")
        root_generator_class = GENERATORS[schema['type']]
        root_generator = root_generator_class(schema, schema['$id'], GENERATORS)
        root_generator.generate_parser_call(
            "out",
            out_file,
        )
        out_file.print("return false;")
    out_file.print("")


def generate_parser_h(schema, h_file, prefix, postfix):
    h_file_name = h_file.name
    h_file = CodeBlockPrinter(h_file)

    h_file.write(NOTE_FOR_GENERATED_FILES)

    header_guard_name = re.sub("[^A-Z0-9]", "_", os.path.basename(h_file_name).upper())
    h_file.print("#ifndef {}".format(header_guard_name))
    h_file.print("#define {}".format(header_guard_name))

    h_file.print("#include <stdint.h>")
    h_file.print("#include <stdbool.h>")

    if prefix:
        h_file.print_separator("User-added prefix")
        h_file.write(prefix)

    h_file.print_separator("Generated type declarations")
    root_generator_class = GENERATORS[schema['type']]
    root_generator = root_generator_class(schema, schema['$id'], GENERATORS)
    root_generator.generate_type_declaration(h_file, force=True)
    h_file.print("bool json_parse_{id}(const char* json_string, {id}_t* out);".format(id=schema['$id']))

    if postfix:
        h_file.print_separator("User-added postfix")
        h_file.write(postfix)

    h_file.print("#endif /* {} */".format(header_guard_name))


def generate_parser_c(schema, c_file, h_file_name, prefix, postfix):
    c_file = CodeBlockPrinter(c_file)

    c_file.write(NOTE_FOR_GENERATED_FILES)
    c_file.print('#include "{}"'.format(h_file_name))

    if prefix:
        c_file.print_separator("User-added prefix")
        c_file.write(prefix)

    with open(os.path.join(DIR_OF_THIS_FILE, '..', 'jsmn', 'jsmn.h')) as jsmn_h:
        c_file.print("")
        c_file.print('#define JSMN_STATIC')
        c_file.print("")
        c_file.print_separator("jsmn.h (From https://github.com/zserge/jsmn)")
        c_file.write(jsmn_h.read())
        c_file.print("")

    with open(os.path.join(DIR_OF_THIS_FILE, 'builtin_parsers.c')) as builtins_file:
        c_file.print_separator("builtin_parsers.c")
        c_file.write(builtins_file.read())
        c_file.print("")

    c_file.print_separator("Generated parsers")
    c_file.print("")
    root_generator_class = GENERATORS[schema['type']]
    root_generator = root_generator_class(schema, schema['$id'], GENERATORS)
    root_generator.generate_parser_bodies(c_file)
    generate_root_parser(schema, c_file)

    if postfix:
        c_file.print_separator("User-added postfix")
        c_file.write(postfix)
