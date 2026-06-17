PY ?= python3

.PHONY: help demo tour agent check

help:
	@echo "make demo   - replay the recorded tour (no key, no beta)"
	@echo "make tour   - run steps 1-4 live (needs ANTHROPIC_API_KEY)"
	@echo "make agent  - run step 5, a Managed Agent, live (needs key and beta)"
	@echo "make check  - prose gate for README and CLAUDE.md"

demo:
	@$(PY) tour/replay.py

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
