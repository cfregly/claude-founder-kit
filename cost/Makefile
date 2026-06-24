PY ?= python

.PHONY: demo check test

demo:
	$(PY) run.py

check:
	$(PY) scripts/deslop_check.py
	$(PY) -m compileall cost_control run.py scripts

test: check
	@if env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN PYTHON_DOTENV_DISABLED=1 $(PY) run.py; then \
	  echo "run.py exited 0 without a key, expected non-zero"; \
	  exit 1; \
	else \
	  echo "missing-key path fails fast"; \
	fi
