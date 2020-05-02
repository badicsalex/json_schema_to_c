#ifndef H_PREFIX_INCLUDED
#error Ayaya, C before H???
#endif

#ifndef H_POSTFIX_INCLUDED
#error Ayaya, C before H, but worse??
#endif

#ifndef C_PREFIX_INCLUDED
#error Ayaya, no prefix?
#endif

int c_postfix_included(){
    return 1;
}
