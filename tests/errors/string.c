#include "string.parser.h"

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    check_error(
        "{\"name\": true}",
        "Unexpected token in 'name': PRIMITIVE instead of STRING",
        9
    );
    check_error(
        "{\"name\": \"n>8 here.\"}",
        "String too large in 'name'. Length: 9. Maximum length: 8.",
        10
    );
    check_error(
        "{\"name\": \" <4\"}",
        "String too short in 'name'. Length: 3. Minimum length: 4.",
        10
    );
    return 0;
}
