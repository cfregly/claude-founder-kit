PY ?= python
RECEIPT_ARGS := $(if $(RECEIPT),--receipt $(RECEIPT),)

.DEFAULT_GOAL := help
.PHONY: help demo json check test

help:
	@printf 'pilot check: programmatic tool calling receipt check before the first pilot customer\n\n'
	@printf '  make demo   Run the readable deterministic programmatic tool calling pilot check\n'
	@printf '  make demo RECEIPT=/tmp/programmatic_tool_calling_receipt.json   Check a live programmatic tool calling receipt\n'
	@printf '  make json   Print the full machine-readable pilot-check result\n'
	@printf '  make check  Validate docs, templates, and control coverage\n'
	@printf '  make test   Run the pilot-check tests\n'

demo:
	$(PY) demo.py $(RECEIPT_ARGS)

json:
	$(PY) demo.py $(RECEIPT_ARGS) --json

check:
	$(PY) scripts/check_docs.py

test:
	$(PY) -m unittest discover -s tests -q
