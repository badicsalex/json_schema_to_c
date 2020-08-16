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
from abc import ABC, abstractmethod
from collections import namedtuple


class NoDefaultValue(Exception):
    pass


GeneratorInitParametersBase = namedtuple(
    "GeneratorInitParameters",
    (
        'name',
        'settings',
        'generator_factory'
    )
)


class GeneratorInitParameters(GeneratorInitParametersBase):
    __slots__ = ()

    def with_suffix(self, suffix):
        return GeneratorInitParameters(
            "{}_{}".format(self.name, suffix),
            self.settings,
            self.generator_factory
        )


class Generator(ABC):
    JSON_FIELDS = (
        "description",
        "js2cDefault",
    )

    c_type = None
    description = None
    js2cDefault = None

    def __init__(self, schema, parameters):
        self.settings = parameters.settings
        self.name = parameters.name
        if "$id" in schema:
            self.name = schema["$id"]
            if self.name[0] == '#':
                self.name = self.name[1:]
        for attr in self.JSON_FIELDS:
            if attr in schema:
                setattr(self, attr, schema[attr])

    @abstractmethod
    def generate_parser_call(self, out_var_name, out_file):
        pass

    @abstractmethod
    def max_token_num(self):
        pass

    @classmethod
    @abstractmethod
    def can_parse_schema(cls, schema):
        pass

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "{} {};".format(self.c_type, field_name), self.description
        )

    def generate_type_declaration(self, out_file, *, force=False):
        if force:
            out_file.print("typedef ")
            self.generate_field_declaration(self.name + "_t", out_file)

    def generate_parser_bodies(self, out_file):
        pass

    def has_default_value(self):
        return self.js2cDefault is not None

    def generate_set_default_value(self, out_var_name, out_file):
        assert self.has_default_value(), "Caller is responsible for checking this."
        if self.js2cDefault is None:
            return False
        out_file.print("{} = {};".format(out_var_name, self.js2cDefault))
        return True

    @classmethod
    def generate_logged_error(cls, log_message, out_file):
        if isinstance(log_message, str):
            out_file.print("LOG_ERROR(CURRENT_TOKEN(parse_state).start, \"{}\", parse_state->current_key)".format(log_message))
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
