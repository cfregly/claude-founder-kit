# idea operator commands. The Idea stage of Anthropic's Founder's
# Playbook: validate the idea before you build, and pressure-test the raise.
# Each target runs both sub-tools from inside their own subdir, so each keeps
# its own gate, tests, and demo unchanged.
PY ?= python
ifneq ($(findstring /,$(PY)),)
PY_RUN := $(abspath $(PY))
else
PY_RUN := $(PY)
endif

.DEFAULT_GOAL := help
.PHONY: help check test demo

help:
	@printf 'idea: the Idea stage\n\n'
	@printf '  make check   Run both sub-tools doc-correctness gates\n'
	@printf '  make test    Run both sub-tools test suites\n'
	@printf '  make demo    Run each sub-tools demo\n\n'
	@printf '  validate/  scores the startup signal and argues against the idea\n'
	@printf '  raise/     builds and lints the pitch on the Sequoia arc\n'

check:
	(cd validate && $(MAKE) PY="$(PY_RUN)" check) && (cd raise && $(MAKE) PY="$(PY_RUN)" check)

test:
	(cd validate && $(MAKE) PY="$(PY_RUN)" test) && (cd raise && $(MAKE) PY="$(PY_RUN)" test)

demo:
	(cd validate && $(MAKE) PY="$(PY_RUN)" demo) && (cd raise && $(MAKE) PY="$(PY_RUN)" demo)
