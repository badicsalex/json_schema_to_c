#include "cpp.parser.h"

#include <stdio.h>
#include <assert.h>

#ifndef __cplusplus
#error This file should be complied with C++
#endif

int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* The type her MUST be int64_t, or else it's a breaking change. */
    int64_t the_num = 0;
    assert(!json_parse_root("1337 ", &the_num));
    assert(the_num == 1337);

    return 0;
}
