# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The launch module of claude-founder-kit turns early traction into a growth engine that runs without
founder bottlenecks: it captures activation events, measures the funnel, operates the
loop on a schedule, and runs the weekly metrics brief, using the whole Claude
Developer Platform to do it. One pipeline (capture, measure,
enrich, decide, draft, gate, remember, render) turns a founder cohort into the
weekly startup-signal report. It is a command-line and scheduled-agent system, not
a dashboard or UI. The deterministic stages (capture, measure, the gate, the audit,
the report template) are stdlib only and carry the receipt, so the gate runs
offline in CI. `make demo` runs the whole live pipeline (enrich, decide, draft,
render), so it needs `ANTHROPIC_API_KEY` and fails fast without it. The generative
stages (enrich, decide, draft) run Claude on every run and raise a clear error with
no key, so a misconfiguration is loud, not a silent downgrade.

## Run it

```bash
make demo       # the whole live pipeline -> the weekly report (needs ANTHROPIC_API_KEY)
make test       # the test suite
make check      # the doc-correctness gate
make coverage   # the platform-surface coverage map
make deploy     # dry-run the Managed Agents weekly deployment plan
```

`make demo` runs the live pipeline (enrich, decide, draft, render), so it needs
`ANTHROPIC_API_KEY` and fails fast without it. `python -m activation measure
cohort.json`, `operate readout.json`, `enrich`, `decide`, `draft`, `agent`, `mcp`,
and `deploy` are the other subcommands. The generative stages (enrich, decide,
draft) need `ANTHROPIC_API_KEY` and a current anthropic SDK and raise without them,
and the local agent harness needs `claude-agent-sdk`.

## Where things are

| Path | What it holds |
| --- | --- |
| `activation/contracts.py` | the canonical stages, phases, gates: one source of truth |
| `activation/capture/` | emit, the eleven queries, the cohort roll-up, the backends |
| `activation/measure/metrics.py` | the funnel and the retention metrics |
| `activation/enrich/`, `decide/`, `draft/` | the generative Claude steps, mandatory on every run |
| `activation/route/` | route a company batch to the right outreach brief, draft each into the gated outbox |
| `activation/operate/` | the gate ledger, the report template, the memory |
| `activation/harness/` | agent_sdk (local), managed_agent (cloud), mcp_server |
| `activation/platform/` | the shared client and the coverage map |
| `agents/*.yaml` | the version-controlled Managed Agents definitions for the ant CLI |
| `scripts/check_docs.py` | the doc-correctness gate |

## How to extend

- The contracts are the spine. `contracts.py` owns the stages, the event map, the
  phases, and the three gates. Add an event there, not a translation layer.
- The capture, measure, and operate stages are stdlib only and deterministic. The
  same readout gives the same plan every run.
- The gate is the boundary: every action carries always, ask, or never. Only
  always actions run unattended, and `audit` proves it. Any change to the boundary
  is visible in the diff and caught by the audit and the test.
- The generative stages (`platform/client.py`'s `require_client` guards them) are
  the only place a model runs. Each calls `require_client` and raises with no key
  or no SDK, so a missing key fails loud rather than degrading. Keep it that way:
  determinism on the gate, Claude on the judgment, and the gate verifies the output.
- The coverage map (`platform/coverage.py`) is the verifiable claim that the report
  touches the whole platform. Update it when a step changes which surface it uses.

## Conventions

- Run `make check` and `make test` before you commit.
- The deterministic spine is seeded at 7. The funnel and activation numbers in the
  README and the docs are reproducible from it, so re-run before you change a number,
  do not edit it by hand.
- Telemetry is opt-out. Never make emit track silently, and never commit a key.
  `.env` stays git-ignored.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. The deslop
  gate enforces it on the README. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
