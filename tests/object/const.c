#include "const.parser.h"

#include <string.h>
#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    /* Matching const, optional one omitted; const fields have no struct member, name still defaults. */
    assert(!json_parse_root("{\"version\": 1}", &root));
    assert(!strcmp(root.name, "x"));

    /* Optional const present and matching. */
    assert(!json_parse_root("{\"version\": 1, \"kind\": \"widget\"}", &root));

    /* Wrong const values are rejected. */
    assert(json_parse_root("{\"version\": 2}", &root));
    assert(json_parse_root("{\"version\": 1, \"kind\": \"gadget\"}", &root));

    /* Required const missing is rejected; the optional const may stay absent. */
    assert(json_parse_root("{}", &root));

    return 0;
}
