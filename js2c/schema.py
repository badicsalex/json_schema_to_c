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
import json


# WARNING: reviewing the following algorithm might cause brain damage
# Sorry for that.
def resolve_children(full_schema, part_to_resolve):
    if part_to_resolve is None:
        return
    if isinstance(part_to_resolve, (str, int, bool, float)):
        return
    if isinstance(part_to_resolve, list):
        for i, v in enumerate(part_to_resolve):
            part_to_resolve[i] = resolve_ref(full_schema, v)
            resolve_children(full_schema, v)
        return
    if isinstance(part_to_resolve, dict):
        for k, v in part_to_resolve.items():
            part_to_resolve[k] = resolve_ref(full_schema, v)
            resolve_children(full_schema, v)
        return
    raise ValueError("Value {} is not supported by the schema loader".format(part_to_resolve))


def resolve_ref(full_schema, part_to_resolve):
    if not isinstance(part_to_resolve, dict) or "$ref" not in part_to_resolve:
        return part_to_resolve
    if len(part_to_resolve) > 1:
        raise ValueError("Reference nodes should not contain other fields")

    ref_str = part_to_resolve["$ref"]
    if ref_str[0] != '#':
        raise ValueError("Only in-file references are supported")
    if ref_str[1] != '/':
        raise ValueError("Only path-like references are supported. (Id-based references are not)")
    ref_str = ref_str[2:] + '/'
    replacement = full_schema
    while ref_str:
        part, ref_str = ref_str.split('/', 1)
        replacement = replacement[part]
    return replacement
# WARNING OVER


def load_schema(schema_file):
    schema = json.load(schema_file)
    assert '$id' in schema, "All schemas must have an ID (a field named '$id')"
    resolve_children(schema, schema)
    return schema
