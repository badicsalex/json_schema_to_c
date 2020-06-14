#include "defaults.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t got;

    assert(!json_parse_root("{ \"id\": \"1234\", \"exists\": false, \"mass\": 4321}", &got));

    assert(strcmp(got.name, "cauliflower") == 0);
    assert(got.is_good == true);
    assert(got.number == 1337);
    assert(got.width == 567.12345);
    assert(strcmp(got.id, "1234") == 0);
    assert(got.exists == false);
    assert(got.mass == 4321);
    assert(got.attributes.n == 0);
    assert(got.sub_obj.is_good == true);
    assert(got.sub_obj.number == 1337);
    assert(got.sub_obj.sub_obj.is_good == true);
    assert(got.sub_obj.sub_obj.number == 1337);
    assert(got.the_enum == ROOT_THE_ENUM_ENUM_VAL_2);

    assert(
        !json_parse_root(
            "{ \
                \"name\": \"potato\", \
                \"is_good\": false, \
                \"number\": 5, \
                \"width\": 5, \
                \"id\": \"1234\", \"exists\": false, \"mass\": 4321, \
                \"sub_obj\": { \"sub_obj\": {\"number\": 420 }}, \
                \"the_enum\": \"enum_val_3\" \
            }", &got
        )
    );
    assert(!strcmp(got.name, "potato"));
    assert(!got.is_good);
    assert(got.number == 5);
    assert(got.width == 5.0);
    assert(got.attributes.n == 0);
    assert(got.sub_obj.sub_obj.number == 420);
    assert(got.the_enum == ROOT_THE_ENUM_ENUM_VAL_3);

    return 0;
}
