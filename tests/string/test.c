#include "parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "\"apple\"";

int main(int argc, char** argv){
    root_t root = {};
    assert(!parse(data, &root));
    assert(!strcmp(root, "apple"));
    return 0;
}
