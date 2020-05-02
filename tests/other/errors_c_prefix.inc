#include <stdio.h>

char last_error[10000];
int last_error_pos;

#define LOG_ERROR(position, ... ) \
    {\
        last_error_pos = position; \
        snprintf(last_error, sizeof(last_error), __VA_ARGS__); \
    }
