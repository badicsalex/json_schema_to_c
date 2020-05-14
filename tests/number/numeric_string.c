#include "numeric_string.parser.h"

#include <stdio.h>
#include <assert.h>


int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root;

    /* Check defaults */
    assert(!json_parse_root("{}", &root));
    assert(root.decimal == 1234);
    assert(root.hex1 == 0x1234);
    assert(root.hex2 == 0x1234);
    assert(root.autonum == 0x1234);
    assert(root.u_decimal == 1234);
    assert(root.u_hex1 == 0x1234);
    assert(root.u_hex2 == 0x1234);
    assert(root.u_autonum == 0x1234);
    assert(root.anyof_hex == 1234);

    /* String not allowed */
    assert(json_parse_root("{\"decimal\": asdads}", &root));

    /* Signed cases */
    assert(!json_parse_root("{\"decimal\": \"5432\"}", &root));
    assert(root.decimal == 5432);
    assert(!json_parse_root("{\"decimal\": \"-5432\"}", &root));
    assert(root.decimal == -5432);

    assert(!json_parse_root("{\"hex1\": \"5432\"}", &root));
    assert(root.hex1 == 0x5432);
    assert(!json_parse_root("{\"hex1\": \"-5432\"}", &root));
    assert(root.hex1 == -0x5432);

    assert(!json_parse_root("{\"hex2\": \"0x5432\"}", &root));
    assert(root.hex2 == 0x5432);
    assert(!json_parse_root("{\"hex2\": \"-0x5432\"}", &root));
    assert(root.hex2 == -0x5432);

    assert(!json_parse_root("{\"autonum\": \"05432\"}", &root));
    assert(root.autonum == 05432);

    assert(!json_parse_root("{\"autonum\": \"0x5432\"}", &root));
    assert(root.autonum == 0x5432);
    assert(!json_parse_root("{\"autonum\": \"-0x5432\"}", &root));
    assert(root.autonum == -0x5432);

    assert(!json_parse_root("{\"autonum\": \"5432\"}", &root));
    assert(root.autonum == 5432);

    assert(!json_parse_root("{\"anyof_hex\": \"123\"}", &root));
    assert(root.anyof_hex == 0x123);
    assert(!json_parse_root("{\"anyof_hex\": 5432}", &root));
    assert(root.anyof_hex == 5432);

    /* Unsigned cases */
    assert(json_parse_root("{\"u_decimal\": 5}", &root));
    assert(!json_parse_root("{\"u_decimal\": \"5432\"}", &root));
    assert(root.u_decimal == 5432);
    assert(json_parse_root("{\"u_decimal\": \"-5432\"}", &root));

    assert(!json_parse_root("{\"u_hex1\": \"5432\"}", &root));
    assert(root.u_hex1 == 0x5432);
    assert(json_parse_root("{\"u_hex1\": \"-5432\"}", &root));

    assert(!json_parse_root("{\"u_hex2\": \"0x5432\"}", &root));
    assert(root.u_hex2 == 0x5432);
    assert(json_parse_root("{\"u_hex2\": \"-0x5432\"}", &root));

    assert(!json_parse_root("{\"u_autonum\": \"05432\"}", &root));
    assert(root.u_autonum == 05432);

    assert(!json_parse_root("{\"u_autonum\": \"0x5432\"}", &root));
    assert(root.u_autonum == 0x5432);
    assert(json_parse_root("{\"u_autonum\": \"-0x5432\"}", &root));

    assert(!json_parse_root("{\"u_autonum\": \"5432\"}", &root));
    assert(root.u_autonum == 5432);

    /* Magic anyof case */
    assert(!json_parse_root("{\"anyof_hex\": \"123\"}", &root));
    assert(root.anyof_hex == 0x123);
    assert(!json_parse_root("{\"anyof_hex\": 5432}", &root));
    assert(root.anyof_hex == 5432);
    assert(json_parse_root("{\"anyof_hex\": \"12\"}", &root));
    assert(json_parse_root("{\"anyof_hex\": 122}", &root));
    assert(json_parse_root("{\"anyof_hex\": 1000001}", &root));
    assert(json_parse_root("{\"anyof_hex\": \"f4241\"}", &root));

    return 0;
}
