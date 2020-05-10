#include <stdio.h>
#include <string.h>
#include <assert.h>

char last_error[10000];
int last_error_pos;

#define LOG_ERROR(position, ... ) \
    {\
        last_error_pos = position; \
        snprintf(last_error, sizeof(last_error), __VA_ARGS__); \
    }

void check_error(const char* json, const char* expected_str, int expected_pos){
    root_t root = {};
    assert(json_parse_root(json, &root));
    if (strcmp(last_error, expected_str)){
        fprintf(stderr, "When checking %s\n", json);
        fprintf(stderr, "Last error: %s\n", last_error);
        fprintf(stderr, "Expected  : %s\n", expected_str);
        assert(false);
    }
    if (expected_pos != -1 && expected_pos != last_error_pos){
        fprintf(stderr, "When checking %s\n", json);
        fprintf(stderr, "Last error pos: %i\n", last_error_pos);
        fprintf(stderr, "Expected   pos: %i\n", expected_pos);
        assert(false);
    }
}

bool error_creating_parser(const char* src, int size, int* out, const char** error){
    (void)src;
    if (size == 1) {
        *out = 0;
        return false;
    }
    if (size == 2) {
        *error = "Custom error";
    }
    return true;
}
