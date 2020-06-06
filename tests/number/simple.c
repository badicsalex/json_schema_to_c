#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* The type her MUST be int64_t, or else it's a breaking change. */
    int64_t the_num = 0;
    assert(!json_parse_root("1337 ", &the_num));
    assert(the_num == 1337);

    assert(!json_parse_root("9223372036854775807 ", &the_num));
    assert(the_num == 9223372036854775807LL);

    assert(!json_parse_root("-9223372036854775807 ", &the_num));
    assert(the_num == -9223372036854775807LL);
    return 0;
}
