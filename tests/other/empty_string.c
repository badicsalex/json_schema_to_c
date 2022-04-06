#include "empty_string.parser.h"

#include <assert.h>
#include <stdio.h>

bool __attribute__((noinline)) parse_no_inline(const char *json_string, root_t *out) {
    return json_parse_root(json_string, out);
}

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;
    root_t data;
    /* poison the stack */
    assert(!parse_no_inline("\"aaaa\" ", &data));
    /* parsing an empty sring should be a non-crashing error */
    assert(parse_no_inline("", &data));
    return 0;
}
