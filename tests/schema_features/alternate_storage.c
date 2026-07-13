#include "alternate_storage.parser.h"

#include <string.h>
#include <assert.h>


const char* data = "{\"kept\": 7, \"ignored\": {\"a\": 1, \"b\": [2, 3]}, \"blob\": [10, 20, 30]}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    assert(root.kept == 7);

    /* "ignored" is js2cType: void, so it is dropped, not stored: the struct holds only kept and
       blob, and a leaked void member would make root_t larger than this. */
    struct expected_layout { int64_t kept; root_json_ref_t blob; };
    assert(sizeof(root_t) == sizeof(struct expected_layout));

    /* "blob" (raw) kept a reference to the raw text of its value, brackets included. */
    const char* expected = "[10, 20, 30]";
    assert(root.blob.length == strlen(expected));
    assert(!strncmp(data + root.blob.index, expected, root.blob.length));
    return 0;
}
