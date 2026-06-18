# idea/validate operator commands. POSIX-make-friendly.
.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'idea/validate\n\n'
	@printf '  make demo    Score a strong pitch (8/10), then write the live intervention (needs ANTHROPIC_API_KEY)\n'
	@printf '  make test    Run the test suite\n'
	@printf '  make check   Run the doc-correctness gate\n'

demo:
	@printf '== signal score: a strong pitch (deterministic) ==\n'
	python -m startup_signal_lab.score examples/strong_pitch.md
	@printf '\n== the live founder intervention (needs ANTHROPIC_API_KEY) ==\n'
	python -m startup_signal_lab.intervene examples/strong_pitch.md

test:
	python -m pytest tests/ -q

check:
	python scripts/check_docs.py
