.PHONY: check clean help pylint_check

help:
	@echo "This makefile does not have a default target."
	@echo "Supported targets: check, clean, help"
	@echo "You can also run 'make' in the example directory"

clean:
	$(MAKE) -C example clean
	$(MAKE) -C tests clean

check: pylint_check pep8_check
	$(MAKE) -C tests all

pylint_check:
	pylint js2c *.py

pep8_check:
	autopep8 -d *.py js2c/*.py --exit-code
