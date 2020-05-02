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

import os
import sys
import subprocess
import traceback
import tempfile
import difflib

DIR_OF_THIS_FILE = os.path.dirname(__file__)
JSMN_DIR = os.path.join(DIR_OF_THIS_FILE, '..', 'jsmn')
CC = [
    'gcc',
    '-Wall',
    '-Werror',
    '-I', '.',
    '-I', JSMN_DIR,
    '-I', os.path.join(DIR_OF_THIS_FILE, '..'),  # for json_schema_to_c.h
]

JSON_SCHEMA_TO_C = [
    os.path.join(DIR_OF_THIS_FILE, '..', 'json_schema_to_c.py')
]


def get_all_tests():
    (_, dirnames, _) = next(os.walk(DIR_OF_THIS_FILE))
    if '__pycache__' in dirnames:
        dirnames.remove('__pycache__')
    return dirnames


def run_test(test_name, tmpdir):
    test_dir = os.path.join(DIR_OF_THIS_FILE, test_name)
    schema_file_name = os.path.join(test_dir, 'schema.json')
    test_c_file_name = os.path.join(test_dir, 'test.c')
    with open(os.path.join(test_dir, 'output.txt')) as output_file:
        output = output_file.read()

    subprocess.run(
        JSON_SCHEMA_TO_C + [schema_file_name, 'parser.c', 'parser.h'],
        check=True,
        cwd=tmpdir,
    )
    subprocess.run(
        CC + [test_c_file_name, 'parser.c', '-o', 'test'],
        check=True,
        cwd=tmpdir,
    )

    result = subprocess.run(
        [os.path.join(tmpdir, 'test')],
        check=True,
        stdout=subprocess.PIPE,
        encoding='utf-8',
    )
    if result.stdout != output:
        err_str = "Wrong output (- is expected, + is actual):\n"
        diff = "".join(
            difflib.ndiff(
                result.stdout.splitlines(keepends=True),
                output.splitlines(keepends=True),
            )
        )
        assert result.stdout == output, err_str + diff


def run_test_set(tests):
    tests_successful = 0
    for test in sorted(tests):
        try:
            print("== Running {} ==".format(test))
            with tempfile.TemporaryDirectory() as tmpdir:
                run_test(test, tmpdir)
            print("OK.")
            tests_successful = tests_successful + 1
        except Exception:
            traceback.print_exc()

    print('-' * 25)
    print("{}/{} tests successful.".format(tests_successful, len(tests)))
    return tests_successful == len(tests)
