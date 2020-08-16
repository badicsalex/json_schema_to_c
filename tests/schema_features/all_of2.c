#include "all_of2.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{"
    "\"good_veggie\": {"
        "\"weight\": {"
            "\"max\": 15"
        "}"
    "}"
"}";

void check_veggie(veggie_t *v, veggie_quality_t quality, int min_weight, int max_weight){
    assert(v->quality == quality);
    assert(v->weight.min == min_weight);
    assert(v->weight.max == max_weight);
}

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    /* The main point here is that both veggies are the same type */
    check_veggie(&root.good_veggie, VEGGIE_QUALITY_GOOD, 0, 15);
    check_veggie(&root.ok_veggie, VEGGIE_QUALITY_OK, 0, 5);
    return 0;
}
