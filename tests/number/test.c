#include "parser.h"

#include <stdio.h>
#include <assert.h>

root_t root = {};

const char* data = "{\"the_num\": 1337 }";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    assert(sizeof(root.the_num) == 8);
    assert(root.the_num == 1337);
    return 0;
}
