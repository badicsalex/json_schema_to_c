#include "custom.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "{\"error_arr\": [{}]}",
        "Error parsing 'error_arr', value=\"INVALID DEFAULT\": error calling error_creating_parser",
        15
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
    return 0;
}
