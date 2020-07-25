#include "all_of.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{"
    "\"veggie1\": {"
        "\"name\": \"potato\","
        "\"name2\": \"peas\","
        "\"is_good\": true"
    "},"
    "\"veggie2\": {"
        "\"is_good\": true"
    "}"
"}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    assert(!strcmp(root.veggie2.name, "ayaya"));
    assert(!strcmp(root.veggie2.name2, "lel"));
    return 0;
}
