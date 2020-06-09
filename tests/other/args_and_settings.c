#include "prefix_postfix.parser.h"

#include <stdio.h>
#include <assert.h>

#ifndef H_PREFIX_INCLUDED
#error H prefix was not included in .h
#endif

#ifndef H_POSTFIX_INCLUDED
#error H postfix was not included in .h
#endif

#ifdef C_PREFIX_INCLUDED
#error C prefix was included in .h
#endif

#ifdef C_POSTFIX_INCLUDED
#error C postfix was included in .h
#endif

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    assert(c_prefix_included());
    assert(c_postfix_included());
    return 0;
}
