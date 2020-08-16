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
import re


class NoDefaultValue(Exception):
    pass


GeneratorInitParametersBase = namedtuple(
    "GeneratorInitParameters",
    (
        'parser_name',
        'type_name',
        'settings',
        'generator_factory',
        'type_cache'
    )
)


class GeneratorInitParameters(GeneratorInitParametersBase):
    __slots__ = ()

    def with_suffix(self, type_name, suffix):
        # Remove _t suffix if present
        type_name = re.sub("_t$", "", type_name)
        return GeneratorInitParameters(
            "{}_{}".format(self.parser_name, suffix),
            "{}_{}_t".format(type_name, suffix),
            self.settings,
            self.generator_factory,
            self.type_cache,
        )


class Generator(ABC):
    JSON_FIELDS = (
        "description",
        "js2cDefault",
        "js2cType",
    )

    c_type = None
    description = None
    js2cDefault = None
    js2cType = None

    def __init__(self, schema, parameters):
        for attr in self.JSON_FIELDS:
            if attr in schema:
                setattr(self, attr, schema[attr])

        self.settings = parameters.settings
        self.parser_name = parameters.parser_name

        if self.js2cType is not None:
            self.type_name = self.js2cType
        elif "$id" in schema:
            # Remove starting # if present
            self.type_name = re.sub("^#", "", schema["$id"]) + "_t"
        else:
            self.type_name = parameters.type_name

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


class CType():
    def __init__(self, type_name, description):
        self.type_name = type_name
        self.description = description
        self.declaration_generated = False

    def __str__(self):
        return self.type_name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.__dict__)

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "{} {};".format(self.type_name, field_name), self.description
        )

    def generate_type_declaration(self, out_file):
        if self.declaration_generated:
            return
        self.generate_type_declaration_impl(out_file)
        self.declaration_generated = True

    def generate_type_declaration_impl(self, out_file):
        # Simple types (e.g. uint64_t) should already be declared
        pass

    def __eq__(self, other):
        # Description deliberately left out. It will be the same type
        # The main use-case is documenting a description differently on different
        # parts of the JSON. The main result here will be a wrong docstring on the type,
        # which is an OK trade-off.
        return self.__class__ == other.__class__ and self.type_name == other.type_name
