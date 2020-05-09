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
#include "../../jsmn/jsmn.h"
#endif

#ifndef LOG_ERROR
#define LOG_ERROR(position, ...)
#endif

typedef struct parse_state_s {
    const char* json_string;
    jsmntok_t tokens[1024];
    uint64_t current_token;
} parse_state_t;

#define CURRENT_TOKEN(parse_state) ((parse_state)->tokens[(parse_state)->current_token])
#define CURRENT_STRING_LENGTH(parse_state) (CURRENT_TOKEN(parse_state).end - CURRENT_TOKEN(parse_state).start)
#define CURRENT_STRING_FOR_ERROR(parse_state) CURRENT_STRING_LENGTH(parse_state), ((parse_state)->json_string + CURRENT_TOKEN(parse_state).start)

static inline const char* token_type_as_string(jsmntype_t type){
    switch(type){
        case JSMN_UNDEFINED: return "UNDEFINED";
        case JSMN_OBJECT: return "OBJECT";
        case JSMN_ARRAY: return "ARRAY";
        case JSMN_STRING: return "STRING";
        case JSMN_PRIMITIVE: return "PRIMITIVE";
        default: return "UNKNOWN";
    }
}

static inline const char* jsmn_error_as_string(int err){
    switch(err){
        case JSMN_ERROR_INVAL: return "Invalid character";
        case JSMN_ERROR_NOMEM: return "JSON file too complex";
        case JSMN_ERROR_PART: return "End-of-file reached (JSON file incomplete)";
        default: return "Internal error";
    }
}

static inline bool check_type(const parse_state_t* parse_state, jsmntype_t type){
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    if (token->type != type){
        LOG_ERROR(
            token->start,
            "Unexpected token: %s instead of %s",
            token_type_as_string(token->type),
            token_type_as_string(type)
        )
        return true;
    }
    return false;
}

static inline bool current_string_is(const parse_state_t* parse_state, const char *s) {
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    return 
        (token->type == JSMN_STRING) &&
        (strlen(s) == (size_t)(token->end - token->start)) &&
        (memcmp(parse_state->json_string + token->start, s, token->end - token->start) == 0);
}

static inline bool builtin_parse_string(parse_state_t* parse_state, char *out, int min_len, int max_len){
    if (check_type(parse_state, JSMN_STRING)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    if (token->end - token->start > max_len){
        LOG_ERROR(token->start, "String too large. Length: %i. Maximum length: %i.", token->end - token->start, max_len);
        return true;
    }
    if (token->end - token->start < min_len){
        LOG_ERROR(token->start, "String too short. Length: %i. Minimum length: %i.", token->end - token->start, min_len);
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
        LOG_ERROR(token->start, "Invalid boolean literal: %.*s", CURRENT_STRING_FOR_ERROR(parse_state));
        return true;
    }
    *out = first_char == 't';
    parse_state->current_token += 1;
    return false;
}

static inline bool builtin_parse_signed(parse_state_t* parse_state, int64_t *out){
    if (check_type(parse_state, JSMN_PRIMITIVE)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    char * end_char = NULL;
    *out = strtoll(parse_state->json_string + token->start, &end_char, 10);
    if (end_char != parse_state->json_string + token->end){
        LOG_ERROR(token->start, "Invalid signed integer literal: %.*s", CURRENT_STRING_FOR_ERROR(parse_state));
        return true;
    }
    parse_state->current_token += 1;
    return false;
}

static inline bool builtin_parse_unsigned(parse_state_t* parse_state, uint64_t *out){
    if (check_type(parse_state, JSMN_PRIMITIVE)){
        return true;
    }
    const jsmntok_t* token = &parse_state->tokens[parse_state->current_token];
    const char * start_char = parse_state->json_string + token->start;
    char * end_char = NULL;
    if (*start_char > '9' || *start_char < '0'){
        LOG_ERROR(token->start, "Invalid unsigned integer literal: %.*s", CURRENT_STRING_FOR_ERROR(parse_state));
        return true;
    }
    *out = strtoull(start_char, &end_char, 10);
    if (end_char != parse_state->json_string + token->end){
        LOG_ERROR(token->start, "Invalid unsigned integer literal: %.*s", CURRENT_STRING_FOR_ERROR(parse_state));
        return true;
    }
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
        LOG_ERROR(parser.pos, "JSON syntax error: %s", jsmn_error_as_string(token_num));
        return true;
    }
    return false;
}
