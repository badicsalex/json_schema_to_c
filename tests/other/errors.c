#include "errors.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>

void check_error(const char* json, const char* expected_str, int expected_pos){
    root_t root = {};
    assert(json_parse_root(json, &root));
    if (strcmp(last_error, expected_str)){
        fprintf(stderr, "When checking %s\n", json);
        fprintf(stderr, "Last error: %s\n", last_error);
        fprintf(stderr, "Expected  : %s\n", expected_str);
        assert(false);
    }
    if (expected_pos != -1 && expected_pos != last_error_pos){
        fprintf(stderr, "When checking %s\n", json);
        fprintf(stderr, "Last error pos: %i\n", last_error_pos);
        fprintf(stderr, "Expected   pos: %i\n", expected_pos);
        assert(false);
    }
}

int main(int argc, char** argv){
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
        "Invalid integer literal: INVALID",
        8
    );
    check_error(
        "{\"num\": 100e}",
        "Invalid integer literal: 100e",
        8
    );
    check_error(
        "{\"num\": 0x100}",
        "Invalid integer literal: 0x100",
        8
    );
    check_error(
        "{\"num\": \"1234\"}",
        "Unexpected token: STRING instead of PRIMITIVE",
        9
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

    return 0;
}
