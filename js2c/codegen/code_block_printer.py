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


class CodeBlockContextManager:
    def __init__(self, printer, indent_level, indent_only=False):
        self.printer = printer
        self.indent_level = indent_level
        self.indent_only = indent_only

    def __enter__(self):
        if not self.indent_only:
            self.printer.print("{")
        self.printer.indent_level += self.indent_level
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.printer.indent_level -= self.indent_level
        if not self.indent_only:
            self.printer.print("}")


class CodeBlockPrinter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.indent_level = 0
        self.last_was_else = False
        self.text = ""

    def save_to_file(self):
        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write(self.text)

    def print(self, line):
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
        self.last_was_else = line == "else"

    def print_with_docstring(self, line, docstring):
        if not docstring:
            self.print(line)
        else:
            self.print(line.ljust(40) + "/**< {} */".format(docstring))

    def print_separator(self, separator_str):
        pad_length = (70 - len(separator_str))//2
        self.print("/* {p} {s} {p} */".format(p="=" * pad_length, s=separator_str))

    def write(self, data):
        """ Write raw data to the file """
        self.text += "\n"
        self.text += data

    def code_block(self, indent_level=4, standalone=False):
        if standalone:
            self.text += "\n{}".format(" "*self.indent_level)
            # XXX: this is to prevent padding the opening brace that comes next
            self.last_was_else = True
        return CodeBlockContextManager(self, indent_level)

    def if_block(self, condition, indent_level=4, standalone=False):
        self.print("if ({})".format(condition))
        return self.code_block(indent_level, standalone)

    def for_block(self, for_stuff, indent_level=4, standalone=False):
        self.print("for ({})".format(for_stuff))
        return self.code_block(indent_level, standalone)

    def indent(self, indent_level=4):
        return CodeBlockContextManager(self, indent_level, indent_only=True)
