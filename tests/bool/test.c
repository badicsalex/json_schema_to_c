#include "parser.h"

#include <stdio.h>
#include <assert.h>

root_t root = {};

const char* data = "{\"bool1\": false, \"bool2\": true}";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    assert(root.bool1 == false);
    assert(root.bool2 == true);
    return 0;
}
