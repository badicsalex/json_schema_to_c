#include "simple.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "\"apple\"";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    assert(!strcmp(root, "apple"));
    return 0;
}
