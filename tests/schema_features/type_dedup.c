#include "type_dedup.parser.h"

#include <string.h>
#include <assert.h>

/* Two fields with the same $id describe the same C type, so the type cache compares them
   and declares it once. The fields share the type, rather than getting a copy each. */
int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    assert(!json_parse_root(
        "{\"name_a\": \"one\", \"name_b\": \"two\","
        " \"list_a\": [1], \"list_b\": [2, 3],"
        " \"either_a\": 7, \"either_b\": false}", &root));

    assert(!strcmp(root.name_a, "one"));
    assert(!strcmp(root.name_b, "two"));
    assert(root.list_a.n == 1 && root.list_a.items[0] == 1);
    assert(root.list_b.n == 2 && root.list_b.items[1] == 3);
    assert(root.either_a.type == EITHER_OPTION_INT64 && root.either_a.option_int64 == 7);
    assert(root.either_b.type == EITHER_OPTION_BOOL && root.either_b.option_bool == false);

    /* Same $id, same C type: a struct only assigns to an identical one. */
    root.list_b = root.list_a;
    root.either_b = root.either_a;
    assert(root.list_b.n == 1 && root.list_b.items[0] == 1);
    assert(root.either_b.type == EITHER_OPTION_INT64 && root.either_b.option_int64 == 7);

    /* An array cannot be assigned, so its size is all there is to compare. */
    assert(sizeof(root.name_a) == sizeof(root.name_b));
    root.name_b[0] = root.name_a[0];
    assert(root.name_b[0] == 'o');

    return 0;
}
