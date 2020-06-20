#include "custom_types.parser.h"

#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root;

    assert(sizeof(root.u8) == 1);
    assert(sizeof(root.u16) == 2);
    assert(sizeof(root.u32) == 4);
    assert(sizeof(root.u64) == 8);
    assert(sizeof(root.s8) == 1);
    assert(sizeof(root.s16) == 2);
    assert(sizeof(root.s32) == 4);
    assert(sizeof(root.s64) == 8);
    assert(!json_parse_root("{"
        "\"u8\": 255,"
        "\"u16\": 65535,"
        "\"u32\": 4294967295,"
        "\"u64\": 18446744073709551615,"
        "\"s8\": -128,"
        "\"s16\": -32768,"
        "\"s32\": -2147483648,"
        "\"s64\": -9223372036854775807"
    "}", &root));

    assert(root.u8 == 255);
    assert(root.u16 == 65535);
    assert(root.u32 == 4294967295);
    assert(root.u64 == 18446744073709551615ULL);
    assert(root.s8 == -128);
    assert(root.s16 == -32768);
    assert(root.s32 == -2147483648);
    assert(root.s64 == -9223372036854775807LL);

    assert(root.min0 == -9223372036854775806LL);


    return 0;
}
