#include "any_of_const.parser.h"

#include <assert.h>

/* The classic tagged-union pattern: each option is an object with a `const` discriminator field. */
int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};

    /* The "kind" const picks the option; the const itself has no struct member. */
    assert(!json_parse_root("{\"shape\": {\"kind\": \"circle\", \"radius\": 5}}", &root));
    assert(root.shape.type == ROOT_SHAPE_CIRCLE);
    assert(root.shape.circle.radius == 5);

    assert(!json_parse_root("{\"shape\": {\"kind\": \"square\", \"side\": 3}}", &root));
    assert(root.shape.type == ROOT_SHAPE_SQUARE);
    assert(root.shape.square.side == 3);

    /* The discriminator need not come first. */
    assert(!json_parse_root("{\"shape\": {\"radius\": 7, \"kind\": \"circle\"}}", &root));
    assert(root.shape.type == ROOT_SHAPE_CIRCLE);
    assert(root.shape.circle.radius == 7);

    /* An unknown discriminator matches no option. */
    assert(json_parse_root("{\"shape\": {\"kind\": \"triangle\", \"radius\": 1}}", &root));

    return 0;
}
