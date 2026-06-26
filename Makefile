# claude-founder-kit: build a startup on Claude, idea to scale.
# The top-level demo is live. Checks and tests stay deterministic and keyless.

MODULES := day0 first_hour idea mvp tool_tuning launch scale quality cost
PY ?= python
ifneq ($(findstring /,$(PY)),)
PY_RUN := $(abspath $(PY))
else
PY_RUN := $(PY)
endif

.PHONY: help setup demo test check adversarial tune-tools companions companion check-companions day0 \
        demo-day0 demo-first_hour demo-idea demo-mvp demo-tool_tuning demo-launch demo-scale demo-quality demo-cost

help:
	@echo "claude-founder-kit"
	@echo "  make setup           install every stage's deps"
	@echo "  make demo            run the live walkthrough (needs ANTHROPIC_API_KEY)"
	@echo "  make day0            run the keyless day-0 trust receipt"
	@echo "  make demo-<stage>    one stage: day0 first_hour idea mvp tool_tuning launch scale quality cost"
	@echo "  make tune-tools      print the pinned companion harness workflow"
	@echo "  make companions      list pinned companion repos"
	@echo "  make companion ID=x  print one pinned companion workflow"
	@echo "  make check-companions verify companion URLs and pins; add CLONE=1 for clone checks"
	@echo "  make test            run every stage's tests"
	@echo "  make check           run every stage's gates"
	@echo "  make adversarial     run checks and tests that enforce the value bar"

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e quality

demo: demo-day0 demo-first_hour demo-idea demo-mvp demo-tool_tuning demo-launch demo-scale demo-quality demo-cost
	@echo ""
	@echo "founder-kit: live walkthrough completed."

day0: demo-day0

demo-day0:
	@echo "== day 0: evals, permissions, monitoring, rollback, stopping conditions =="
	@cd day0 && $(MAKE) PY="$(PY_RUN)" demo

demo-first_hour:
	@echo "== first hour: one call up to a managed agent =="
	@cd first_hour && $(MAKE) PY="$(PY_RUN)" demo

demo-idea:
	@echo "== idea: validate the signal, lint the raise =="
	@cd idea && $(MAKE) PY="$(PY_RUN)" demo

demo-mvp:
	@echo "== mvp: prompt to production, then review the tools =="
	@cd mvp && $(MAKE) PY="$(PY_RUN)" demo

demo-tool_tuning:
	@echo "== tool tuning: pinned companion harness workflow =="
	@cd tool_tuning && $(MAKE) PY="$(PY_RUN)" demo

tune-tools: demo-tool_tuning

companions:
	$(PY_RUN) scripts/companion_registry.py

companion:
	@test -n "$(ID)" || { echo "set ID=<companion id>"; exit 2; }
	$(PY_RUN) scripts/companion_registry.py --id "$(ID)"

check-companions:
	$(PY_RUN) scripts/check_companions.py --verify-urls $(if $(CLONE),--clone,)

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
	@$(PY_RUN) scripts/check_value_bar.py
	@for m in $(MODULES); do \
	  if [ -f $$m/Makefile ] && grep -q '^check:' $$m/Makefile; then \
	    echo "== check: $$m =="; (cd $$m && $(MAKE) PY="$(PY_RUN)" check) || exit 1; \
	  fi; \
	done

adversarial: check test
