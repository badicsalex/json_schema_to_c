#ifndef JSON_SCHEMA_TO_C_H_
#define JSON_SCHEMA_TO_C_H_
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "jsmn/jsmn.h"

typedef struct parse_state_s {
    const char* json_string;
    jsmntok_t tokens[1024];
    uint64_t current_token;
} parse_state_t;

static bool check_type(const parse_state_t* parse_state, jsmntype_t type){
    /* TODO errorlog */
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    return token->type != type;
}

static bool current_string_is(const parse_state_t* parse_state, const char *s) {
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    return 
        (token->type == JSMN_STRING) &&
        (strlen(s) == token->end - token->start) &&
        (strncmp(parse_state->json_string + token->start, s, token->end - token->start) == 0);
}

static bool builtin_parse_string(parse_state_t* parse_state, char *out, uint64_t max_len){
    if (check_type(parse_state, JSMN_STRING)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    if (token->end - token->start > max_len){
        /* TODO errorlog */
        return true;
    }
    memcpy(out, parse_state->json_string + token->start, token->end - token->start);
    out[token->end - token->start] = 0;
    parse_state->current_token += 1;
    return false;
}

static bool builtin_parse_bool(parse_state_t* parse_state, bool *out){
    if (check_type(parse_state, JSMN_PRIMITIVE)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    const char first_char = parse_state->json_string[token->start];
    if (first_char != 't' && first_char != 'f'){
        /* TODO errorlog */
        return true;
    }
    *out = first_char == 't';
    parse_state->current_token += 1;
    return false;
}

static bool builtin_parse_number(parse_state_t* parse_state, int64_t *out){
    if (check_type(parse_state, JSMN_PRIMITIVE)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    const char first_char = parse_state->json_string[token->start];
    if (first_char != '-' && !(first_char >= '0' && first_char <= '9')){
        /* TODO errorlog */
        return true;
    }
    *out = atoi(parse_state->json_string + token->start);
    parse_state->current_token += 1;
    return false;
}

static bool builtin_parse_json_string(parse_state_t* parse_state, const char* json_string){
    jsmn_parser parser;
    parse_state->json_string = json_string;
    parse_state->current_token = 0;

    jsmn_init(&parser);
    int token_num = jsmn_parse(
        &parser,
        json_string,
        strlen(json_string),
        parse_state->tokens,
        sizeof(parse_state->tokens) / sizeof(parse_state->tokens[0])
    );
    if (token_num < 0) {
        /* TODO errorlog */
        return true;
    }
    return false;
}

#endif // JSON_SCHEMA_TO_C_H_
