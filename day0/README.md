# Day 0 Trust Path

Build trust controls before the first live user. This stage is a small, keyless harness that shows
the minimum trust and safety shape a founder should wire in before a Claude workflow touches customer
data or takes actions.

## Value Bar

This stage is a candidate until it is adversarially-confirmed to add value for a real builder taking
a Claude workflow toward production. A passing demo proves the controls run. It does not prove a
startup shipped more safely until a skeptical reviewer compares it with the prior workflow and leaves
a receipt.

## Run It

```bash
make day0
cd day0 && make demo
cd day0 && make check
cd day0 && make test
```

No API key is required. The demo is deterministic so it can run in CI and on a fresh clone.

## What It Covers

| Control | File | What the demo proves |
| --- | --- | --- |
| Evals | `evals/template.jsonl` | Golden cases cover win, honesty, permission, rollback, and stop behavior |
| Permissions | `templates/trust_controls.json` | Read-only work can run, outward actions ask, destructive actions are denied |
| Monitoring | `templates/trust_controls.json` | Each run reports correctness, latency, fallback, policy, and cost signals |
| Rollback | `templates/rollout_gate.json` | Canary regressions route back to the direct path |
| Stopping conditions | `templates/rollout_gate.json` | Wrong answers, policy drift, failure spikes, and cost regressions stop rollout |
| Tool contract | `templates/tool_contract_template.json` | The tool says what it can read, what it returns, and what it must not do |

## The Day-0 Contract

Before a workflow is called production-ready, write these down:

1. The claim: what workload Claude should improve.
2. The eval: what fixture or trace would catch a wrong answer.
3. The permission boundary: what can run, what asks, and what never runs.
4. The monitoring signals: what gets logged on every task.
5. The rollout gate: offline, shadow, canary, then default.
6. The rollback path: where traffic goes when the canary fails.
7. The stopping conditions: which failures pause or stop rollout.

## Where To Go Next

- First API call: `make demo-first_hour`
- Build with evals and cost receipts: `cd mvp/build && python 03_evals.py`
- Review tool and agent boundaries: `cd mvp/harden && make demo`
- Run promoted feature proofs: `make companion ID=feature-hits`
- Tune tool contracts: `make tune-tools`
