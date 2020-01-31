#!/usr/bin/env python3
import json
import argparse
from abc import ABC, abstractmethod
from collections import namedtuple


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a JSON parser in C based on a json schema")
    parser.add_argument("schema_file", type=argparse.FileType('r'))
    parser.add_argument("c_file", type=argparse.FileType('w'))
    parser.add_argument("h_file", type=argparse.FileType('w'))
    return parser.parse_args()


class Generator(ABC):
    @classmethod
    @abstractmethod
    def generate_type_declaration(cls, schema, name, out_file):
        pass


class StringGenerator(Generator):
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        if "maxLength" not in schema:
            raise ValueError("Strings must have maxLength")
        out_file.write("typedef char {}_t[{}];\n\n".format(
            name, schema["maxLength"] + 1))


class NumberGenerator(Generator):
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        out_file.write("typedef int64_t {}_t;\n\n".format(name))


class BoolGenerator(Generator):
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        out_file.write("typedef bool {}_t;\n\n".format(name))


class ObjectGenerator(Generator):
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        if "additionalProperties" not in schema or schema["additionalProperties"] != False:
            raise ValueError(
                "Object types must have additionalProperties set to false")
        for prop_name, prop_schema in schema["properties"].items():
            generate_type_declaration(
                prop_schema, "{}_{}".format(name, prop_name), out_file)

        out_file.write("typedef struct {}_s ".format(name) + "{\n")
        for prop_name in schema["properties"]:
            out_file.write("    {n}_{p}_t {p};\n".format(n=name, p=prop_name))
        out_file.write("}} {}_t;\n\n".format(name))


class ArrayGenerator(Generator):
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        if "maxItems" not in schema:
            raise ValueError("Arrays must have maxItems")
        generate_type_declaration(
            schema["items"], "{}_item".format(name), out_file)

        out_file.write("typedef struct {}_s ".format(name) + "{\n")
        out_file.write("    uint64_t n;\n")
        out_file.write("    {}_item_t items[{}];\n".format(
            name, schema["maxItems"]))
        out_file.write("}} {}_t;\n\n".format(name))


generators = {
    "string": StringGenerator,
    "integer": NumberGenerator,
    "boolean": BoolGenerator,
    "object": ObjectGenerator,
    "array": ArrayGenerator,
}


def generate_type_declaration(schema, name, out_file=''):
    generators[schema["type"]].generate_type_declaration(
        schema, name, out_file)


def main(args):
    schema = json.load(args.schema_file)
    args.h_file.write("#include <stdint.h>\n")
    args.h_file.write("#include <stdbool.h>\n\n")
    generate_type_declaration(schema, "root", args.h_file)


if __name__ == "__main__":
    main(parse_args())
