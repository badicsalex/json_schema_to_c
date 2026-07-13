#include "enum.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
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
        "{\"parsed_enum\": \"x\"}",
        "Unknown enum value in 'parsed_enum': x",
        17
    );
    check_error(
        "{\"parsed_enum\": \"bb\"}",
        "Error parsing 'parsed_enum', value=\"bb\": Custom error",
        17
    );
    return 0;
}
