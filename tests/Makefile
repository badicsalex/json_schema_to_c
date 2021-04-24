.PHONY: all
.SILENT:
.PRECIOUS: %.parser.c %.parser.h %.compiled

CFLAGS= \
	-Wall \
	-Werror \
	-Wextra \
	-fsanitize=address \
	-g

ALL_TESTS =  other/cpp.run $(patsubst %.c,%.run,$(filter-out %.parser.c, $(wildcard */*.c)))
PARSER_SOURCE_FILES = ../json_schema_to_c.py $(wildcard ../js2c/*.py) $(wildcard ../js2c/*/*.py) $(wildcard ../js2c/codegen/*.h) ../jsmn/jsmn.h

all: $(ALL_TESTS)
	@echo
	@echo "Tests successful."

clean:
	rm -f */*.parser.c */*.parser.h */*.compiled

# === Special test running and compilation rules ===

other/args_and_settings.parser.c other/args_and_settings.parser.h &: \
		other/args_and_settings.schema.json $(PARSER_SOURCE_FILES) \
		other/c_postfix.inc
	echo "other/args_and_settings: generating schema"
	../json_schema_to_c.py \
		--c-prefix /dev/null \
		--c-postfix other/c_postfix.inc \
		other/args_and_settings.schema.json other/args_and_settings.parser.c other/args_and_settings.parser.h

other/cpp.o: other/cpp.cpp other/cpp.parser.h

other/cpp.compiled: other/cpp.o other/cpp.parser.c
	echo "other/cpp: compiling and linking"
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@


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

