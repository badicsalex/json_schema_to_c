#include "parser.h"

#include <stdio.h>

root_t root = {};

const char* data = "{\"fruit\": \"apple\"}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("The str: %s\n", root.fruit);
    return 0;
}
