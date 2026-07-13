#include "integer.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
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
    return 0;
}
