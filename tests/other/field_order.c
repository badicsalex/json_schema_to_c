#include "field_order.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stddef.h>

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    assert(offsetof(root_t, desc1) < offsetof(root_t, desc2));
    assert(offsetof(root_t, desc2) < offsetof(root_t, desc3));
    assert(offsetof(root_t, desc3) < offsetof(root_t, subobj));
    assert(offsetof(root_t, subobj) < offsetof(root_t, desc4));
    assert(offsetof(root_t, desc4) < offsetof(root_t, desc5));
    assert(offsetof(root_subobj_t, a) < offsetof(root_subobj_t, b));
    assert(offsetof(root_subobj_t, b) < offsetof(root_subobj_t, c));
    return 0;
}
