#include "custom_parser.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root("{}", &root));
    assert(root.id == 0xABCDEF);
    assert(root.point.x == 'a');
    assert(root.point.y == 'b');

    assert(!json_parse_root("{\"id\": \"1234\", \"point\": \"xy\"}", &root));
    assert(root.id == 0x1234);
    assert(root.point.x == 'x');
    assert(root.point.y == 'y');

    assert(json_parse_root("{\"id\": \"X\", \"point\": \"xy\"}", &root));
    assert(json_parse_root("{\"id\": \"1\", \"point\": \"xyz\"}", &root));
    return 0;
}
