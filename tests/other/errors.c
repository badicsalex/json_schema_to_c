#include "errors.parser.h"

#include <string.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "INVALID",
        "Unexpected token: PRIMITIVE instead of OBJECT",
        0
    );
    check_error(
        "[]",
        "Unexpected token: ARRAY instead of OBJECT",
        0
    );
    check_error(
        "{",
        "JSON syntax error: End-of-file reached (JSON file incomplete)",
        1
    );
    char many_objects[20001];
    memset(many_objects, '{', 10000);
    memset(many_objects + 10000, '}', 10000);
    check_error(
        many_objects,
        "JSON syntax error: JSON file too complex",
        -1 /* don't care about the actual position of the failure here */
    );

    check_error(
        "{\"name\": INVALID}",
        "Unexpected token: PRIMITIVE instead of STRING",
        9
    );
    check_error(
        "{\"name\": \"n>8 here.\"}",
        "String too large. Length: 9. Maximum length: 8.",
        10
    );
    check_error(
        "{\"name\": \" <4\"}",
        "String too short. Length: 3. Minimum length: 4.",
        10
    );

    check_error(
        "{\"is_good\": INVALID}",
        "Invalid boolean literal: INVALID",
        12
    );
    check_error(
        "{\"is_good\": \"true\"}",
        "Unexpected token: STRING instead of PRIMITIVE",
        13
    );

    check_error(
        "{\"num\": INVALID}",
        "Invalid signed integer literal: INVALID",
        8
    );
    check_error(
        "{\"num\": 100e}",
        "Invalid signed integer literal: 100e",
        8
    );
    check_error(
        "{\"num\": 0x100}",
        "Invalid signed integer literal: 0x100",
        8
    );
    check_error(
        "{\"num\": \"1234\"}",
        "Unexpected token: STRING",
        9
    );
    check_error(
        "{\"unsigned_num\": INVALID}",
        "Invalid unsigned integer literal: INVALID",
        17
    );
    check_error(
        "{\"unsigned_num\": 100e}",
        "Invalid unsigned integer literal: 100e",
        17
    );
    check_error(
        "{\"unsigned_num\": 0x100}",
        "Invalid unsigned integer literal: 0x100",
        17
    );
    check_error(
        "{\"unsigned_num\": \"1234\"}",
        "Unexpected token: STRING",
        18
    );

    check_error(
        "{\"num2\": 999, \"num\": 5001}",
        "Integer 5001 out of range. It must be <= 5000.",
        21
    );
    check_error(
        "{\"num\": 5000, \"num2\": 1000}",
        "Integer 1000 out of range. It must be < 1000.",
        22
    );
    check_error(
        "{\"num2\": -999, \"num\": -5001}",
        "Integer -5001 out of range. It must be >= -5000.",
        22
    );
    check_error(
        "{\"num\": -5000, \"num2\": -1000}",
        "Integer -1000 out of range. It must be > -1000.",
        23
    );
    check_error(
        "{\"unsigned_num\": -5000}",
        "Invalid unsigned integer literal: -5000",
        17
    );
    check_error(
        "{\"unsigned_num2\": -5000}",
        "Invalid unsigned integer literal: -5000",
        18
    );
    check_error(
        "{\"unsigned_num2\": 120}",
        "Integer 120 out of range. It must be >= 123.",
        18
    );
    check_error(
        "{\"unsigned_num2\": 1200}",
        "Integer 1200 out of range. It must be <= 456.",
        18
    );

    check_error(
        "{\"numeric_string\": 1234}",
        "Unexpected token: PRIMITIVE",
        19
    );
    check_error(
        "{\"numeric_string\": -1234}",
        "Unexpected token: PRIMITIVE",
        19
    );
    check_error(
        "{\"numeric_string\": \"0x1234\"}",
        "Invalid unsigned integer literal: 0x1234",
        20
    );
    check_error(
        "{\"numeric_string\": \"INVALID\"}",
        "Invalid unsigned integer literal: INVALID",
        20
    );
    check_error(
        "{\"anyof_hex\": 12}",
        "Integer 12 out of range. It must be >= 123.",
        14
    );
    check_error(
        "{\"anyof_hex\": \"12\"}",
        "Integer 18 out of range. It must be >= 123.",
        15
    );

    check_error(
        "{\"the_array\": 1}",
        "Unexpected token: PRIMITIVE instead of ARRAY",
        14
    );
    check_error(
        "{\"the_array\": [1,2,3,4]}",
        "Array root_the_array too large. Length: 4. Maximum length: 3.",
        14
    );
    check_error(
        "{\"the_array\": [1]}",
        "Array root_the_array too small. Length: 1. Minimum length: 2.",
        14
    );

    check_error(
        "{}",
        "Missing required field in root: the_array",
        2
    );
    check_error(
        "{\"num\": 1234, \"num\": 1234}",
        "Duplicate field definition in root: num",
        15
    );
    check_error(
        "{\"nonexistent\": INVALID}",
        "Unknown field in root: nonexistent",
        2
    );

    check_error(
        "{\"error_arr\": [{}]}",
        "Error parsing THE ERRORER, value=\"INVALID DEFAULT\": error calling error_creating_parser",
        21
    );
    check_error(
        "{\"error_arr\": [{\"trigger\": \"ab\"}]}",
        "Error parsing THE ERRORER, value=\"ab\": Custom error",
        28
    );
    check_error(
        "{\"error_arr\": [{\"trigger\": \"abc\"}]}",
        "Error parsing THE ERRORER, value=\"abc\": error calling error_creating_parser",
        28
    );

    check_error(
        "{\"the_enum\": \"x\"}",
        "Unknown enum value in root_the_enum: x",
        14
    );
    check_error(
        "{\"the_enum\": 5}",
        "Unexpected token: PRIMITIVE instead of STRING",
        13
    );
    return 0;
}
