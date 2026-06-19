PY ?= python

.PHONY: help demo tour agent check

help:
	@echo "make demo   - run the live tour, steps 1-4 (needs ANTHROPIC_API_KEY)"
	@echo "make agent  - step 5, a Managed Agent, live (needs key and the beta)"
	@echo "make check  - prose gate for README and CLAUDE.md"

demo: tour

tour:
	@$(PY) tour/step1_message.py
	@echo
	@$(PY) tour/step2_thinking.py
	@echo
	@$(PY) tour/step3_tool.py
	@echo
	@$(PY) tour/step4_agent_loop.py

agent:
	@$(PY) tour/step5_managed_agent.py

check:
	@$(PY) check.py
