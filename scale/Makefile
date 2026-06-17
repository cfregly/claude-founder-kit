.PHONY: help demo test check

help:
	@printf 'claude-startup-scale\n\n'
	@printf '  make demo   the deterministic moat readout from the sample cohort, offline\n'
	@printf '  make test   run the test suite\n'
	@printf '  make check  run the doc-correctness gate\n'

demo:
	python3 -m scale examples/cohort.json --json

test:
	python3 -m pytest tests/ -q

check:
	python3 scripts/check_docs.py
