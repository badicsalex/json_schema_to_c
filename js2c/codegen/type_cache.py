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
from typing import TypeVar

from .base import CType, SchemaError

CTypeT = TypeVar("CTypeT", bound=CType)


class TypeCache:
    #pylint: disable=too-few-public-methods
    def __init__(self) -> None:
        self.types: dict[str, CType] = {}

    def try_get_cached(self, c_type: CTypeT, path_in_schema: str) -> CTypeT:
        if c_type.type_name in self.types:
            cached_type = self.types[c_type.type_name]
            if cached_type != c_type:
                raise SchemaError(path_in_schema, f"Two different types with the same name: {c_type.type_name}")
            # __eq__ compares classes too, so an equal type is the same class.
            assert isinstance(cached_type, type(c_type))
            return cached_type
        self.types[c_type.type_name] = c_type
        return c_type
