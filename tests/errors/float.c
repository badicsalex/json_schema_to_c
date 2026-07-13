#include "float.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
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
    return 0;
}
