PY ?= python

.DEFAULT_GOAL := help
.PHONY: help demo check test

help:
	@printf 'day0: trust controls before the first live user\n\n'
	@printf '  make demo   Run the deterministic trust receipt\n'
	@printf '  make check  Validate docs, templates, and control coverage\n'
	@printf '  make test   Run the trust harness tests\n'

demo:
	$(PY) demo.py

check:
	$(PY) scripts/check_docs.py

test:
	$(PY) -m unittest discover -s tests -q
