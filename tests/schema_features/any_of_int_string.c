#include "any_of_int_string.parser.h"

#include <string.h>
#include <assert.h>

/* Without a pattern the two options are unrelated, so this is an ordinary union
   instead of a number that may be spelled as a string. */
int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    assert(!json_parse_root("{\"value\": 42}", &root));
    assert(root.value.type == ROOT_VALUE_INT64);
    assert(root.value.int64 == 42);

    assert(!json_parse_root("{\"value\": \"42\"}", &root));
    assert(root.value.type == ROOT_VALUE_ROOT_VALUE_OPTION_1);
    assert(!strcmp(root.value.root_value_option_1, "42"));

    /* A string is not silently parsed as the integer option. */
    assert(!json_parse_root("{\"value\": \"hello\"}", &root));
    assert(root.value.type == ROOT_VALUE_ROOT_VALUE_OPTION_1);
    assert(!strcmp(root.value.root_value_option_1, "hello"));

    return 0;
}
