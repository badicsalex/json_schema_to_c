example: parser.h parser.o

parser.h parser.c: schema.json
	../json_schema_to_c.py schema.json --c-file parser.c --h-file parser.h

.PHONY: run
run: example
	./example data.json

.PHONY: clean
clean:
	rm -f parser.c parser.h parser.o main.o example
