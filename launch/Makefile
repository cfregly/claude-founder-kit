.PHONY: help demo report capture measure operate gen-examples coverage deploy test check

help:
	@printf 'claude-startup-launch\n\n'
	@printf '  make demo          capture -> measure -> gate -> the weekly report, offline\n'
	@printf '  make report        alias for demo\n'
	@printf '  make measure       score the sample cohort into the readout\n'
	@printf '  make operate       the gated weekly report from the sample readout\n'
	@printf '  make gen-examples  regenerate the committed sample inputs\n'
	@printf '  make coverage      print the platform-surface coverage map\n'
	@printf '  make deploy        dry-run the Managed Agents weekly deployment plan\n'
	@printf '  make test          run the test suite\n'
	@printf '  make check         run the doc-correctness gate\n'

demo:
	python3 -m activation demo

report: demo

capture:
	python3 -m activation capture

measure:
	python3 -m activation measure examples/cohort.json

operate:
	python3 -m activation operate examples/readout.json --weekly --prev examples/prev_week_state.json

gen-examples:
	python3 -m activation gen-examples

coverage:
	python3 -m activation coverage

deploy:
	python3 -m activation deploy --dry-run

test:
	python3 -m pytest tests/ -q

check:
	python3 scripts/check_docs.py
