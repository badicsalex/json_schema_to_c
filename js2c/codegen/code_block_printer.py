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
from __future__ import annotations

import io
import re


class CodeBlockContextManager:
    def __init__(self, printer: CodeBlockPrinter, indent_level: int, indent_only=False, suffix=""):
        self.printer = printer
        self.indent_level = indent_level
        self.indent_only = indent_only
        self.suffix = suffix

    def __enter__(self):
        if not self.indent_only:
            self.printer.print("{")
        self.printer.indent_level += self.indent_level
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.printer.indent_level -= self.indent_level
        if self.indent_only:
            if self.suffix != "":
                self.printer.print(self.suffix)
        else:
            if self.suffix == "":
                self.printer.print("}")
            else:
                self.printer.print("} " + self.suffix)


class CodeBlockPrinter:
    def __init__(self, filepath: str, required_sections_storage: set[str]):
        self.filepath = filepath
        self.indent_level = 0
        self.last_was_else = False
        self.text = ""
        self.required_sections = required_sections_storage

    def save_to_file(self):
        with open(self.filepath, "w") as file:
            file.write(self.get_stripped_text())

    def require_section(self, section_name: str):
        self.required_sections.add(section_name)

        # handle inter-dependencies
        if section_name in ("builtin_check_current_string", "builtin_parse_bool", "builtin_parse_double"):
            self.require_section("check_type")
        if section_name == "builtin_parse_string":
            self.require_section("builtin_check_current_string")

    # returns self.text stripped of non-required sections
    def get_stripped_text(self) -> str:
        res = ""
        in_section = False
        skip_section = False
        cleanup_blank = False
        for line in io.StringIO(self.text):
            if in_section:
                if re.match(r'^\s*//\s*js2c-end\s*$', line):
                    in_section = False
                    cleanup_blank = skip_section
                    continue
                elif skip_section:
                    continue
            elif m := re.match(r'^\s*//\s*js2c-start\s+(\S.*?)\s*$', line):
                tags = set(re.split(r'\s+', m.group(1)))
                in_section = True
                skip_section = self.required_sections & tags == set()
                continue
            elif cleanup_blank:
                cleanup_blank = False
                if re.match(r'^\s*$', line):
                    continue
            res += line
        return res

    def print(self, lines: str | list[str]):
        if isinstance(lines, str):
            self.print_line(lines)
        else:
            for line in lines:
                self.print_line(line)

    def print_line(self, line: str):
        """ Print an indented line """
        if line == "else":
            self.text += " else "
        elif line == "{":
            if self.last_was_else:
                self.text += "{"
            else:
                self.text += " {"
        elif not line:
            self.text += "\n"
        elif self.last_was_else:
            self.text += line
        else:
            self.text += "\n{}{}".format(" "*self.indent_level, line)
        self.last_was_else = (line == "else")

    def print_with_docstring(self, line: str, docstring: str):
        if not docstring:
            self.print(line)
        else:
            self.print(line.ljust(40) + "/**< {} */".format(docstring))

    def print_separator(self, separator_str: str):
        pad_length = (70 - len(separator_str))//2
        self.print("/* {p} {s} {p} */".format(p="=" * pad_length, s=separator_str))

    def write(self, data: str):
        """ Write raw data to the file """
        self.text += "\n"
        self.text += data

    def code_block(self, indent_level=4, standalone=False, suffix="") -> CodeBlockContextManager:
        if standalone:
            self.text += "\n{}".format(" "*self.indent_level)
            # XXX: this is to prevent padding the opening brace that comes next
            self.last_was_else = True
        return CodeBlockContextManager(self, indent_level, suffix=suffix)

    def if_block(self, condition: str, indent_level=4, standalone=False, always_true=False) -> CodeBlockContextManager:
        if always_true:  # no need to have an "if" block, if the condition always true
            return CodeBlockContextManager(self, 0, indent_only=True)
        self.print("if ({})".format(condition))
        return self.code_block(indent_level, standalone)

    def for_block(self, for_stuff: str, indent_level=4, standalone=False) -> CodeBlockContextManager:
        self.print("for ({})".format(for_stuff))
        return self.code_block(indent_level, standalone)

    def do_while_block(self, while_stuff: str, indent_level=4, standalone=False) -> CodeBlockContextManager:
        self.print("do")
        return self.code_block(indent_level, standalone, suffix="while ({});".format(while_stuff))

    def indent(self, indent_level=4) -> CodeBlockContextManager:
        return CodeBlockContextManager(self, indent_level, indent_only=True)
