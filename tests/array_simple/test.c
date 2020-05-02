#include "parser.h"

#include <stdio.h>

root_t root = {};

const char* data = "{\"the_array\": [1,2,3,4,5,6,7]}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    for (unsigned i=0; i<root.the_array.n; ++i){
        printf("Num %u: %li\n", i, root.the_array.items[i]);
    }
    return 0;
}
