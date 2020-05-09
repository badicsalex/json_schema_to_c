#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>


const char* data = "1337";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* The type her MUST be int64_t, or else it's a breaking change. */
    int64_t the_num = 0;
    assert(!json_parse_root(data, &the_num));
    assert(the_num == 1337);
    return 0;
}
