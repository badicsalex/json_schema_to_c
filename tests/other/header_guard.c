#include "header_guard.parser.h"
#include "header_guard.parser.h"
#include "header_guard.parser.h"

#include <stdio.h>
#include <assert.h>
#include <string.h>


const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true}}";

int main(int argc, char** argv){
    root_t root = {};
    assert(!json_parse_root(data, &root));
    assert(!strcmp(root.vegetable.name, "potato"));
    return 0;
}
