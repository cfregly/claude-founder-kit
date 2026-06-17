# claude-startup-idea operator commands. The Idea stage of Anthropic's Founder's
# Playbook: validate the idea before you build, and pressure-test the raise.
# Each target runs both sub-tools from inside their own subdir, so each keeps
# its own gate, tests, and demo unchanged.
.DEFAULT_GOAL := help
.PHONY: help check test demo

help:
	@printf 'claude-startup-idea: the Idea stage\n\n'
	@printf '  make check   Run both sub-tools doc-correctness gates\n'
	@printf '  make test    Run both sub-tools test suites\n'
	@printf '  make demo    Run each sub-tools demo\n\n'
	@printf '  validate/  scores the startup signal and argues against the idea\n'
	@printf '  raise/     builds and lints the pitch on the Sequoia arc\n'

check:
	(cd validate && make check) && (cd raise && make check)

test:
	(cd validate && make test) && (cd raise && make test)

demo:
	(cd validate && make demo) && (cd raise && make demo)
