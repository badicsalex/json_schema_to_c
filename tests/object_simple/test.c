#include "parser.h"

#include <stdio.h>

root_t root = {};

int main(int argc, char** argv){
    if (parse(argv[1], &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("The name: %s\n", root.vegetable.name);
    return 0;
}
