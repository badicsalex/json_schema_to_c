#!/usr/bin/env python3
import json
import argparse
from abc import ABC, abstractmethod
from collections import namedtuple


def parse_args():
    parser = argparse.ArgumentParser(description="Create a JSON parser in C based on a json schema")
    parser.add_argument("schema_file", type=argparse.FileType('r'))
    parser.add_argument("c_file", type=argparse.FileType('w'))
    parser.add_argument("h_file", type=argparse.FileType('w'))
    return parser.parse_args()


class Generator(ABC):
    @classmethod
    @abstractmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        pass

    @classmethod
    @abstractmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        pass

    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        pass

    @classmethod
    def generate_parser_bodies(cls, schema, name, out_file):
        pass


class StringGenerator(Generator):
    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        if "maxLength" not in schema:
            raise ValueError("Strings must have maxLength")
        out_file.write("    char {}[{}];\n".format(field_name, schema["maxLength"] + 1))

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        if "maxLength" not in schema:
            raise ValueError("Strings must have maxLength")
        out_file.write(
            "error = error || builtin_parse_string(parse_state, {}[0], {});\n"
            .format(out_var_name, schema["maxLength"])
        )


class NumberGenerator(Generator):
    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        out_file.write("    int64_t {};\n".format(field_name))

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        out_file.write(
            "error = error || builtin_parse_number(parse_state, {});\n"
            .format(out_var_name)
        )


class BoolGenerator(Generator):
    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        out_file.write("    bool {};\n".format(field_name))

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        out_file.write(
            "error = error || builtin_parse_bool(parse_state, {});\n"
            .format(out_var_name)
        )


class ObjectGenerator(Generator):
    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        out_file.write("    {}_t {};\n".format(name, field_name))

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        out_file.write(
            "error = error || parse_{}(parse_state, {});\n"
            .format(name, out_var_name)
        )

    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        if "additionalProperties" not in schema or schema["additionalProperties"] != False:
            raise ValueError(
                "Object types must have additionalProperties set to false")
        for prop_name, prop_schema in schema["properties"].items():
            GlobalGenerator.generate_type_declaration(prop_schema, "{}_{}".format(name, prop_name), out_file)

        out_file.write("typedef struct {}_s ".format(name) + "{\n")
        for prop_name, prop_schema in schema["properties"].items():
            GlobalGenerator.generate_field_declaration(
                prop_schema,
                "{}_{}".format(name, prop_name),
                prop_name,
                out_file
            )
        out_file.write("}} {}_t;\n\n".format(name))

    @classmethod
    def generate_parser_bodies(cls, schema, name, out_file):
        for prop_name, prop_schema in schema["properties"].items():
            GlobalGenerator.generate_parser_bodies(prop_schema, "{}_{}".format(name, prop_name), out_file)
        out_file.write("static bool parse_{name}(parse_state_t* parse_state, {name}_t* out)".format(name=name))
        out_file.write("{\n")
        out_file.write("    bool error=check_type(parse_state, JSMN_OBJECT);\n")
        out_file.write("    uint64_t i;\n")
        out_file.write("    const uint64_t n = parse_state->tokens[parse_state->current_token].size;\n")
        out_file.write("    parse_state->current_token += 1;\n")
        out_file.write("    for (i = 0; !error && i < n; ++ i) {\n")
        out_file.write("        ")

        for prop_name, prop_schema in schema["properties"].items():
            out_file.write('if (current_string_is(parse_state, "{}"))'.format(prop_name))
            out_file.write("{\n")
            out_file.write("            parse_state->current_token += 1;\n")
            out_file.write("            ")
            GlobalGenerator.generate_parser_call(
                prop_schema,
                "{}_{}".format(name, prop_name),
                "&out->{}".format(prop_name),
                out_file
            )
            out_file.write("        } else ")
        out_file.write("{\n")
        out_file.write("            /* TODO ERRORLOG */ \n")
        out_file.write("            error=true; \n")
        out_file.write("        }\n")
        out_file.write("    }\n")
        out_file.write("    return error;\n")
        out_file.write("}\n\n")


