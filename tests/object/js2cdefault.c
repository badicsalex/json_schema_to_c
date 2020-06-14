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

    /* Now that padding bytes are take care of, set fields */
    expected = (root_t){
        .name="cauliflower",
        .is_good=true,
        .number=1337,
        .id="xxxx",
        .mass=1338,
        .sub_obj={
            .number=1339,
            .mass=1330
        }
    };
    assert(!json_parse_root("{}", &got));

    /* This is actually UB because of the padding bytes. We should compare field-by-field */
    assert(!memcmp(&got, &expected, sizeof(root_t)));

    return 0;
}
