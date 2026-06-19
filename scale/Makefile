PY ?= python

.PHONY: help demo test check

help:
	@printf 'scale\n\n'
	@printf '  make demo   the live moat readout and GTM motion (needs ANTHROPIC_API_KEY)\n'
	@printf '  make test   run the test suite\n'
	@printf '  make check  run the doc-correctness gate\n'

demo:
	$(PY) -m scale examples/cohort.json

test:
	$(PY) -m pytest tests/ -q

check:
	$(PY) scripts/check_docs.py
