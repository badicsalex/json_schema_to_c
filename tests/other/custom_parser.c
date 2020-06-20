#include "custom_parser.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root("{}", &root));
    assert(root.id == 0x01EFCDAB01EFCDAB);
    assert(root.point.x == 'a');
    assert(root.point.y == 'b');

    assert(!json_parse_root("{\"id\": \"1234\", \"short_id\": \"1234\", \"point\": \"xy\"}", &root));
    assert(root.id == 0x3412000000000000);
    assert(root.short_id == 0x3412000000000000);
    assert(root.point.x == 'x');
    assert(root.point.y == 'y');

    assert(json_parse_root("{\"id\": \"X\", \"point\": \"xy\"}", &root));
    assert(json_parse_root("{\"id\": \"1\", \"point\": \"xyz\"}", &root));

    assert(json_parse_root("{\"short_id\": \"1\"}", &root));
    assert(json_parse_root("{\"short_id\": \"12345678\"}", &root));
    assert(json_parse_root("{\"short_id\": 12345678}", &root));
    return 0;
}
