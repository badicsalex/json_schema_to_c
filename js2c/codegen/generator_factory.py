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
from .array import ArrayGenerator
from .integer import IntegerGenerator, NumericStringGenerator, IntegerStringAnyOfGenerator
from .float import FloatGenerator
from .bool import BoolGenerator
from .object import ObjectGenerator
from .string import StringGenerator
from .enum import EnumGenerator


class GeneratorFactory:
    #pylint: disable=too-few-public-methods
    GENERATORS = [
        EnumGenerator,
        NumericStringGenerator,
        IntegerStringAnyOfGenerator,
        StringGenerator,
        IntegerGenerator,
        FloatGenerator,
        BoolGenerator,
        ObjectGenerator,
        ArrayGenerator,
    ]

    @classmethod
    def get_generator_for(cls, schema, parameters):
        for generator_class in cls.GENERATORS:
            if generator_class.can_parse_schema(schema):
                return generator_class(schema, parameters)
        raise ValueError("Could not find any generators to parse schema: {}.".format(schema))
