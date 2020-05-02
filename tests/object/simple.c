#include "simple.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true}}";

int main(int argc, char** argv){
    root_t root = {};
    assert(!parse(data, &root));
    assert(!strcmp(root.vegetable.name, "potato"));
    return 0;
}
