# Trust Model

Current status: mechanically checked, not externally confirmed.

The repo can tell you whether the code, docs, receipts, and gates agree. It cannot tell you that a founder, builder, or operator got value until a skeptical user tests it against a baseline. That is the bar: adversarially-confirmed to add value.

## What the Gates Check

| Gate | Command | What it catches |
| --- | --- | --- |
| Value-bar gate | `python scripts/check_value_bar.py` | Missing value-bar language, overclaimed wording, official-sounding drift |
| Root doc and test pass | `make check && make test` | Stage doc correctness, score drift, offline tests, compile checks |
| Live-entrypoint gate | `cd mvp/build && python scripts/check_live_entrypoints.py` | Broken live scripts, tracebacks without a key, unclear key failures |
| Full adversarial pass | `make adversarial` | The full local gate stack a reviewer should run before trusting the repo |
| CI deterministic job | `.github/workflows/ci.yml` | `make check`, `make test`, and `make adversarial` on push and pull request |
| CI live smoke | `.github/workflows/ci.yml` | A small key-backed push-only smoke path when the repo secret is configured |

## What the Gates Do Not Check

- They do not prove a founder saved time.
- They do not prove a pitch improved.
- They do not prove activation got clearer.
- They do not prove the cost pattern helps your workload.
- They do not prove a security reviewer found the same risks as the local rules.

Those require a baseline, a skeptical reviewer, and a receipt.

## Stage Trust Map

| Stage | Current evidence | Receipt needed before a value claim |
| --- | --- | --- |
| First hour | Live API ladder and transcript shape | A new platform user compares it with their baseline onboarding path |
| Idea | Offline scoring and deck lint gates | A founder or reviewer compares the output with the prior decision or pitch |
| MVP build | Eval lint, live-entrypoint checks, cost receipts | A builder compares it with their normal prompt-to-production workflow |
| MVP harden | Tool and harness rule tests | A security or agent reviewer compares findings with a baseline review |
| Launch | Deterministic reference cohort and gated report | An operator compares it with their weekly activation review |
| Scale | Offline moat scoring tests | A growth lead compares it with their account-planning workflow |
| Quality | De-slop rules and examples | A reviewer compares before and after on a real artifact |
| Cost | Usage-object receipts | A builder compares the lever against a baseline bill or token trace |

## Current Internal Evidence

[receipts/internal-founder-simulation-2026-06-24/receipt.md](receipts/internal-founder-simulation-2026-06-24/receipt.md) records one internal founder simulation. It shows the kit catching a weak eval set, unsafe MCP tool contracts, and concrete launch or scale motions on a realistic scenario.

This is useful evidence, but it is not external proof. It does not replace a skeptical user running the kit on their own workflow.

## Value Receipt Template

Copy this into an issue, PR, or `receipts/` file when a stage earns stronger language.

```md
# Value Receipt: <stage and task>

Status: candidate | mechanically checked | adversarially confirmed | rejected
Reviewer role: <founder, builder, operator, security reviewer, growth lead>
Workflow: <real or realistic task>
Baseline: <old process, manual pass, competing tool, or previous artifact>
Command or artifact tested: <exact command or file>
Objection tried: <what the reviewer challenged>
Outcome axis: <time, clarity, cost, risk caught, activation, decision speed>
Observed result: <number or concrete observation>
Decision: <use, change, reject>
Follow-up: <what changed because of this run>
```

Do not name private people in public receipts. Use roles.

## How to Challenge a Stage

1. Pick one stage and one real job.
2. Save the baseline artifact or timing.
3. Run the stage.
4. Ask a skeptical reviewer what got worse, what stayed vague, and what they would reject.
5. Record the outcome.
6. Only then upgrade the label.

If the run fails, record that too. A rejected receipt is useful evidence.
