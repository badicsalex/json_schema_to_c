#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    bool the_bool;
    assert(!json_parse_root("true", &the_bool));
    assert(the_bool == true);

    assert(!json_parse_root("false", &the_bool));
    assert(the_bool == false);
    return 0;
}
