#!/usr/bin/env python3
import json
import argparse

INDENT = '    '

def parse_args():
    parser = argparse.ArgumentParser(description="Create a JSON parser in C based on a json schema")
    parser.add_argument("schema_file", type=argparse.FileType('r'))
    parser.add_argument("c_file", type=argparse.FileType('w'))
    parser.add_argument("h_file", type=argparse.FileType('w'))
    return parser.parse_args()

class StringGenerator:
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file, indent):
        if "maxLength" not in schema:
            raise ValueError("Strings must have maxLength")
        out_file.write(indent)
        out_file.write("char {}[{}];\n".format(name, schema["maxLength"] + 1))

class NumberGenerator:
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file, indent):
        out_file.write(indent)
        out_file.write("int64_t {};\n".format(name))

class BoolGenerator:
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file, indent):
        out_file.write(indent)
        out_file.write("bool {};\n".format(name))

class ObjectGenerator:
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file, indent):
        if "additionalProperties" not in schema or schema["additionalProperties"] != False:
            raise ValueError("Object types must have additionalProperties set to false")
        out_file.write(indent)
        out_file.write("struct {\n")
        for prop_name, prop_schema in schema["properties"].items():
            generate_type_declaration(prop_schema, prop_name, out_file, indent + INDENT)
        out_file.write(indent)
        out_file.write("}} {};\n".format(name))

class ArrayGenerator:
    @classmethod
    def generate_type_declaration(cls, schema, name, out_file, indent):
        if "maxItems" not in schema:
            raise ValueError("Arrays must have maxItems")
        out_file.write(indent)
        out_file.write("struct {\n")
        out_file.write(indent + INDENT)
        out_file.write("uint64_t n;\n")
        generate_type_declaration(schema["items"], "items[{}]".format(schema["maxItems"]), out_file, indent + INDENT)
        out_file.write(indent)
        out_file.write("}} {};\n".format(name))


generators = {
    "string": StringGenerator,
    "integer": NumberGenerator,
    "boolean": BoolGenerator,
    "object": ObjectGenerator,
    "array": ArrayGenerator,
}

def generate_type_declaration(schema, name, out_file, indent = ''):
    generators[schema["type"]].generate_type_declaration(schema, name, out_file, indent)


def main(args):
    schema = json.load(args.schema_file)
    args.h_file.write("#include <stdint.h>\n")
    args.h_file.write("#include <stdbool.h>\n\n")
    args.h_file.write("typedef ")
    generate_type_declaration(schema, "root", args.h_file)

if __name__ == "__main__":
    main(parse_args())
