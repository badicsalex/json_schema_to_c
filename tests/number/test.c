#include "parser.h"

#include <stdio.h>

root_t root = {};

const char* data = "{\"the_num\": 1337 }";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Sizeof num: %li\n", sizeof(root.the_num));
    printf("The num: %li\n", root.the_num);
    return 0;
}
