# quality operator commands. POSIX-make-friendly.
PY ?= python

.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'quality\n\n'
	@printf '  make demo    Before and after: a sloppy doc (F) then clean prose (A)\n'
	@printf '  make test    Run the rule test suite\n'
	@printf '  make check   Run the doc-correctness gate and self-deslop the README\n'

demo:
	@printf '== before: a sloppy doc, with the live Claude judge ==\n'
	-$(PY) -m deslop examples/sloppy.md --judge
	@printf '\n== after: clean prose ==\n'
	$(PY) -m deslop examples/clean.md --judge

test:
	$(PY) tests/test_rules.py

check:
	$(PY) scripts/check_docs.py
	$(PY) -m deslop README.md
