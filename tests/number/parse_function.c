#include "parse_function.parser.h"

#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    /* The parsed integer is passed through int_double() and stored as its output type. */
    assert(!json_parse_root("{\"doubled\": 10}", &root));
    assert(root.doubled == 20);

    /* The default (21) also goes through int_double(). */
    assert(!json_parse_root("{}", &root));
    assert(root.doubled == 42);

    /* Range checks apply to the raw integer, before the custom function. */
    assert(json_parse_root("{\"doubled\": 2000}", &root));

    /* The custom function can reject a value. */
    assert(json_parse_root("{\"doubled\": 13}", &root));
    return 0;
}
