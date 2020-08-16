#include "type_names.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>


const char* data = "{\"vegetable\": { \"name\": \"potato\", \"is_good\": true, \"origin\": \"EU\"}}";

int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root(data, &root));
    vegetable_t vegetable = root.vegetable;
    name_t name;
    memcpy(name, vegetable.name, sizeof(name));
    assert(!strcmp(name, "potato"));
    my_report_name_type report_name;
    memcpy(report_name, root.report_name, sizeof(report_name));
    assert(!strcmp(report_name, "unnamed report"));

    vegetable_origin_t origin = vegetable.origin;
    assert(origin == VEGETABLE_ORIGIN_EU);
    return 0;
}
