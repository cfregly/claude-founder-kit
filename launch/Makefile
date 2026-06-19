PY ?= python

.PHONY: help demo report morning capture measure operate route gen-examples coverage deploy test check

help:
	@printf 'claude-founder-kit (launch module)\n\n'
	@printf '  make demo          capture -> measure -> gate -> the weekly report (live)\n'
	@printf '  make report        alias for demo\n'
	@printf '  make morning       the CASH morning read of the cohort (live, needs ANTHROPIC_API_KEY)\n'
	@printf '  make measure       score the sample cohort into the readout\n'
	@printf '  make operate       the gated weekly report from the sample readout\n'
	@printf '  make route         route the sample YC cohort, drafting a per-company email to the outbox\n'
	@printf '  make gen-examples  regenerate the committed sample inputs\n'
	@printf '  make coverage      print the platform-surface coverage map\n'
	@printf '  make deploy        dry-run the Managed Agents weekly deployment plan\n'
	@printf '  make test          run the test suite\n'
	@printf '  make check         run the doc-correctness gate\n'

demo:
	$(PY) -m activation demo

report: demo

morning:
	$(PY) morning_read.py --read

capture:
	$(PY) -m activation capture

measure:
	$(PY) -m activation measure examples/cohort.json

operate:
	$(PY) -m activation operate examples/readout.json --weekly --prev examples/prev_week_state.json

route:
	$(PY) -m activation route examples/batch.csv

gen-examples:
	$(PY) -m activation gen-examples

coverage:
	$(PY) -m activation coverage

deploy:
	$(PY) -m activation deploy --dry-run

test:
	$(PY) -m pytest tests/ -q

check:
	$(PY) scripts/check_docs.py
