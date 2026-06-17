# claude-startup-idea / validate operator commands. POSIX-make-friendly.
.DEFAULT_GOAL := help
.PHONY: help demo test check

help:
	@printf 'claude-startup-idea / validate\n\n'
	@printf '  make demo    Score a strong pitch (8/10) then a weaker one, offline, no API key\n'
	@printf '  make test    Run the test suite\n'
	@printf '  make check   Run the doc-correctness gate\n'

demo:
	@printf '== a strong pitch ==\n'
	python -m startup_signal_lab.score examples/strong_pitch.md
	@printf '\n== a weaker pitch for contrast ==\n'
	python -m startup_signal_lab.score examples/sample_pitch.md

test:
	python -m pytest tests/ -q

check:
	python scripts/check_docs.py
