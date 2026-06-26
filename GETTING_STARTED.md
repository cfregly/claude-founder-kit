# Getting Started

Start with the gates, then choose the stage that matches the job. Do not start with the full live demo unless you already have a key and know which path you want to test.

## 1. Prove the Repo Runs

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make setup
make adversarial
```

`make adversarial` is the local trust pass. It runs the value-bar gate, every deterministic doc gate, every offline test, and the live-entrypoint check that verifies live scripts fail cleanly when no key is present.

This does not prove the kit helped a founder. It means the repo is mechanically checked and ready for a real user run.

## 2. Pick the Job

| If you need to | Start here | Command |
| --- | --- | --- |
| Add day-0 trust controls before live users | `day0/` | `make day0` |
| See the platform path from first call to agent | `first_hour/` | `make demo-first_hour` |
| Pressure-test an idea or pitch | `idea/` | `make demo-idea` |
| Build a Claude app path with evals and cost receipts | `mvp/build/` | `cd mvp/build && python 03_evals.py` |
| Run promoted Claude feature proofs | companion `feature-hits` | `make companion ID=feature-hits` |
| Review MCP tools and agent boundaries | `mvp/harden/` | `cd mvp/harden && make demo` |
| Tune tool names, descriptions, schemas, and harness behavior | `tool_tuning/` | `make tune-tools` |
| Measure a launch cohort and gate the weekly motion | `launch/` | `make demo-launch` |
| Score moat and GTM motion | `scale/` | `make demo-scale` |
| De-slop docs before shipping | `quality/` | `cd quality && python -m deslop README.md` |
| Measure Claude cost levers | `cost/` | `make demo-cost` |

Live commands need `ANTHROPIC_API_KEY`. Offline gates do not.

## 3. Run One Live Path

```bash
cp .env.example .env
# fill ANTHROPIC_API_KEY in .env, or export it in your shell
make demo-mvp
```

Use one stage first. The full `make demo` walks the whole kit, which is useful for a tour but noisy when you are trying to understand one job.

## 4. Inspect the Receipts

Look for generated outputs before you trust a claim.

| Artifact | What it tells you |
| --- | --- |
| `day0/evals/template.jsonl` | Win, honesty, permission, rollback, and stop-condition fixtures |
| `day0/templates/rollout_gate.json` | Offline, shadow, canary, default, rollback, and stopping conditions |
| `mvp/build/data/last_eval.json` | Which eval tiers ran, passed, or were unavailable for your key |
| `mvp/build/data/last_run.json` | Cost, latency, tokens, cache reads, and routing result for the cost benchmark |
| `companions/registry.json` | The pinned companion repo commits, ledgers, receipts, and commands |
| `receipts/feature-hits-companion-pin-2026-06-26/receipt.md` | The pinned feature-hits commit and commands |
| `cost/data/last_run_receipt.md` | Token and cost details for the cost lever run |
| `launch/examples/readout.json` | Reference launch cohort readout used by deterministic launch checks |

Generated receipts are mechanical evidence. They are useful, but they are not the same as user value.

## 5. Apply the Value Bar

Nothing here is called valuable until it is adversarially-confirmed to add value. To test a stage for real value, run it against a baseline workflow, let a skeptical user reject it, record the objection, and save the receipt. Use [TRUST.md](TRUST.md) for the template.

## 6. Common Failure Modes

- Missing key: live scripts exit with an explicit `ANTHROPIC_API_KEY` error.
- Model access: gated models may show as unavailable. That is an access gap, not a pass.
- Cost claims: rerun the benchmark and quote your own receipt.
- Value claims: if there is no baseline and skeptical receipt, call the output candidate or mechanically checked.
