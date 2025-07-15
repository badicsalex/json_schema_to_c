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
from dataclasses import dataclass
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


@dataclass
class CodeSection:
    content: str
    name: str | None

    def is_blank(self) -> bool:
        return bool(re.match(r'^\s*$', self.content))


class CodeUsageResolver:
    required_sections: set[str] = set()
    sections_dependencies: dict[str, set[str]] = {}
    resolved = False

    def add_required_section(self, section_name: str):
        self.required_sections.add(section_name)
        self.resolved = False

    def add_section_dependencies(self, dependent_name: str, dependencies_name: set[str]):
        if dependent_name not in self.sections_dependencies:
            self.sections_dependencies[dependent_name] = set()
        self.sections_dependencies[dependent_name] = self.sections_dependencies[dependent_name].union(dependencies_name)
        self.resolved = False

    def is_section_required(self, section_name: str | None) -> bool:
        if section_name is None:
            return True
        if not self.resolved:
            self.__resolve()
        return section_name in self.required_sections

    def __resolve(self):
        while True:
            initial_len = len(self.required_sections)
            self.__resolve_once()
            new_len = len(self.required_sections)
            if new_len == initial_len:
                break
        self.resolved = True

    def __resolve_once(self):
        resolved: set[str] = set()
        for required_section in self.required_sections:
            resolved = resolved.union(self.sections_dependencies.get(required_section, set()))
        self.required_sections = self.required_sections.union(resolved)


class CodeBlockPrinter:
    def __init__(self, filepath: str, code_usage_resolver: CodeUsageResolver):
        self.filepath = filepath
        self.indent_level = 0
        self.last_was_else = False
        self.text = ""
        self.code_usage_resolver = code_usage_resolver

    def save_to_file(self):
        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write(self.__into_pruned_text())

    def require_section(self, section_name: str):
        self.code_usage_resolver.add_required_section(section_name)

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

    def __into_pruned_text(self) -> str:
        pruned_text = ""
        skip_if_blank = False

        for section in self.__into_code_sections():
            if not self.code_usage_resolver.is_section_required(section.name):
                skip_if_blank = True # skip unused section and the following blank
                continue
            if skip_if_blank:
                skip_if_blank = False
                if section.is_blank():
                    continue
            pruned_text += section.content

        return pruned_text

    def __into_code_sections(self) -> list[CodeSection]:
        sections: list[CodeSection] = []

        in_named_section = False
        section_name = ""
        section_needs: set[str] = set()
        section_text = ""

        for txt_chunk in re.split(r'^[ \t]*(//[ \t]*js2c-(?:start|end)(?:[ \t][^\n]*?)?)[ \t]*$\n?', self.text, flags=re.MULTILINE):
            if in_named_section:
                if re.match(r'^//\s*js2c-end', txt_chunk):
                    in_named_section = False
                    sections.append(CodeSection(content=section_text, name=section_name))
                    self.code_usage_resolver.add_section_dependencies(section_name, section_needs)
                else:
                    section_text += txt_chunk
            else:
                if m := re.match(r'^//\s*js2c-start\s+(\S+)(?:\s+\(\s*needs\s*:\s*([^ \t,]+(?:\s*,\s*[^ \t,]+)*)\s*\))?$', txt_chunk):
                    in_named_section = True
                    section_name = m.group(1)
                    section_needs = set(re.split(r'\s*,\s*', m.group(2))) if m.group(2) else set()
                    section_text = ""
                else:
                    sections.append(CodeSection(content=txt_chunk, name=None))

        return sections
