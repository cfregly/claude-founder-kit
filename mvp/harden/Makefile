# mvp/harden operator commands. POSIX-make-friendly.
PY ?= python

.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'mvp/harden\n\n'
	@printf '  make demo    Before and after: a vague server (14) then the contract-grade rewrite (100)\n'
	@printf '  make test    Run the rule test suite\n'
	@printf '  make check   Run the doc-correctness and rule-count gate\n'

demo:
	@printf '== before: five tools the model has to guess at, with the live Claude rewrite ==\n'
	-$(PY) -m contract_doctor examples/vague_tools.json --judge
	@printf '\n== after: the same five tools rewritten as contracts ==\n'
	$(PY) -m contract_doctor examples/contract_grade_tools.json --judge

test:
	$(PY) tests/test_rules.py

check:
	$(PY) scripts/check_docs.py
