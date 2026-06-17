# claude-founder-kit: build a startup on Claude, idea to scale.
# Every demo makes a real Claude call. There is no offline mode.

MODULES := first_hour idea mvp launch scale quality cost
PY ?= python3

.PHONY: help setup demo test check \
        demo-first_hour demo-idea demo-mvp demo-launch demo-scale demo-quality demo-cost

help:
	@echo "claude-founder-kit"
	@echo "  make setup           install every stage's deps"
	@echo "  make demo            run the whole arc live (needs ANTHROPIC_API_KEY)"
	@echo "  make demo-<stage>    one stage: first_hour idea mvp launch scale quality cost"
	@echo "  make test            run every stage's tests"
	@echo "  make check           run every stage's gates"

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e quality

demo: demo-first_hour demo-idea demo-mvp demo-launch demo-scale demo-quality demo-cost
	@echo ""
	@echo "founder-kit: the whole arc ran live."

demo-first_hour:
	@echo "== first hour: one call up to a managed agent =="
	@cd first_hour && $(MAKE) demo

demo-idea:
	@echo "== idea: validate the signal, lint the raise =="
	@cd idea && $(MAKE) demo

demo-mvp:
	@echo "== mvp: prompt to production, then review the tools =="
	@cd mvp && $(MAKE) demo

demo-launch:
	@echo "== launch: measure activation, gate the motion =="
	@cd launch && $(MAKE) demo

demo-scale:
	@echo "== scale: the data moat and the next motion =="
	@cd scale && $(MAKE) demo

demo-quality:
	@echo "== quality: the de-slop linter =="
	@cd quality && $(MAKE) demo

demo-cost:
	@echo "== cost: the platform cost levers =="
	@cd cost && $(PY) run.py

test:
	@for m in $(MODULES); do \
	  if [ -f $$m/Makefile ] && grep -q '^test:' $$m/Makefile; then \
	    echo "== test: $$m =="; (cd $$m && $(MAKE) test) || exit 1; \
	  fi; \
	done

check:
	@for m in $(MODULES); do \
	  if [ -f $$m/Makefile ] && grep -q '^check:' $$m/Makefile; then \
	    echo "== check: $$m =="; (cd $$m && $(MAKE) check) || exit 1; \
	  fi; \
	done
