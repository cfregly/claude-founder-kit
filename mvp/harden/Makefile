# claude-startup-mvp / harden operator commands. POSIX-make-friendly.
.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'claude-startup-mvp / harden\n\n'
	@printf '  make demo    Before and after: a vague server (14) then the contract-grade rewrite (100)\n'
	@printf '  make test    Run the rule test suite\n'
	@printf '  make check   Run the doc-correctness and rule-count gate\n'

demo:
	@printf '== before: five tools the model has to guess at ==\n'
	-python -m contract_doctor examples/vague_tools.json
	@printf '\n== after: the same five tools rewritten as contracts ==\n'
	python -m contract_doctor examples/contract_grade_tools.json

test:
	python tests/test_rules.py

check:
	python scripts/check_docs.py
