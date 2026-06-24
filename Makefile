# claude-founder-kit: build a startup on Claude, idea to scale.
# The top-level demo is live. Checks and tests stay deterministic and keyless.

MODULES := first_hour idea mvp launch scale quality cost
PY ?= python
ifneq ($(findstring /,$(PY)),)
PY_RUN := $(abspath $(PY))
else
PY_RUN := $(PY)
endif

.PHONY: help setup demo test check \
        demo-first_hour demo-idea demo-mvp demo-launch demo-scale demo-quality demo-cost

help:
	@echo "claude-founder-kit"
	@echo "  make setup           install every stage's deps"
	@echo "  make demo            run the live walkthrough (needs ANTHROPIC_API_KEY)"
	@echo "  make demo-<stage>    one stage: first_hour idea mvp launch scale quality cost"
	@echo "  make test            run every stage's tests"
	@echo "  make check           run every stage's gates"

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e quality

demo: demo-first_hour demo-idea demo-mvp demo-launch demo-scale demo-quality demo-cost
	@echo ""
	@echo "founder-kit: live walkthrough completed."

demo-first_hour:
	@echo "== first hour: one call up to a managed agent =="
	@cd first_hour && $(MAKE) PY="$(PY_RUN)" demo

demo-idea:
	@echo "== idea: validate the signal, lint the raise =="
	@cd idea && $(MAKE) PY="$(PY_RUN)" demo

demo-mvp:
	@echo "== mvp: prompt to production, then review the tools =="
	@cd mvp && $(MAKE) PY="$(PY_RUN)" demo

demo-launch:
	@echo "== launch: measure activation, gate the motion =="
	@cd launch && $(MAKE) PY="$(PY_RUN)" demo

demo-scale:
	@echo "== scale: the data moat and the next motion =="
	@cd scale && $(MAKE) PY="$(PY_RUN)" demo

demo-quality:
	@echo "== quality: the de-slop linter =="
	@cd quality && $(MAKE) PY="$(PY_RUN)" demo

demo-cost:
	@echo "== cost: the platform cost levers =="
	@cd cost && $(PY_RUN) run.py

test:
	@for m in $(MODULES); do \
	  if [ -f $$m/Makefile ] && grep -q '^test:' $$m/Makefile; then \
	    echo "== test: $$m =="; (cd $$m && $(MAKE) PY="$(PY_RUN)" test) || exit 1; \
	  fi; \
	done

check:
	@for m in $(MODULES); do \
	  if [ -f $$m/Makefile ] && grep -q '^check:' $$m/Makefile; then \
	    echo "== check: $$m =="; (cd $$m && $(MAKE) PY="$(PY_RUN)" check) || exit 1; \
	  fi; \
	done
