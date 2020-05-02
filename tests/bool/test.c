#include "parser.h"

#include <stdio.h>

root_t root = {};

int main(int argc, char** argv){
    if (parse(argv[1], &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Bool1: %s\n", root.bool1 ? "true" : "false");
    printf("Bool2: %s\n", root.bool2 ? "true" : "false");
    return 0;
}
