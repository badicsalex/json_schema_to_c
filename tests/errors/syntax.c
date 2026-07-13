#include "syntax.parser.h"

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
        "",
        "String did not contain any JSON tokens",
        0
    );
    return 0;
}
