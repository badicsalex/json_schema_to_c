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
    assert(THE_ENUM_AND_THE_LAST == THE_ENUM_LAST - 1);
    return 0;
}
