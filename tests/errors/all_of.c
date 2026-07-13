#include "all_of.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    /* Each value satisfies the looser original bound but violates the merged one. */
    check_error(
        "{\"merged_int\": 5}",
        "Integer 5 in 'merged_int' out of range. It must be >= 10.",
        15
    );
    check_error(
        "{\"merged_int\": 80}",
        "Integer 80 in 'merged_int' out of range. It must be <= 50.",
        15
    );
    check_error(
        "{\"merged_str\": \"abc\"}",
        "String too short in 'merged_str'. Length: 3. Minimum length: 4.",
        16
    );
    check_error(
        "{\"merged_str\": \"abcdefghij\"}",
        "String too large in 'merged_str'. Length: 10. Maximum length: 8.",
        16
    );
    check_error(
        "{\"merged_arr\": [1]}",
        "Array 'merged_arr' too small. Length: 1. Minimum length: 2.",
        15
    );
    check_error(
        "{\"merged_arr\": [1,2,3,4,5]}",
        "Array 'merged_arr' too large. Length: 5. Maximum length: 4.",
        15
    );
    return 0;
}
