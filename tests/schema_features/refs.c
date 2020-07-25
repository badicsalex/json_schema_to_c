#include "refs.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{\"veggie1\": { \"name\": \"potato\", \"is_good\": true}, \"veggie2\": { \"name\": \"tomato\", \"is_good\": true},}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    assert(!strcmp(root.veggie1.name, "potato"));
    assert(!strcmp(root.veggie2.name, "tomato"));
    return 0;
}
