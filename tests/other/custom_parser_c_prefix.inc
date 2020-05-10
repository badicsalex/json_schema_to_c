#include <stdlib.h> 

bool hex_parser(const char* src, int size, int64_t* out, const char** error){
    char * end_char = NULL;
    *out = strtoll(src, &end_char, 16);
    if (end_char != (src + size)){
        *error = "Invalid int literal";
        return true;
    }
    return false;
}

bool pt_prsr(const char* src, int size, custom_point_t* pt, const char** error){
    (void)error;
    if (size != 2){
        return true;
    }
    pt->x = src[0];
    pt->y = src[1];
    return false;
}
