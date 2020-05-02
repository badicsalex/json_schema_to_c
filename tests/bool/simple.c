#include "simple.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    bool the_bool;
    assert(!parse("true", &the_bool));
    assert(the_bool == true);

    assert(!parse("false", &the_bool));
    assert(the_bool == false);
    return 0;
}
