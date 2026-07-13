#include "parse_function.parser.h"

#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    /* Valid labels are validated, then transformed by the custom parser. */
    assert(!json_parse_root("{\"color\": \"red\"}", &root));
    assert(root.color == 0xFF0000);
    assert(!json_parse_root("{\"color\": \"blue\"}", &root));
    assert(root.color == 0x0000FF);

    /* The default goes through the parser too. */
    assert(!json_parse_root("{}", &root));
    assert(root.color == 0x00FF00);

    /* A string outside the enum is rejected before the parser runs. */
    assert(json_parse_root("{\"color\": \"cyan\"}", &root));

    return 0;
}
