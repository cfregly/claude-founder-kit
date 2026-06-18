# mvp/build operator commands. POSIX-make-friendly.
.DEFAULT_GOAL := help
.PHONY: help setup demo test check

help:
	@printf 'mvp/build\n\n'
	@printf '  make setup   Install the Python deps (one time)\n'
	@printf '  make demo    Measure the cost table live, ~36 real calls (needs ANTHROPIC_API_KEY)\n'
	@printf '  make test    Run the eval-set self-test\n'
	@printf '  make check   Run the doc-correctness gate\n'

setup:
	pip install -q -r requirements.txt

demo:
	@printf '== same workload, three ways, measured live (~36 real calls, needs ANTHROPIC_API_KEY) ==\n'
	python 04_cost_engineering.py

test:
	python eval_lint.py --selftest

check:
	python scripts/check_docs.py
