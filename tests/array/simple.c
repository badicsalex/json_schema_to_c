#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>

const char* data = "[1,2,3,4,5,6,7]";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    for (unsigned i=0; i<root.n; ++i){
        assert(root.items[i] == i + 1);
    }
    return 0;
}
