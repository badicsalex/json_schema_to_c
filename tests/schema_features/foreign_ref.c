#include "foreign_ref.parser.h"

#include <string.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    /* Both fields come from a $ref into a sibling schema file. */
    assert(!json_parse_root("{\"name\": \"potato\", \"weight\": 250}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(root.weight == 250);
    return 0;
}
