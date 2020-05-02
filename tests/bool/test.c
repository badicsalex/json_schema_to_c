#include "parser.h"

#include <stdio.h>

root_t root = {};

const char* data = "{\"bool1\": false, \"bool2\": true}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Bool1: %s\n", root.bool1 ? "true" : "false");
    printf("Bool2: %s\n", root.bool2 ? "true" : "false");
    return 0;
}
