#include <stdlib.h> 
#include <byteswap.h>

bool big_endian_hex(const char* src, int size, uint64_t* out, const char** error){
    char * end_char = NULL;
    *out = bswap_64(strtoull(src, &end_char, 16));
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

