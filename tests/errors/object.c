#include "object.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "{\"num\": 1}",
        "Missing required field in 'document root': the_array",
        0
    );
    check_error(
        "{}",
        "Missing required field in 'document root': the_array",
        0
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
