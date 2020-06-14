#include "no_label_convert.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    the_enum_t root = THE_ENUM_last;
    assert(!json_parse_the_enum("\"value to s@nitize\"", &root));
    assert(root == THE_ENUM_value_to_s_nitize);
    assert(!json_parse_the_enum("\"camelCased1\"", &root));
    assert(root == THE_ENUM_camelCased1);
    /* Mainly here to check if the enum label exists */
    assert(root != THE_ENUM_camel_andUnderscore);
    assert(root != THE_ENUM_TitleCased);
    return 0;
}
