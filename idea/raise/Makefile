# idea/raise operator commands. POSIX-make-friendly.
PY ?= python

.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'idea/raise\n\n'
	@printf '  make demo    Before and after: a sloppy deck (0) then the sharp rewrite (100)\n'
	@printf '  make test    Run the rule test suite\n'
	@printf '  make check   Run the doc-correctness gate\n'

demo:
	@printf '== before: a sloppy draft, with the live Claude narrative read ==\n'
	-$(PY) -m pitch_lint examples/sloppy_deck.json --judge
	@printf '\n== after: the same company, rewritten on the arc ==\n'
	$(PY) -m pitch_lint examples/sharp_deck.json --judge

test:
	$(PY) tests/test_rules.py

check:
	$(PY) scripts/check_docs.py
