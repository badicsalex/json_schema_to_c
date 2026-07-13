#include "any_of.parser.h"

#include <string.h>
#include <assert.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    /* First option (a bare integer): parses, and logs nothing. */
    last_error[0] = '\0';
    assert(!json_parse_root("{\"value\": 42}", &root));
    assert(root.value.type == ROOT_VALUE_INT64);
    assert(root.value.int64 == 42);
    assert(last_error[0] == '\0');

    /* Second option: the integer is tried first and fails, but its error must not surface. */
    last_error[0] = '\0';
    assert(!json_parse_root("{\"value\": {\"x\": 1, \"y\": 2}}", &root));
    assert(root.value.type == ROOT_VALUE_POINT);
    assert(root.value.point.x == 1);
    assert(root.value.point.y == 2);
    assert(last_error[0] == '\0');

    /* No option matches: only the union's own error is reported. */
    assert(json_parse_root("{\"value\": \"neither\"}", &root));
    assert(!strcmp(last_error, "Invalid anyOf value in 'value': no option matched"));

    return 0;
}
