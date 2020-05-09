#include "max_tokens.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{ \
        \"things\": [ \
            { \"name\": \"a\", \"coordinate\": 5}, \
            { \"name\": \"b\", \"coordinate\": 6}, \
            { \"name\": \"c\", \"coordinate\": 7} \
        ], \
        \"is_good\": true \
    }";

const char* data2 = "{ \
        \"things\": [ \
            { \"name\": \"a\", \"coordinate\": 5}, \
            { \"name\": \"b\", \"coordinate\": 6}, \
            { \"name\": \"c\", \"coordinate\": 7} \
        ], \
        \"is_good\": true, \
        \"a\" ";

const char* data3 = "{ \
        \"things\": [ \
            { \"name\": \"a\", \"coordinate\": 5}, \
            { \"name\": \"b\", \"coordinate\": 6}, \
            { \"name\": \"c\", \"coordinate\": 7} \
        ], \
        \"is_good\": true ";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    check_error(
        data2,
        "JSON syntax error: JSON file too complex",
        200
    );
    check_error(
        data3,
        "JSON syntax error: End-of-file reached (JSON file incomplete)",
        191
    );
    return 0;
}
