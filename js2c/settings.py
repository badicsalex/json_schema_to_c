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
import argparse, sys
from dataclasses import dataclass
from typing_extensions import TextIO, TypeVar

T = TypeVar('T')
PRINT_RESOLVED_SCHEMA_FLAG = "--print-resolved-schema"
TOKENS_BUF_MAX_SIZE_DEFAULT = "1024*1024"

@dataclass
class SettingsField:
    name: str
    type: T
    help: str
    metavar: str
    required: bool
    default: str | None


def snake_to_camel_case(text: str) -> str:
    text = text.replace("_", " ").title().replace(" ", "")
    return text[0].lower() + text[1:]


class Settings:
    # pylint: disable=too-few-public-methods
    FIELDS = [
        SettingsField(
            "h_file",
            type=str,
            help="Filename of the generated parser .h file",
            metavar="file",
            required=PRINT_RESOLVED_SCHEMA_FLAG not in sys.argv,
            default=None,
        ),
        SettingsField(
            "c_file",
            type=str,
            help="Filename of the generated parser .c file",
            metavar="file",
            required=PRINT_RESOLVED_SCHEMA_FLAG not in sys.argv,
            default=None,
        ),
        SettingsField(
            "h_prefix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right after the header guard and includes in the generated header.",
            metavar="file",
            required=False,
            default=None,
        ),
        SettingsField(
            "h_postfix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right before header guard's #endif in the generated header.",
            metavar="file",
            required=False,
            default=None,
        ),
        SettingsField(
            "c_prefix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right after the includes, before the JSMN code in the generated C file.",
            metavar="file",
            required=False,
            default=None,
        ),
        SettingsField(
            "c_postfix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed at the end of the generated C file.",
            metavar="file",
            required=False,
            default=None,
        ),
        SettingsField(
            "allow_additional_properties",
            type=int,
            help="Allow additionalProperties to be true (default for objects), and leave a $token_num amount of space for these \n"
            "additional properties during the tokenizing step. (One token is basically one element, e.g. a string literal or a number)",
            metavar="tokens",
            required=False,
            default=None,
        ),
        SettingsField(
            "include_external_builtins_file",
            type=str,
            help="Instead of manually including the builtin functions to the generated parser, only an include statement \n"
            "with this path will be generated. Be sure to copy js2c_builtins.h there.",
            metavar="file",
            required=False,
            default=None,
        ),
        SettingsField(
            "file_parser_max_size",
            type=str,
            help="Max input file size allowed (as a C expression). Only relevant in the function that parse JSON from a file path.",
            metavar="expression",
            required=False,
            default=None,
        ),
        SettingsField(
            "tokens_buf_max_size",
            type=str,
            help=f"Maximum memory size limit allowed (as a C expression) when allocating the JSMN token buffer. Default is {TOKENS_BUF_MAX_SIZE_DEFAULT}.",
            metavar="expression",
            required=False,
            default=TOKENS_BUF_MAX_SIZE_DEFAULT,
        ),
    ]

    h_file: str | None
    h_prefix_file: TextIO | None
    h_postfix_file: TextIO | None
    c_file: str | None
    c_prefix_file: TextIO | None
    c_postfix_file: TextIO | None
    allow_additional_properties: str | None
    include_external_builtins_file: str | None
    file_parser_max_size: int | None
    tokens_buf_max_size: int | None

    def __init__(self, args, settings_json):
        for field in self.FIELDS:
            field_name_in_camel = snake_to_camel_case(field.name)
            if field.name in settings_json:
                self.parse_field(field, settings_json[field.name])
            elif field_name_in_camel in settings_json:
                self.parse_field(field, settings_json[field_name_in_camel])
            elif args.get(field.name, None) is not None:
                setattr(self, field.name, args[field.name])
            else:
                setattr(self, field.name, None)

    def parse_field(self, field_desc: SettingsField, field_data):
        setattr(self, field_desc.name, field_desc.type(field_data))

    @classmethod
    def fill_argparse(cls, parser: argparse.ArgumentParser):
        for field in cls.FIELDS:
            parser.add_argument(
                "--" + field.name.replace('_', '-'),
                metavar=field.metavar,
                type=field.type,
                help=field.help,
                required=field.required,
                default=field.default,
            )
