#include "parser.h"

#include <stdio.h>

root_t root = {};

int main(int argc, char** argv){
    if (parse(argv[1], &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Some thing is %s\nSome other thing is %ld\n", root.fruits.items[2], root.multidimensionals.items[1].items[0].items[1]);
}
