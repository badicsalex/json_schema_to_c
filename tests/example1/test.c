#include "parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>

root_t root = {};

const char* data = " \
    {                                                     \
        \"fruits\": [\"apple\", \"pear\", \"strawberry\"],\
        \"vegetables\": [                                 \
            {                                             \
                \"name\": \"carrot\",                     \
                \"is_good\": false                        \
            },                                            \
            {                                             \
                \"name\": \"potato\",                     \
                \"is_good\": true                         \
            }                                             \
        ],                                                \
        \"multidimensionals\":[                           \
            [                                             \
                [1,2,3,4],                                \
                [5,6,7,8]                                 \
            ],                                            \
            [                                             \
                [11,12,13,14],                            \
                [25,26,27,28]                             \
            ]                                             \
        ]                                                 \
    }                                                     \
";

int main(int argc, char** argv){
    if (parse(data, &root)){
        printf("Parse failed\n");
        return 2;
    }
    assert(!strcmp( root.fruits.items[2], "strawberry"));
    assert(root.multidimensionals.items[1].items[0].items[1] == 12);
    return 0;
}
