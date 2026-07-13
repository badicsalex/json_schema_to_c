#include <stdio.h>
#include <string.h>

char last_error[1000];

#define LOG_ERROR(position, ...) { snprintf(last_error, sizeof(last_error), __VA_ARGS__); }
