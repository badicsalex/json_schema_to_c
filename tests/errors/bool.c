#include "bool.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
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
    return 0;
}
