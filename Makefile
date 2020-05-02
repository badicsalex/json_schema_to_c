.PHONY: check clean help

help:
	@echo "This makefile does not have a default target."
	@echo "Supported targets: check, clean, help"
	@echo "You can also run 'make' in the example directory"

clean:
	$(MAKE) -C example clean
	$(MAKE) -C tests clean

check:
	$(MAKE) -C tests all
