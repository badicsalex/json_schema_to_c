#include "parser.h"

#include <stdio.h>

root_t root = {};

int main(int argc, char** argv){
    if (parse(argv[1], &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Sizeof num: %li\n", sizeof(root.the_num));
    printf("The num: %li\n", root.the_num);
    return 0;
}
