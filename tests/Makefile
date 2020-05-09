.PHONY: all
.SILENT:
.PRECIOUS: %.parser.c %.parser.h %.compiled

CFLAGS= \
	-Wall \
	-Werror \
	-Wextra \
	-g

ALL_TESTS =  $(patsubst %.c,%.run,$(filter-out %.parser.c, $(wildcard */*.c)))
PARSER_SOURCE_FILES = ../json_schema_to_c.py $(wildcard ../js2c/*.py) $(wildcard ../js2c/*/*.py) $(wildcard ../js2c/codegen/*.c) ../jsmn/jsmn.h

all: $(ALL_TESTS)
	@echo
	@echo "Tests successful."

clean:
	rm -f */*.parser.c */*.parser.h */*.compiled

# === Special test running and compilation rules ===

other/prefix_postfix.parser.c other/prefix_postfix.parser.h &: \
		other/prefix_postfix.schema.json $(PARSER_SOURCE_FILES) \
		other/h_prefix.inc other/h_postfix.inc other/c_prefix.inc other/c_postfix.inc
	echo "other/prefix_postfix: generating schema"
	../json_schema_to_c.py \
		--h-prefix other/h_prefix.inc \
		--h-postfix other/h_postfix.inc \
		--c-prefix other/c_prefix.inc \
		--c-postfix other/c_postfix.inc \
		other/prefix_postfix.schema.json other/prefix_postfix.parser.c other/prefix_postfix.parser.h

other/errors.parser.c other/errors.parser.h &: \
		other/errors.schema.json $(PARSER_SOURCE_FILES) \
		other/errors_c_prefix.inc other/errors_h_prefix.inc
	echo "other/errors: generating schema"
	../json_schema_to_c.py \
		--h-prefix other/errors_h_prefix.inc \
		--c-prefix other/errors_c_prefix.inc \
		other/errors.schema.json other/errors.parser.c other/errors.parser.h

other/max_tokens.parser.c other/max_tokens.parser.h &: \
		other/max_tokens.schema.json $(PARSER_SOURCE_FILES) \
		other/errors_c_prefix.inc other/errors_h_prefix.inc
	echo "other/max_tokens: generating schema"
	../json_schema_to_c.py \
		--h-prefix other/errors_h_prefix.inc \
		--c-prefix other/errors_c_prefix.inc \
		other/max_tokens.schema.json other/max_tokens.parser.c other/max_tokens.parser.h


# === General test running and compilation rules ===
%.parser.c %.parser.h: %.schema.json $(PARSER_SOURCE_FILES)
	echo "$*: generating schema"
	../json_schema_to_c.py $*.schema.json $*.parser.c $*.parser.h


%.compiled: %.c %.parser.c
	echo "$*: compiling $*"
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

%.run: %.compiled
	./$<
	@echo "$*: OK"

