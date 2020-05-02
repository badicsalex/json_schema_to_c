#include "parser.h"

#include <stdio.h>

char file_contents[10000] = {};

example_schema_t root = {};

int main(int argc, char** argv){
    if (argc<2){
        printf("Not enough arguments\n");
        return 3;
    }
    FILE* input_file = fopen(argv[1], "r");
    if (!input_file){
        printf("Failed to open file\n");
        return 1;
    }
    fread(file_contents, sizeof(file_contents)-1, 1, input_file);
    fclose(input_file);
    if (json_parse_example_schema(file_contents, &root)){
        printf("Parse failed\n");
        return 2;
    }
    printf("Some thing is %s\nSome other thing is %ld\n", root.fruits.items[2], root.multidimensionals.items[1].items[0].items[1]);
}
