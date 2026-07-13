#include "large_bound.parser.h"

#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    /* The maximum (1.8e19) exceeds INT64_MAX, so its range-check literal must be ULL-suffixed,
       and a value just under it must still be accepted. */
    assert(!json_parse_root("{\"big\": 17000000000000000000}", &root));
    assert(root.big == 17000000000000000000ULL);
    return 0;
}
