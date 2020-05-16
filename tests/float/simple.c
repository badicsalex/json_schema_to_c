#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* The type her MUST be double, or else it's a breaking change. */
    double the_num = 0;
    assert(!json_parse_root("1337", &the_num));
    assert(the_num == 1337.0);
    assert(!json_parse_root("3.141592653589793", &the_num));
    assert(the_num == 3.141592653589793);
    assert(!json_parse_root("1e200", &the_num));
    assert(the_num == 1e200);

    /* Very small denormal */
    assert(!json_parse_root("-1e-323", &the_num));
    assert(the_num == -1e-323);
    return 0;
}
