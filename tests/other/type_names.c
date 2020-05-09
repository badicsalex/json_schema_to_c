#include "type_names.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true}}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    vegetable_t vegetable = root.vegetable;
    name_t name;
    memcpy(name, vegetable.name, sizeof(name));
    assert(!strcmp(name, "potato"));
    return 0;
}
