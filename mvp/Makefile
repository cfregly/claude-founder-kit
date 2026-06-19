# mvp operator commands. POSIX-make-friendly.
# Two co-located sub-tools, each with its own package, tests, and gate:
#   build/   the path from a first Claude call to a deployable agent
#   harden/  the security review of the MCP and agent surface
# Each target fans out into both subdirs. A subdir failing fails the whole target.
PY ?= python
ifneq ($(findstring /,$(PY)),)
PY_RUN := $(abspath $(PY))
else
PY_RUN := $(PY)
endif

.DEFAULT_GOAL := help
.PHONY: help setup demo test check

help:
	@printf 'mvp: build the product, then a security review before any user\n\n'
	@printf '  make setup   Install build/ deps (one time, for the live acts)\n'
	@printf '  make demo    Run both demos: the cost receipt, then the before/after lint\n'
	@printf '  make test    Run both test suites: the eval-set self-test and the rule suite\n'
	@printf '  make check   Run both deterministic gates: the doc-correctness checks\n'

setup:
	cd build && $(MAKE) PY="$(PY_RUN)" setup

demo:
	@printf '== build: the cost receipt, measured live (needs ANTHROPIC_API_KEY) ==\n'
	cd build && $(MAKE) PY="$(PY_RUN)" demo
	@printf '\n== harden: a vague server (14) then the contract-grade rewrite (100) ==\n'
	cd harden && $(MAKE) PY="$(PY_RUN)" demo

test:
	cd build && $(MAKE) PY="$(PY_RUN)" test
	cd harden && $(MAKE) PY="$(PY_RUN)" test

check:
	cd build && $(MAKE) PY="$(PY_RUN)" check
	cd harden && $(MAKE) PY="$(PY_RUN)" check
