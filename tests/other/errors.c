#include "errors.parser.h"

#include <string.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "true ",
        "Unexpected token in 'document root': PRIMITIVE instead of OBJECT",
        0
    );
    check_error(
        "[]",
        "Unexpected token in 'document root': ARRAY instead of OBJECT",
        0
    );
    check_error(
        "{",
        "JSON syntax error: End-of-file reached (JSON file incomplete)",
        1
    );
    char many_objects[20001] = {};
    memset(many_objects, '[', 10000);
    memset(many_objects + 10000, ']', 10000);
    check_error(
        many_objects,
        "JSON syntax error: JSON file too complex",
        -1 /* don't care about the actual position of the failure here */
    );

    check_error(
        "{\"name\": true}",
        "Unexpected token in 'name': PRIMITIVE instead of STRING",
        9
    );
    check_error(
        "{\"name\": \"n>8 here.\"}",
        "String too large in 'name'. Length: 9. Maximum length: 8.",
        10
    );
    check_error(
        "{\"name\": \" <4\"}",
        "String too short in 'name'. Length: 3. Minimum length: 4.",
        10
    );

    check_error(
        "{\"is_good\": 1}",
        "Invalid boolean literal in 'is_good': 1",
        12
    );
    check_error(
        "{\"is_good\": \"true\"}",
        "Unexpected token in 'is_good': STRING instead of PRIMITIVE",
        13
    );

    check_error(
        "{\"num\": true}",
        "Invalid signed integer literal in 'num': true",
        8
    );
    check_error(
        "{\"num\": 100e}",
        "Invalid signed integer literal in 'num': 100e",
        8
    );
    check_error(
        "{\"num\": 0x100}",
        "Invalid signed integer literal in 'num': 0x100",
        8
    );
    check_error(
        "{\"num\": \"1234\"}",
        "Unexpected token in 'num': STRING",
        9
    );
    check_error(
        "{\"unsigned_num\": true}",
        "Invalid unsigned integer literal in 'unsigned_num': true",
        17
    );
    check_error(
        "{\"unsigned_num\": 100e}",
        "Invalid unsigned integer literal in 'unsigned_num': 100e",
        17
    );
    check_error(
        "{\"unsigned_num\": 0x100}",
        "Invalid unsigned integer literal in 'unsigned_num': 0x100",
        17
    );
    check_error(
        "{\"unsigned_num\": \"1234\"}",
        "Unexpected token in 'unsigned_num': STRING",
        18
    );

    check_error(
        "{\"num2\": 999, \"num\": 5001}",
        "Integer 5001 in 'num' out of range. It must be <= 5000.",
        21
    );
    check_error(
        "{\"num\": 5000, \"num2\": 1000}",
        "Integer 1000 in 'num2' out of range. It must be < 1000.",
        22
    );
    check_error(
        "{\"num2\": -999, \"num\": -5001}",
        "Integer -5001 in 'num' out of range. It must be >= -5000.",
        22
    );
    check_error(
        "{\"num\": -5000, \"num2\": -1000}",
        "Integer -1000 in 'num2' out of range. It must be > -1000.",
        23
    );
    check_error(
        "{\"unsigned_num\": -5000}",
        "Invalid unsigned integer literal in 'unsigned_num': -5000",
        17
    );
    check_error(
        "{\"unsigned_num2\": -5000}",
        "Invalid unsigned integer literal in 'unsigned_num2': -5000",
        18
    );
    check_error(
        "{\"unsigned_num2\": 120}",
        "Integer 120 in 'unsigned_num2' out of range. It must be >= 123.",
        18
    );
    check_error(
        "{\"unsigned_num2\": 1200}",
        "Integer 1200 in 'unsigned_num2' out of range. It must be <= 456.",
        18
    );

    check_error(
        "{\"numeric_string\": 1234}",
        "Unexpected token in 'numeric_string': PRIMITIVE",
        19
    );
    check_error(
        "{\"numeric_string\": -1234}",
        "Unexpected token in 'numeric_string': PRIMITIVE",
        19
    );
    check_error(
        "{\"numeric_string\": \"0x1234\"}",
        "Invalid unsigned integer literal in 'numeric_string': 0x1234",
        20
    );
    check_error(
        "{\"numeric_string\": \"INVALID\"}",
        "Invalid unsigned integer literal in 'numeric_string': INVALID",
        20
    );
    check_error(
        "{\"anyof_hex\": 12}",
        "Integer 12 in 'anyof_hex' out of range. It must be >= 123.",
        14
    );
    check_error(
        "{\"anyof_hex\": \"12\"}",
        "Integer 18 in 'anyof_hex' out of range. It must be >= 123.",
        15
    );

    check_error(
        "{\"the_array\": 1}",
        "Unexpected token in 'the_array': PRIMITIVE instead of ARRAY",
        14
    );
    check_error(
        "{\"the_array\": [1,2,3,4]}",
        "Array 'the_array' too large. Length: 4. Maximum length: 3.",
        14
    );
    check_error(
        "{\"the_array\": [1]}",
        "Array 'the_array' too small. Length: 1. Minimum length: 2.",
        14
    );

    check_error(
        "{}",
        "Missing required field in 'document root': the_array",
        2
    );
    check_error(
        "{\"num\": 1234, \"num\": 1234}",
        "Duplicate field definition in 'document root': num",
        15
    );
    check_error(
        "{\"nonexistent\": true}",
        "Unknown field in 'document root': nonexistent",
        2
    );

    check_error(
        "{\"error_arr\": [{}]}",
        "Error parsing 'error_arr', value=\"INVALID DEFAULT\": error calling error_creating_parser",
        21
    );
    check_error(
        "{\"error_arr\": [{\"trigger\": \"ab\"}]}",
        "Error parsing 'trigger', value=\"ab\": Custom error",
        28
    );
    check_error(
        "{\"error_arr\": [{\"trigger\": \"abc\"}]}",
        "Error parsing 'trigger', value=\"abc\": error calling error_creating_parser",
        28
    );

    check_error(
        "{\"the_enum\": \"x\"}",
        "Unknown enum value in 'the_enum': x",
        14
    );
    check_error(
        "{\"the_enum\": 5}",
        "Unexpected token in 'the_enum': PRIMITIVE instead of STRING",
        13
    );

    check_error(
        "{\"fnum\": true}",
        "Invalid floating point literal in 'fnum': true",
        9
    );
    check_error(
        "{\"fnum\": 100x}",
        "Invalid floating point literal in 'fnum': 100x",
        9
    );
    check_error(
        "{\"fnum\": 0x100}",
        "Invalid floating point literal in 'fnum': 0x100",
        9
    );
    check_error(
        "{\"fnum\": inf}",
        "JSON syntax error: Invalid character",
        9
    );
    check_error(
        "{\"fnum\": nan}",
        "Invalid floating point literal in 'fnum': nan",
        9
    );
    check_error(
        "{\"fnum\": nanabcd}",
        "Invalid floating point literal in 'fnum': nanabcd",
        9
    );
    check_error(
        "{\"fnum\": \"1234\"}",
        "Unexpected token in 'fnum': STRING instead of PRIMITIVE",
        10
    );
    check_error(
        "{\"fnum2\": 999.99999, \"fnum\": 5000.00000000001}",
        "Floating point value 5000.00000000001 in 'fnum' out of range. It must be <= 5000.",
        29
    );
    check_error(
        "{\"fnum\": 5000, \"fnum2\": 1000}",
        "Floating point value 1000 in 'fnum2' out of range. It must be < 1000.",
        24
    );
    check_error(
        "{\"fnum2\": -999.99999, \"fnum\": -5000.0001}",
        "Floating point value -5000.0001 in 'fnum' out of range. It must be >= -5000.",
        30
    );
    check_error(
        "{\"fnum\": -5000, \"fnum2\": -1000}",
        "Floating point value -1000 in 'fnum2' out of range. It must be > -1000.",
        25
    );

    check_error(
        "{\"the_array\": [1, 2], \"fnum2\": }",
        "Missing value in 'document root', after key: fnum2",
        23
    );
    check_error(
        "{\"the_array\": [1, 2], \"name\": \"\"  \"fnum2\": 0}",
        "Missing separator between values in 'document root', after key: name",
        23
    );

    check_error(
        "{\"obj_with_subobj\": {\"a\": true, \"subsub\": {\"x\": 1, \"y\": 2}, \"b\": 2}}",
        "Invalid signed integer literal in 'a': true",
        26
    );
    check_error(
        "{\"obj_with_subobj\": {\"a\": 1, \"subsub\": {\"x\": true, \"y\": 2}, \"b\": 2}}",
        "Invalid signed integer literal in 'x': true",
        45
    );
    check_error(
        "{\"obj_with_subobj\": {\"a\": 1, \"subsub\": {\"x\": 1, \"y\": true}, \"b\": 2}}",
        "Invalid signed integer literal in 'y': true",
        53
    );
    check_error(
        "{\"obj_with_subobj\": {\"a\": 1, \"subsub\": {\"x\": 1, \"y\": 2}, \"b\": true}}",
        "Invalid signed integer literal in 'b': true",
        62
    );
    return 0;
}
