#include "alternate_storage.parser.h"

#include <string.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* "meta" is js2cType: void and not listed in "required", so it is optional: omitting it still
       parses. "blob" is js2cType: raw and required. */
    const char* d1 = "{\"kept\": 7, \"blob\": [10, 20, 30]}";
    root_t root = {};
    assert(!json_parse_root(d1, &root));
    assert(root.kept == 7);

    /* void is dropped, not stored: the struct holds only kept and blob, and a leaked void member
       would make root_t larger than this. */
    struct expected_layout { int64_t kept; root_json_ref_t blob; };
    assert(sizeof(root_t) == sizeof(struct expected_layout));

    /* raw kept a reference to the raw text of its value, brackets included. */
    const char* blob1 = "[10, 20, 30]";
    assert(root.blob.length == strlen(blob1));
    assert(!strncmp(d1 + root.blob.index, blob1, root.blob.length));

    /* When "meta" is present (here a nested object), it is validated then dropped. */
    const char* d2 = "{\"kept\": 1, \"meta\": {\"a\": 1, \"b\": [2, 3]}, \"blob\": [4]}";
    root_t root2 = {};
    assert(!json_parse_root(d2, &root2));
    assert(root2.kept == 1);
    assert(!strncmp(d2 + root2.blob.index, "[4]", root2.blob.length));

    return 0;
}
