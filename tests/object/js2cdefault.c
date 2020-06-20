#include "js2cdefault.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t got, expected;
    /* memset is needed for the later memcmp. Otherwise, padding bytes will not get set to 0. */
    memset(&got, 0, sizeof(root_t));
    memset(&expected, 0, sizeof(root_t));

    assert(!json_parse_root("{}", &got));
    assert(strcmp(got.name, "cauliflower") == 0);
    assert(got.is_good == true);
    assert(got.number == 1337);
    assert(strcmp(got.id, "xxxx") == 0);
    assert(got.mass == 1338);
    assert(got.sub_obj.number == 1339);
    assert(got.sub_obj.mass == 1330);
    assert(got.the_enum == ROOT_THE_ENUM_ENUM_VAL_3);
    assert(got.def_obj.number == 5432);
    assert(got.def_arr.n == 3);
    assert(got.def_arr.items[2] == 3);

    return 0;
}
