#include "allow_additional.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{\"vegetable\": }";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root("{ \"name\": \"potato\", \"is_good\": true}", &root));
    assert(!json_parse_root("{ \"name\": \"potato\", \"is_good\": true, \"something\": \"else\"}", &root));
    assert(!json_parse_root("{\"something\": \"else\"}", &root));
    assert(!json_parse_root("{\"a\": [1, 2, [1, {\"a\":{\"b\": \"a\", \"c\": true}}],1], \"b\": {}}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(!json_parse_root("{\"a\": [1, 2, [1, {\"a\":{\"b\": \"a\", \"c\": true}}],1], \"name\": \"carrot\"}", &root));
    assert(!strcmp(root.name, "carrot"));
    assert(!json_parse_root("{\"a\": [1, 2, [1, {\"a\":{\"b\": \"a\", \"c\": true}}],1], \"b\": {}, \"name\": \"carrot\"}", &root));
    assert(!strcmp(root.name, "carrot"));
    assert(!json_parse_root("{\"a\": [1, 2, [1, {\"a\":{\"b\": \"a\", \"c\": true}}],1], \"name\": \"carrot\", \"b\": {}}", &root));
    assert(!strcmp(root.name, "carrot"));

    /* Too complex schemas should still cause an error. (additional properties param should be 20)
     * In the testcase, the key is one token, the array length is another, and the array elements are 18*/
    assert(json_parse_root(
        "{\
            \"name\": \"potato\", \
            \"is_good\": true, \
            \"x\": [1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9] \
        }",
        &root
    ));

    /* The token number calculator should still be precise. (additional properties param should be 20) */
    assert(!json_parse_root(
        "{\
            \"name\": \"potato\", \
            \"is_good\": true, \
            \"x\": [1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8] \
        }",
        &root
    ));
    assert(root.is_good);

    return 0;
}
