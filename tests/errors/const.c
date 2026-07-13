#include "const.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "{\"a_const\": 43}",
        "Invalid const value in 'a_const', expected: 42",
        12
    );
    check_error(
        "{\"a_str_const\": \"wrong\"}",
        "Invalid const value in 'a_str_const', expected: fixed",
        17
    );
    return 0;
}
