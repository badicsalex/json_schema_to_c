#include "invalid.parser.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>



int main(int argc, char** argv){
    (void)argc;
    (void)argv;
    root_t root = {};
    assert(!json_parse_root("{ \"name\": \"potato\", \"the_array\": [], \"is_good\": true}", &root));
    assert(!strcmp(root.name, "potato"));
    /* Mising "," after [] is accidentally handled correctly. */
    assert(!json_parse_root("{ \"name\": \"potato\", \"the_array\": [] \"is_good\": true}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(root.the_array.n == 0);
    assert(root.is_good);

    assert(!json_parse_root("{ \"the_array\": [] \"name\": \"potato\", \"is_good\": true}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(root.the_array.n == 0);
    assert(root.is_good);
    assert(!json_parse_root("{ \"the_array\": [0,1,2,3] \"name\": \"potato\", \"is_good\": true}", &root));
    assert(!strcmp(root.name, "potato"));
    assert(root.the_array.n == 4);
    assert(root.is_good);

    /* Missing "" */
    assert(json_parse_root("{ name: \"potato\", \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": potato, \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", the_array: [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [], is_good: true}", &root));

    /* missing comma */
    assert(json_parse_root("{ \"name\": \"potato\" \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [] 0, \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [0] 0, \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"is_good\": true \"the_array\": []}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"sub_ojb\": {} \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"sub_ojb\": {\"a\": 0} \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"sub_ojb\": {\"a\": 0} 0, \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"sub_ojb\": {\"a\": } 0, \"the_array\": [], \"is_good\": true}", &root));

    /* missing value */
    assert(json_parse_root("{ \"name\": , \"the_array\": [], \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": , \"is_good\": true}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"is_good\": ,\"the_array\": []}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [], \"subobj\":, \"is_good\": true}", &root));

    assert(json_parse_root("{ \"the_array\": [], \"is_good\": true, \"name\": }", &root));
    assert(json_parse_root("{ \"name\": \"potato\",  \"is_good\": true, \"the_array\":}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [], \"is_good\":}", &root));
    assert(json_parse_root("{ \"name\": \"potato\", \"the_array\": [], \"is_good\": true, \"subobj\":}", &root));

    return 0;
}