class ArrayGenerator(Generator):
    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        out_file.write("    {}_t {};\n".format(name, field_name))

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        out_file.write(
            "error = error || parse_{}(parse_state, {});\n"
            .format(name, out_var_name)
        )

    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        if "maxItems" not in schema:
            raise ValueError("Arrays must have maxItems")
        GlobalGenerator.generate_type_declaration(schema["items"], "{}_item".format(name), out_file)

        out_file.write("typedef struct {}_s ".format(name) + "{\n")
        out_file.write("    uint64_t n;\n")
        GlobalGenerator.generate_field_declaration(
            schema["items"],
            "{}_item".format(name),
            "items[{}]".format(schema["maxItems"]), out_file
        )
        out_file.write("}} {}_t;\n\n".format(name))

    @classmethod
    def generate_parser_bodies(cls, schema, name, out_file):
        GlobalGenerator.generate_parser_bodies(schema["items"], "{}_item".format(name), out_file)
        out_file.write("static bool parse_{name}(parse_state_t* parse_state, {name}_t* out)".format(name=name))
        out_file.write("{\n")
        out_file.write("    bool error=check_type(parse_state, JSMN_ARRAY);\n")
        out_file.write("    uint64_t i;\n")
        out_file.write("    const uint64_t n = parse_state->tokens[parse_state->current_token].size;\n")
        out_file.write("    out->n = n;\n")
        out_file.write("    parse_state->current_token += 1;\n")
        out_file.write("    for (i = 0; !error && i < n; ++ i) {\n")
        out_file.write("        ")
        GlobalGenerator.generate_parser_call(
            schema["items"],
            "{}_item".format(name),
            "&out->items[i]",
            out_file
        )
        out_file.write("    }\n")
        out_file.write("    return error;\n")
        out_file.write("}\n\n")


class GlobalGenerator(Generator):
    OTHER_GENERATORS = {
        "string": StringGenerator,
        "integer": NumberGenerator,
        "boolean": BoolGenerator,
        "object": ObjectGenerator,
        "array": ArrayGenerator,
    }

    @classmethod
    def generate_field_declaration(cls, schema, name, field_name, out_file):
        cls.OTHER_GENERATORS[schema["type"]]\
            .generate_field_declaration(schema, name, field_name, out_file)

    @classmethod
    def generate_parser_call(cls, schema, name, out_var_name, out_file):
        cls.OTHER_GENERATORS[schema["type"]]\
            .generate_parser_call(schema, name, out_var_name, out_file)

    @classmethod
    def generate_type_declaration(cls, schema, name, out_file):
        cls.OTHER_GENERATORS[schema["type"]]\
            .generate_type_declaration(schema, name, out_file)

    @classmethod
    def generate_parser_bodies(cls, schema, name, out_file):
        cls.OTHER_GENERATORS[schema["type"]]\
            .generate_parser_bodies(schema, name, out_file)


def generate_root_parser(schema, out_file):
    out_file.write("bool parse(char* json_string, root_t* out){\n")
    out_file.write("    bool error = false;\n")
    out_file.write("    parse_state_t parse_state_var;\n")
    out_file.write("    parse_state_t* parse_state = &parse_state_var;\n")
    out_file.write("    error = error || builtin_parse_json_string(parse_state, json_string);\n")
    out_file.write("    ")
    GlobalGenerator.generate_parser_call(
        schema,
        "root",
        "out",
        out_file,
    )
    out_file.write("    return error;\n")
    out_file.write("}\n")


def main(args):
    schema = json.load(args.schema_file)
    args.h_file.write("#include <stdint.h>\n")
    args.h_file.write("#include <stdbool.h>\n\n")
    GlobalGenerator.generate_type_declaration(schema, "root", args.h_file)
    args.h_file.write("bool parse(char* json_string, root_t* out);")

    args.c_file.write('#include "{}"\n'.format(args.h_file.name))
    args.c_file.write('#include "json_schema_to_c.h"\n\n')

    GlobalGenerator.generate_parser_bodies(schema, "root", args.c_file)
    generate_root_parser(schema, args.c_file)


if __name__ == "__main__":
    main(parse_args())
