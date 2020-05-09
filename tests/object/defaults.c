#include "defaults.parser.h"

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

    /* Now that padding bytes are take care of, set fields */
    expected = (root_t){
        .name="cauliflower",
        .is_good=true,
        .number=1337,
        .id="1234",
        .exists=false,
        .mass=4321
    };
    assert(!json_parse_root("{ \"id\": \"1234\", \"exists\": false, \"mass\": 4321}", &got));

    /* This is actually UB because of the padding bytes. We should compare field-by-field */
    assert(!memcmp(&got, &expected, sizeof(root_t)));

    assert(
        !json_parse_root(
            "{ \
                \"name\": \"potato\", \
                \"is_good\": false, \
                \"number\": 5, \
                \"id\": \"1234\", \"exists\": false, \"mass\": 4321 \
            }", &got
        )
    );
    assert(!strcmp(got.name, "potato"));
    assert(!got.is_good);
    assert(got.number == 5);

    return 0;
}
