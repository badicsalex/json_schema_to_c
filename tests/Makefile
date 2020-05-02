.PHONY: all
.SILENT:
.PRECIOUS: %.parser.c %.parser.h %.compiled

CFLAGS= \
	-Wall \
	-Werror \
	-I ../jsmn \
	-I .. \
	-I .

ALL_TESTS =  $(patsubst %.c,%.run,$(filter-out %.parser.c, $(wildcard */*.c)))
PARSER_PY_FILES = ../json_schema_to_c.py $(wildcard ../js2c/*.py)

all: $(ALL_TESTS)
	@echo
	@echo "Tests successful."

clean:
	rm -f */*.parser.c */*.parser.h */*.compiled

%.parser.c %.parser.h: %.schema.json $(PARSER_PY_FILES)
	echo "$*: generating schema"
	../json_schema_to_c.py $*.schema.json $*.parser.c $*.parser.h


%.compiled: %.c %.parser.c ../json_schema_to_c.h
	echo "$*: compiling $*"
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

%.run: %.compiled
	./$<
	@echo "$*: OK"

