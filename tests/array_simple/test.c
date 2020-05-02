#include "parser.h"

#include <stdio.h>

root_t root = {};

int main(int argc, char** argv){
    if (parse(argv[1], &root)){
        printf("Parse failed\n");
        return 2;
    }
    for (unsigned i=0; i<root.the_array.n; ++i){
        printf("Num %u: %li\n", i, root.the_array.items[i]);
    }
    return 0;
}
