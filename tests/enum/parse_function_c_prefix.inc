#include <string.h>

/* Only labels reach this (the generator validates first), so unknowns need no handling. */
bool parse_color(const char* src, int size, int* out, const char** error){
    (void)error;
    if (size == 3 && !strncmp(src, "red", 3))   { *out = 0xFF0000; return false; }
    if (size == 5 && !strncmp(src, "green", 5)) { *out = 0x00FF00; return false; }
    if (size == 4 && !strncmp(src, "blue", 4))  { *out = 0x0000FF; return false; }
    return true;
}
