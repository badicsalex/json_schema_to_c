#include "parser.h"

#include <stdio.h>

root_t root = {};

const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true}}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("The name: %s\n", root.vegetable.name);
    return 0;
}
