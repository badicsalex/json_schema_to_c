#include "parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>

root_t root = {};

const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true}}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    assert(!strcmp(root.vegetable.name, "potato"));
    return 0;
}
