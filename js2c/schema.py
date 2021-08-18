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
import json
from collections import OrderedDict


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


def all_of_merge_single_pair(element1, element2):
    if type(element1) is not type(element2):
        raise TypeError(
            "Field types are different in allOf declaration: '{}' vs. '{}'"
            .format(element1, element2)
        )
    if isinstance(element1, dict):
        return all_of_merge_dict(element1, element2)
    if isinstance(element1, list):
        return element1 + [item for item in element2 if item not in element1]
    if element1 == element2:
        return element1
    raise ValueError(
        "Could not merge fields for allOf declaration: '{}' and '{}'"
        .format(element1, element2)
    )


def all_of_merge_dict(schema1, schema2):
    result = schema1.copy()
    for key, value in schema2.items():
        if key in result:
            result[key] = all_of_merge_single_pair(result[key], value)
        else:
            result[key] = value
    return result


def resolve_all_of(schema):
    if not isinstance(schema, dict):
        # TODO: Also process arrays in the schema. I'm not sure it's needed though, there are not many arrays
        #       in schema definitions, and I think none of them need allOf expansion.
        return schema

    result = OrderedDict((k, resolve_all_of(v)) for k, v in schema.items() if k != "allOf")
    if "allOf" in schema:
        for schema_to_process in schema["allOf"]:
            schema_to_process = resolve_all_of(schema_to_process)
            result = all_of_merge_dict(result, schema_to_process)
    return result


def load_schema(schema_file):
    schema = json.load(schema_file, object_pairs_hook=OrderedDict)
    assert '$id' in schema, "All schemas must have an ID (a field named '$id')"
    resolve_children(schema, schema)
    schema = resolve_all_of(schema)
    return schema
