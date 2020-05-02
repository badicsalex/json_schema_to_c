#include "parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>

root_t root = {};

const char* data = "{\"fruit\": \"apple\"}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    assert(!strcmp(root.fruit, "apple"));
    return 0;
}
