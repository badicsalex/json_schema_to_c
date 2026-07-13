#include "array.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "{\"the_array\": 1}",
        "Unexpected token in 'the_array': PRIMITIVE instead of ARRAY",
        14
    );
    check_error(
        "{\"the_array\": [1,2,3,4]}",
        "Array 'the_array' too large. Length: 4. Maximum length: 3.",
        14
    );
    check_error(
        "{\"the_array\": [1]}",
        "Array 'the_array' too small. Length: 1. Minimum length: 2.",
        14
    );
    return 0;
}
