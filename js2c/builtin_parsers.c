/*
 * MIT License
 *
 * Copyright (c) 2020 Alex Badics
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Hack to let the IDE know that we need JSMN.
 * In a normal situation, it will be included or pasted before this file. */
#ifndef JSMN_H
#error "jsmn.h not included"
#include "../jsmn/jsmn.h"
#endif

typedef struct parse_state_s {
    const char* json_string;
    jsmntok_t tokens[1024];
    uint64_t current_token;
} parse_state_t;

static inline bool check_type(const parse_state_t* parse_state, jsmntype_t type){
    /* TODO errorlog */
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    return token->type != type;
}

static inline bool current_string_is(const parse_state_t* parse_state, const char *s) {
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    return 
        (token->type == JSMN_STRING) &&
        (strlen(s) == token->end - token->start) &&
        (strncmp(parse_state->json_string + token->start, s, token->end - token->start) == 0);
}

static inline bool builtin_parse_string(parse_state_t* parse_state, char *out, uint64_t max_len){
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

static inline bool builtin_parse_bool(parse_state_t* parse_state, bool *out){
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

static inline bool builtin_parse_number(parse_state_t* parse_state, int64_t *out){
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

static inline bool builtin_parse_json_string(parse_state_t* parse_state, const char* json_string){
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
