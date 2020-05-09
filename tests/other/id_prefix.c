#include "id_prefix.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;

    /* We are mainly interested in the type name and the parse functio name.*/
    AnInteresting_schema1d_t the_object = 0;
    assert(!json_parse_AnInteresting_schema1d("1", &the_object));
    assert(the_object == 1);
    return 0;
}
