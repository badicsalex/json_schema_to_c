#include "any_of_option_names.parser.h"

#include <assert.h>

/* Union members are named after their option's type. "bool" is a C keyword, and a name
   stripped down to "0" is not an identifier at all, so both get an option_ prefix. */
int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    assert(!json_parse_root("{\"keyword\": 42, \"digit\": {\"a\": 1}}", &root));
    assert(root.keyword.type == ROOT_KEYWORD_OPTION_INT64);
    assert(root.keyword.option_int64 == 42);
    assert(root.digit.type == ROOT_DIGIT_OPTION_0);
    assert(root.digit.option_0.a == 1);

    assert(!json_parse_root("{\"keyword\": true, \"digit\": {\"b\": 2}}", &root));
    assert(root.keyword.type == ROOT_KEYWORD_OPTION_BOOL);
    assert(root.keyword.option_bool == true);
    assert(root.digit.type == ROOT_DIGIT_OPTION_1);
    assert(root.digit.option_1.b == 2);

    return 0;
}
