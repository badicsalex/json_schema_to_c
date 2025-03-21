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

import argparse
import json
import os
import sys

from js2c.schema import load_schema
from js2c.codegen.base import SchemaError
from js2c.codegen.root import RootGenerator
from js2c.settings import Settings, PRINT_RESOLVED_SCHEMA_FLAG

HELP = """
Create a JSON parser in C based on a json schema
""".strip()

HELP_EPILOG = """
You can specify arguments in the schema too, under the js2cSettings" key,
in either snake or camel case. E.g.:
"js2cSettings": {"cPrefixFile": "my.inc"}

The settings in the schema take precedence.
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=HELP,
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "schema_file",
        type=str,
        help="Filename of the JSON schema to use. Schema version 7 is supported.",
    )
    Settings.fill_argparse(parser)
    parser.add_argument(
        PRINT_RESOLVED_SCHEMA_FLAG,
        action="store_true",
        help="Prints JSON schema with all `refs` and `allOf` resolved.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace):
    schema = load_schema(args.schema_file)
    settings = Settings(vars(args), schema.get('js2cSettings', {}))

    if args.print_resolved_schema:
        print(json.dumps(schema, indent=4))

    if settings.h_file is None and settings.c_file is None:
        return

    try:
        root_generator = RootGenerator(schema, settings)
        if settings.h_file is not None: root_generator.generate_parser_h(settings.h_file)
        if settings.c_file is not None: root_generator.generate_parser_c(settings.c_file, os.path.basename(args.h_file))
    except SchemaError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(parse_args())
