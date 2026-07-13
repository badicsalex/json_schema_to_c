#include "with_len.parser.h"

#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    /* Valid JSON inside a larger, non-NUL-terminated buffer: strlen would overread, so the
       caller's length must bound the parse and the trailing junk must be left unparsed. */
    const char data[] = {
        '{', '"', 'v', 'a', 'l', 'u', 'e', '"', ':', ' ', '4', '2', '}',
        '!', 'j', 'u', 'n', 'k', '{', '['
    };
    const size_t json_len = 13;
    root_t root = {};
    assert(!json_parse_root_with_len(data, json_len, &root));
    assert(root.value == 42);
    return 0;
}
