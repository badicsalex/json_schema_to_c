#include "simple.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    the_enum_t root = THE_ENUM_LAST;
    assert(!json_parse_the_enum("\"value to s@nitize\"", &root));
    assert(root == THE_ENUM_VALUE_TO_S_NITIZE);
    assert(!json_parse_the_enum("\"camelCased1\"", &root));
    assert(root == THE_ENUM_CAMEL_CASED_1);
    /* Mainly here to check if the enum label exists */
    assert(root != THE_ENUM_CAMEL_AND_UNDERSCORE);
    assert(root != THE_ENUM_TITLE_CASED);
    assert(root != THE_ENUM_JS_2_C);
    assert(root != THE_ENUM_JS_1337_C);
    assert(root != THE_ENUM_I_HATE_JSCRIPT);
    assert(root != THE_ENUM_AA_AA_AAA_AAAA);
    return 0;
}
