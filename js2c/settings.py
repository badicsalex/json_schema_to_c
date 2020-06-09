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
from collections import namedtuple
import argparse

SettingsField = namedtuple("SettingsField", ["name", "type", "help", "default", "metavar"])


class Settings:
    # pylint: disable=too-few-public-methods
    FIELDS = [
        SettingsField(
            "h_prefix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right after the header guard and includes in the generated header.",
            default=None,
            metavar="file",
        ),
        SettingsField(
            "h_postfix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right before header guard's #endif in the generated header.",
            default=None,
            metavar="file",
        ),
        SettingsField(
            "c_prefix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed right after the includes, before the JSMN code in the generated C file.",
            default=None,
            metavar="file",
        ),
        SettingsField(
            "c_postfix_file",
            type=argparse.FileType('r'),
            help="Contents of this file will be placed at the end of the generated C file.",
            default=None,
            metavar="file",
        ),
        SettingsField(
            "allow_additional_properties",
            type=int,
            help="Allow additionalProperties to be true (default for objects), and leave a $token_num amount of space for these "
            "additional properties during the tokenizing step. (One token is basically one element, e.g. a string literal or a number)",
            default=None,
            metavar="tokens",
        ),
    ]

    def __init__(self, args):
        for k, v in args.items():
            setattr(self, k, v)

    @classmethod
    def fill_argparse(cls, parser):
        for field in cls.FIELDS:
            parser.add_argument(
                "--" + field.name.replace('_', '-'),
                metavar=field.metavar,
                type=field.type,
                help=field.help,
                default=field.default,
            )
