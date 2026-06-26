# claude-founder-kit

[![ci](https://github.com/cfregly/claude-founder-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/cfregly/claude-founder-kit/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Build a startup on Claude, from the first API call to reading the data moat. One repo, one command,
with the live steps calling the Claude Developer Platform and the gates staying reproducible offline.

This is a founder workflow kit for Claude builders as runnable code. Each stage is a tool a founder actually
uses, and the stages run in order: get to first value, build the product, tune the tools, launch and
measure activation, then read the data moat and the next move.

It is shaped by repeated founder pitch and activation sessions: pressure-test the wedge, build the
first workflow, measure the second build, and route the next GTM motion.

## Value Bar

Nothing in this repo is called valuable until it is adversarially-confirmed to add value. Passing tests and gates means the work is mechanically vetted. Value needs skeptical review against a baseline, with a receipt. See [VALUE_BAR.md](VALUE_BAR.md) and [VALIDATION.md](VALIDATION.md).

Start with [GETTING_STARTED.md](GETTING_STARTED.md) to choose a path. Read [TRUST.md](TRUST.md) before making a value claim.

Start here, then branch only when you need a deeper proof. This repo is the broader founder-journey
kit. [`claude-feature-hits`](https://github.com/cfregly/claude-feature-hits) holds the promoted
Claude feature proofs. [`claude-agent-harness-optimization`](https://github.com/cfregly/claude-agent-harness-optimization)
holds the tool-contract tuning workbench. The companion registry pins both so those moving repos stay
reproducible.

## Run it

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make setup                     # install every stage's deps
cp .env.example .env           # fill ANTHROPIC_API_KEY for live demos
make day0                      # run the keyless trust receipt
make demo                      # run the live walkthrough across stages
make demo-mvp                  # run one stage on its own
make tune-tools                # print the pinned companion harness workflow
make companions                # list pinned companion repos
make companion ID=feature-hits # print the pinned feature-proof workflow
make check-companions          # verify companion URLs and pins
make test                      # every stage's tests
make check                     # every stage's gates
make adversarial               # full local trust gate
```

`make demo` is the live walkthrough and needs `ANTHROPIC_API_KEY` from `.env` or the shell. `make check` and `make test` are deterministic
and do not need a key. `.env` is ignored and must stay local. CI runs those gates on every push and pull request, then runs a push-only
live smoke on a repository secret for a small core path. Measured run outputs live in each stage's
`data/` directory when you regenerate them.

Expected local verification:

```bash
make check   # doc checks and score-drift gates
make test    # offline tests for idea, mvp, launch, scale, and quality
make adversarial
```

## The stages

| Stage | Dir | What it does |
| --- | --- | --- |
| Day 0 | `day0/` | evals, permissions, logs, monitoring, rollback, and stopping conditions before live users |
| First hour | `first_hour/` | the platform ladder, one API call up to a managed agent |
| Idea | `idea/` | score the startup signal, then lint the raise on the Sequoia arc |
| MVP | `mvp/` | prompt to production, then a security review of the agent tools |
| Tool tuning | `tool_tuning/` | thin recipe for the companion harness repo that tunes tool contracts |
| Launch | `launch/` | capture a cohort, measure activation, gate the weekly motion |
| Scale | `scale/` | score the data moat and the GTM motion to run next |
| Quality | `quality/` | the de-slop linter every document in this repo passes |
| Cost | `cost/` | the Claude platform cost levers, each read off the usage object |

Each stage keeps its own README, Makefile, tests, and gate. To work on one alone, `cd` into it.

The Launch stage also ships the [Founder Activation Field Guide](launch/FOUNDER_ACTIVATION_FIELD_GUIDE.md),
an operator field guide for turning founders into builders, wired to the launch module's measured
loop: the workshop formats, the activation motion, the metrics, and the 90-day ramp.

The Tool tuning recipe keeps `claude-agent-harness-optimization` separate and pins the companion
repo from founder-kit. It is the bridge to `optimize-tools`, `model-matrix`, `grind-harness`, and
the confirmed-improvements ledger without duplicating the implementation.

The [Companion Registry](companions/README.md) is the index for deeper repos that founder-kit points
to without vendoring. It currently pins promoted feature proofs, tool tuning, grounding, and Managed
Agents companions.

## What ships with it

The Claude Code skills for these stages are bundled under `.claude/skills/`, so the whole set
installs in one step.

## Trust Docs

- [GETTING_STARTED.md](GETTING_STARTED.md): how to run one path, inspect receipts, and avoid the common traps.
- [day0/](day0/): the keyless trust path for evals, permissions, logs, monitoring, rollback, and stopping conditions.
- [TRUST.md](TRUST.md): what the gates check, what they do not check, and the receipt template for real value evidence.
- [VALIDATION.md](VALIDATION.md): current evidence and missing evidence.
- [receipts/](receipts/): internal and external evidence files, labeled by strength.

## License

MIT. See [LICENSE](LICENSE).
