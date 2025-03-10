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
import json, os
from collections import OrderedDict
from urllib.parse import urlparse


# dictionary of schemas indexed by their canonical file path
schema_cache: dict[str, any] = {}

# todo check for file location
def get_schema_from_path(path: str, relative_to: str) -> any:
    path = os.path.abspath(os.path.join(os.path.dirname(relative_to), path))
    if path in schema_cache:
        if schema_cache[path] is None: # check if slot is already being computed
            raise ValueError("Circular dependency detected in JSON schema reference")
    else:
        schema_cache[path] = None # reserve slot to avoid circular references
        schema_cache[path] = load_schema(path)
    return schema_cache[path]

# WARNING: reviewing the following algorithm might cause brain damage
# Sorry for that.
def resolve_children(full_schema, part_to_resolve, schema_filepath: str):
    if part_to_resolve is None:
        return
    if isinstance(part_to_resolve, (str, int, bool, float)):
        return
    if isinstance(part_to_resolve, list):
        for i, v in enumerate(part_to_resolve):
            part_to_resolve[i] = resolve_ref(full_schema, v, schema_filepath)
            resolve_children(full_schema, v, schema_filepath)
        return
    if isinstance(part_to_resolve, dict):
        for k, v in part_to_resolve.items():
            part_to_resolve[k] = resolve_ref(full_schema, v, schema_filepath)
            resolve_children(full_schema, v, schema_filepath)
        # terminate by cleaning up $defs
        if part_to_resolve == full_schema and "$defs" in full_schema:
            del full_schema["$defs"]
        return
    raise ValueError("Value {} is not supported by the schema loader".format(part_to_resolve))


def resolve_ref(full_schema, part_to_resolve, schema_filepath: str):
    if not isinstance(part_to_resolve, dict) or "$ref" not in part_to_resolve:
        return part_to_resolve
    if len(part_to_resolve) > 1:
        raise ValueError("Reference nodes should not contain other fields")

    ref_str: str = part_to_resolve["$ref"]
    ref_uri = urlparse(ref_str)

    if ref_uri.scheme != "" and ref_uri.scheme != "file":
        raise ValueError("Unsupported references scheme: " + ref_uri.scheme)
    if ref_uri.netloc != "" or ref_uri.params != "" or ref_uri.query != "":
        raise ValueError("Unsupported references: " + ref_str)
    if not ref_uri.fragment.startswith("/"):
        raise ValueError("Only path-like references are supported. (Id-based references are not)")

    if ref_uri.scheme == "file" or ref_uri.path != "":
        full_schema = get_schema_from_path(ref_uri.path, schema_filepath)

    ref_str = ref_uri.fragment[1:] + '/'
    replacement = full_schema
    while ref_str:
        part, ref_str = ref_str.split('/', 1)
        replacement = replacement[part]
    return replacement
# WARNING OVER


def merge_single_pair(element1, element2, key: str):
    if type(element1) is not type(element2):
        raise TypeError(
            "Field types are different in allOf/anyOf/oneOf declaration: '{}' vs. '{}'"
            .format(element1, element2)
        )
    if isinstance(element1, dict):
        return merge_dict(element1, element2)
    if isinstance(element1, list):
        return element1 + [item for item in element2 if item not in element1]
    if element1 == element2:
        return element1
    if isinstance(element1, int) and isinstance(element2, int):
        if key in ("minimum", "exclusiveMinimum", "minLength"): return max(element1, element2)
        if key in ("maximum", "exclusiveMaximum", "maxLength"): return min(element1, element2)
    raise ValueError(
        "Could not merge fields for allOf/anyOf/oneOf declaration: '{}' and '{}'"
        .format(element1, element2)
    )


def merge_dict(schema1, schema2):
    result = schema1.copy()
    for key, value in schema2.items():
        if key in result:
            result[key] = merge_single_pair(result[key], value, key)
        else:
            result[key] = value
    return result


def resolve_all_of(schema):
    if isinstance(schema, list):
        return [resolve_all_of(item) for item in schema]
    elif isinstance(schema, dict):
        result = OrderedDict((k, resolve_all_of(v)) for k, v in schema.items() if k != "allOf")
        if "allOf" in schema:
            for schema_to_process in schema["allOf"]:
                schema_to_process = resolve_all_of(schema_to_process)
                result = merge_dict(result, schema_to_process)
        return result
    else:
        return schema


# replace all oneOf by anyOf
def resolve_one_of(schema):
    if isinstance(schema, dict):
        if "oneOf" in schema:
            if "anyOf" in schema:
                schema["anyOf"] += schema.pop("oneOf")
            else:
                schema["anyOf"] = schema.pop("oneOf")
        for val in schema.values():
            resolve_one_of(val)
    elif isinstance(schema, list):
        for elem in schema:
            resolve_one_of(elem)


def resolve_any_of(schema):
    if isinstance(schema, list):
        return [resolve_any_of(item) for item in schema]
    elif isinstance(schema, dict):
        if "anyOf" in schema:
            common_data = OrderedDict((k, resolve_any_of(v)) for k, v in schema.items() if k != "anyOf" and k != "$id")
            result = OrderedDict((k, resolve_any_of(v)) for k, v in schema.items() if k == "$id")
            result["anyOf"] = [
                merge_dict(resolve_any_of(schema_to_process), common_data)
                for schema_to_process in schema["anyOf"]
            ]
            return result
        else:
            return OrderedDict((k, resolve_any_of(v)) for k, v in schema.items())
    else:
        return schema


def load_schema(schema_filepath: str):
    with open(schema_filepath) as schema_file:
        schema = json.load(schema_file, object_pairs_hook=OrderedDict)
    resolve_children(schema, schema, schema_filepath)
    schema = resolve_all_of(schema)
    resolve_one_of(schema)
    schema = resolve_any_of(schema)
    return schema
