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
import os
from collections import OrderedDict
from urllib.parse import urlparse


# Foreign schema files, keyed by canonical path; a None slot marks a load in progress.
SCHEMA_CACHE = {}


def get_schema_from_path(path, relative_to, authorized_paths):
    path = os.path.abspath(os.path.join(os.path.dirname(relative_to), path))
    roots = [os.path.abspath(a) for a in authorized_paths]
    if not any(path == root or path.startswith(root + os.sep) for root in roots):
        raise ValueError(
            f"Cannot resolve reference to unauthorized path (use --authorized-paths to allow it): {path}"
        )
    if path in SCHEMA_CACHE:
        if SCHEMA_CACHE[path] is None:
            raise ValueError("Circular dependency detected in JSON schema reference")
    else:
        SCHEMA_CACHE[path] = None  # Reserve the slot first, so a ref back into this file is caught.
        SCHEMA_CACHE[path] = load_schema(path, authorized_paths)
    return SCHEMA_CACHE[path]


# WARNING: reviewing the following algorithm might cause brain damage
# Sorry for that.
def resolve_children(full_schema, part_to_resolve, schema_filepath, authorized_paths):
    if part_to_resolve is None:
        return
    if isinstance(part_to_resolve, (str, int, bool, float)):
        return
    if isinstance(part_to_resolve, list):
        for i, v in enumerate(part_to_resolve):
            part_to_resolve[i] = resolve_ref(full_schema, v, schema_filepath, authorized_paths)
            resolve_children(full_schema, v, schema_filepath, authorized_paths)
        return
    if isinstance(part_to_resolve, dict):
        for k, v in part_to_resolve.items():
            part_to_resolve[k] = resolve_ref(full_schema, v, schema_filepath, authorized_paths)
            resolve_children(full_schema, v, schema_filepath, authorized_paths)
        return
    raise ValueError(f"Value {part_to_resolve} is not supported by the schema loader")


def resolve_ref(full_schema, part_to_resolve, schema_filepath, authorized_paths):
    if not isinstance(part_to_resolve, dict) or "$ref" not in part_to_resolve:
        return part_to_resolve
    if len(part_to_resolve) > 1:
        raise ValueError("Reference nodes should not contain other fields")

    ref_uri = urlparse(part_to_resolve["$ref"])
    if ref_uri.scheme not in ("", "file"):
        raise ValueError(f"Unsupported reference scheme: {ref_uri.scheme}")
    if ref_uri.netloc != "" or ref_uri.params != "" or ref_uri.query != "":
        raise ValueError(f'Unsupported reference: {part_to_resolve["$ref"]}')
    if not ref_uri.fragment.startswith("/"):
        raise ValueError("Only path-like references are supported. (Id-based references are not)")

    # A path (or an explicit file: scheme) points at another schema file; a bare fragment stays in this one.
    if ref_uri.scheme == "file" or ref_uri.path != "":
        full_schema = get_schema_from_path(ref_uri.path, schema_filepath, authorized_paths)

    ref_str = ref_uri.fragment[1:] + '/'
    replacement = full_schema
    while ref_str:
        part, ref_str = ref_str.split('/', 1)
        replacement = replacement[part]
    return replacement
# WARNING OVER


def all_of_merge_single_pair(element1, element2, key):
    if type(element1) is not type(element2):
        raise TypeError(
            f"Field types are different in allOf declaration: '{element1}' vs. '{element2}'"
        )
    if isinstance(element1, dict):
        return all_of_merge_dict(element1, element2)
    if isinstance(element1, list):
        return element1 + [item for item in element2 if item not in element1]
    if element1 == element2:
        return element1
    # allOf means both bounds apply, so keep the stricter one.
    if key in ("minimum", "exclusiveMinimum", "minLength", "minItems"):
        return max(element1, element2)
    if key in ("maximum", "exclusiveMaximum", "maxLength", "maxItems"):
        return min(element1, element2)
    raise ValueError(
        f"Could not merge fields for allOf declaration: '{element1}' and '{element2}'"
    )


def all_of_merge_dict(schema1, schema2):
    result = schema1.copy()
    for key, value in schema2.items():
        if key in result:
            result[key] = all_of_merge_single_pair(result[key], value, key)
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


def load_schema(schema_filepath, authorized_paths):
    with open(schema_filepath, encoding="utf-8") as schema_file:
        schema = json.load(schema_file, object_pairs_hook=OrderedDict)
    resolve_children(schema, schema, schema_filepath, authorized_paths)
    schema = resolve_all_of(schema)
    return schema
