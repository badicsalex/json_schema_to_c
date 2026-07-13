#include "all_of_range.parser.h"

#include <string.h>
#include <assert.h>


const char* data = "{"
    "\"merged_int\": 30,"
    "\"merged_str\": \"hello\","
    "\"merged_arr\": [1, 2, 3]"
"}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    /* Merged bounds are int [10, 50], string [4, 8], array [2, 4]. */
    assert(root.merged_int == 30);
    assert(!strcmp(root.merged_str, "hello"));
    assert(root.merged_arr.n == 3);
    assert(root.merged_arr.items[0] == 1);
    assert(root.merged_arr.items[2] == 3);
    return 0;
}
