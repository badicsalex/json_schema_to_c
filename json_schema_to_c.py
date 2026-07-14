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
import os
import sys

from js2c.schema import load_schema
from js2c.codegen.base import SchemaError
from js2c.codegen.root import RootGenerator
from js2c.settings import Settings

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
    parser.add_argument(
        "c_file",
        type=str,
        help="Filename of the generated parser .c file",
    )
    parser.add_argument(
        "h_file",
        type=str,
        help="Filename of the generated parser .h file",
    )
    parser.add_argument(
        "--authorized-paths",
        type=str,
        nargs="+",
        metavar="path",
        default=None,
        help="Files or directories that a schema is allowed to reference across files. "
             "The directory of the schema itself is always allowed.",
    )
    Settings.fill_argparse(parser)
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    # Kept out of js2cSettings on purpose: an untrusted schema must not be able to widen its own allowlist.
    authorized_paths = list(args.authorized_paths or [])
    authorized_paths.append(os.path.dirname(os.path.abspath(args.schema_file)))
    try:
        schema = load_schema(args.schema_file, authorized_paths)
    except (ValueError, OSError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    settings = Settings(vars(args), schema.get('js2cSettings', {}))
    try:
        root_generator = RootGenerator(schema, settings)
        h_file = root_generator.generate_parser_h(args.h_file)
        c_file = root_generator.generate_parser_c(args.c_file, os.path.basename(args.h_file))
    except SchemaError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    # Only touch the output files once both generated cleanly, so a failure leaves them untouched.
    h_file.save_to_file()
    c_file.save_to_file()


if __name__ == "__main__":
    main(parse_args())
