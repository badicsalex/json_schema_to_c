.PHONY: all
.SILENT:
.PRECIOUS: %.parser.c %.parser.h %.compiled

CFLAGS= \
	-Wall \
	-Werror \
	-Wextra \
	-fsanitize=address \
	-g

ALL_COMPILE_TESTS = $(patsubst %.c,%.run,$(filter-out %.parser.c, $(wildcard */*.c)))
ALL_SCHEMA_ERROR_TESTS = $(patsubst %.json,%.run_scherr, $(wildcard schema_error/*.json))
PARSER_SOURCE_FILES = ../json_schema_to_c.py $(wildcard ../js2c/*.py) $(wildcard ../js2c/*/*.py) $(wildcard ../js2c/codegen/*.h) ../jsmn/jsmn.h

all: other/cpp.run $(ALL_COMPILE_TESTS) $(ALL_SCHEMA_ERROR_TESTS)
	@echo
	@echo "Tests successful."

schema_errors: $(ALL_SCHEMA_ERROR_TESTS)
	@echo "Schema error tests successful"

clean:
	rm -f */*.parser.c */*.parser.h */*.compiled */*.err

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

# === Schema error checking rules ===
%.run_scherr: %.json %.expected_err
	echo "$*: generating invalid schema"
	if ../json_schema_to_c.py $*.json $*.parser.c $*.parser.h 2>$*.err; then echo "Invalid schema was processed. That's a problem."; exit 1; fi
	if [ "`<$*.err`" != "`<$*.expected_err`" ]; then echo -e "Wrong error.\\n  Got error: `<$*.err`\\n   Expected: `<$*.expected_err`"; exit 1; fi
	@echo "$*: OK"
