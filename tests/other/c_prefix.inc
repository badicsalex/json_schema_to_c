#ifndef H_PREFIX_INCLUDED
#error Ayaya, C before H???
#endif

#ifndef H_POSTFIX_INCLUDED
#error Ayaya, C before H, but worse??
#endif

int c_prefix_included(){
    return 1;
}
#define C_PREFIX_INCLUDED
