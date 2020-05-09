#include "unsigned.parser.h"

#include <stdio.h>
#include <assert.h>


const char* data = "{\"a\": 18446744073709551615, \"b\": 18446744073709551615}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root;

    assert(!json_parse_root(data, &root));
    assert(root.a == 0xffffffffffffffffULL);
    assert(root.b == 0xffffffffffffffffULL);
    return 0;
}
