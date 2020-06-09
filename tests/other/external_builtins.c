#include "external_builtins.parser.h"

#include <assert.h>

int c_postfix_included();

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    assert(c_postfix_included());
    return 0;
}
