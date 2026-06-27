# Value Receipt: Tool Tuning Before And After Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to the companion tool-contract tuning workbench
Baseline: previous founder-kit pin showed only the passing optimizer bundle
Command or artifact tested: `make tune-tools`, companion `optimize-tools` before and after bundles, and companion `demo.gif`
Objection tried: does "tune one tool" stay too vague for a founder to run
Outcome axis: reproducible before and after workflow clarity
Observed result: founder-kit now points to a pinned companion commit where the weak bundle fails with contract recommendations and the sharpened bundle passes
Decision: keep as candidate until a skeptical builder runs it on a real tool workflow
Follow-up: update this receipt when the companion pin changes

## Pin Bump

- Old pin: `efdc801b6e8e4d9cf1e1c32899c8d95325f79304`
- New pin: `200397d848367dcffab9607ca93254de6b187c33`
- New tag: `founder-kit-tool-tuning-before-after-2026-06-27`
- Repo: [claude-agent-harness-optimization](https://github.com/cfregly/claude-agent-harness-optimization)
- Receipt ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-agent-harness-optimization/blob/200397d848367dcffab9607ca93254de6b187c33/docs/confirmed-improvements.md)

## What Changed

- Added `evals/examples/tool_tuning_before_bundle.json` as a deliberate negative control.
- Added `demo.gif`, `demo.tape`, and `docs/tool_tuning_demo_sample.txt` for a deterministic before and after demo.
- Updated tests so the before bundle must fail with actionable contract recommendations.
- Updated the companion docs so "tune one tool" means tightening one callable's name, `use_when`, `avoid_when`, `input_schema`, output contract, context controls, error guidance, examples, negative guidance, and held-out cases.

## Commands Run

```bash
python -m claude_agent_harness_optimization optimize-tools evals/examples/tool_tuning_before_bundle.json --markdown
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m unittest discover -s tests -q
python scripts/check_value_bar.py
python scripts/deslop_check.py
python -m compileall -q claude_agent_harness_optimization scripts
git diff --check
vhs demo.tape
```

This receipt does not say the recipe is adversarially-confirmed to add value. It records a reproducible pointer to the companion workbench and a transparent before and after workflow.
