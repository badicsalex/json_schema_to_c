.PHONY: all
.SILENT:
.PRECIOUS: %.parser.c %.parser.h %.compiled

CFLAGS= \
	-Wall \
	-Werror \
	-g

ALL_TESTS =  $(patsubst %.c,%.run,$(filter-out %.parser.c, $(wildcard */*.c)))
PARSER_SOURCE_FILES = ../json_schema_to_c.py $(wildcard ../js2c/*.py) $(wildcard ../js2c/*.c) ../jsmn/jsmn.h

all: $(ALL_TESTS)
	@echo
	@echo "Tests successful."

clean:
	rm -f */*.parser.c */*.parser.h */*.compiled

%.parser.c %.parser.h: %.schema.json $(PARSER_SOURCE_FILES)
	echo "$*: generating schema"
	../json_schema_to_c.py $*.schema.json $*.parser.c $*.parser.h


%.compiled: %.c %.parser.c
	echo "$*: compiling $*"
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

%.run: %.compiled
	./$<
	@echo "$*: OK"

