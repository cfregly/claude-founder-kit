PY ?= python

.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'tool_tuning\n\n'
	@printf '  make demo    Print the pinned companion harness workflow\n'
	@printf '  make test    Run the recipe tests\n'
	@printf '  make check   Validate docs, pin, links, and compile the recipe\n'

demo:
	$(PY) tune_tools.py

test:
	$(PY) tests/test_recipe.py

check:
	$(PY) scripts/check_docs.py
	$(PY) -m compileall -q tune_tools.py scripts tests
