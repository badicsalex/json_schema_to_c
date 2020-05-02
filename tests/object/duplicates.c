#include "duplicates.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    root_t root = {};
    assert(!json_parse_root("{ \"name\": \"potato\", \"is_good\": true}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(json_parse_root("{ \"name\": \"potato\", \"is_good\": true, \"name\": \"potato\"}", &root));
    assert(json_parse_root("{ \"is_good\": true, \"name\": \"potato\", \"name\": \"potato\"}", &root));
    assert(json_parse_root("{ \"is_good\": true, \"name\": \"potato\", \"is_good\": true}", &root));

    return 0;
}
