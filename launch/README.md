# Launch, the activation loop

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Turn early traction into a growth engine that runs without founder bottlenecks:
capture activation events, measure the funnel, operate the loop on a schedule, and
run the weekly metrics brief, using the whole Claude Developer Platform to do it.

- One system, one deliverable. Capture events, measure the funnel, research the
  accounts ready for sales, decide the one motion, draft it, gate every outward
  step, remember last week, and produce the report.
- The deterministic stages are stdlib only: capture, measure, the gate, the audit,
  and the report template. They carry the saved output and the CI gate, so the gate runs
  offline with no key and no install.
- The generative stages run Claude (`claude-opus-4-8`) on every run: enrich, decide,
  and draft. `make demo` runs the whole live pipeline through them, so it needs
  `ANTHROPIC_API_KEY` and raises a clear error when the key or the SDK is missing,
  so a misconfiguration is loud, not a silent downgrade.
- It is a command-line and scheduled-agent system, not a dashboard or UI.
- The CASH morning read (`make morning`, `morning_read.py`) is the daily complement to the
  weekly brief: the roughly 25-chart morning review modeled on the public CASH loop, with a live
  Claude read (`claude-opus-4-8`) that proposes the one motion against the biggest leak while a
  human gates it. Fictional cohort, kept consistent with the weekly pipeline so the kit tells one
  story.

## Run it

```bash
make demo       # the whole live pipeline -> the weekly report (needs ANTHROPIC_API_KEY)
make morning    # the CASH morning read of the cohort (live, renders morning.html)
make test       # the test suite
make check      # the doc-accuracy gate
make coverage   # the platform-surface coverage map
make deploy     # dry-run the Managed Agents weekly deployment plan
```

`make demo` runs the live pipeline and needs `ANTHROPIC_API_KEY`. The deterministic
spine is seeded at 7: 165 events from 12 accounts, the funnel
12 / 12 / 10 / 8 / 5 / 4 / 3 / 1, Q9 (the second-build API key) at 5, activation
67%, retention 62%, an 8-day time-to-second-build, time-to-first-value 2.0 days,
and 2 product-qualified accounts ready for handoff. These numbers are reproducible
from the spine, so re-run before changing one.

## Route a batch to the right brief

`python -m activation route examples/batch.csv` reads a CSV of companies and routes each to the outreach
brief that fits its bottleneck across five pillars: cost, speed, reliability, accuracy, and security.
It scores every one-line description against the brief signal words, fills the matching template from
`outreach-examples/`, and writes the draft into the inert outbox. Nothing is sent, the same gate boundary
the rest of the loop carries. Add `--refine` and Claude deepens every draft so the whole body matches the
company (the example sentence and the code's tool name) and classifies the ones the keywords could not
call, substituting only short phrases so the verified numbers never move. The segmentation and the signal
words live in
[outreach-examples/README.md](outreach-examples/README.md).

## The pipeline

Producing one report runs nine steps, and each step lands on the platform surface
that is the right tool for it.

| Step | What it does | Platform surface |
| --- | --- | --- |
| capture | emit events on one durable id (org_id), opt-out | Messages API, MCP server, swappable backends |
| measure | the funnel, the rates, the leak, the PQAs | structured output, token counting |
| enrich | brief each PQA before the handoff | web search and fetch, Batch API, citations, prompt caching |
| decide | the one motion against the biggest leak | adaptive thinking and effort, the advisor tool |
| draft | the founder message per proposed motion | structured output, code execution and the Files API to render |
| gate | nothing outward runs without approval | permission policy, Agent SDK hooks |
| schedule | run every Monday | Managed Agents deployment (cron) |
| remember | the week-over-week deltas | memory tool, memory store |
| package | a founder installs it | Agent Skills, MCP |

`make coverage` prints the full map. `PLATFORM_COVERAGE.md` mirrors it in prose:
29 load-bearing surfaces, the handful of coverage-only ones named honestly.

## The weekly report

The report is an operating document, not a dashboard. Every line triggers a
decision.

- ACTIVATION: signups, the activation rate, time-to-first-value, the biggest leak.
- RETENTION: time-to-second-build (the leading indicator), the retention rate
  with a leaky-bucket flag, engagement retention, and the lines that need billing
  data, judged against the AI-native bar, not the enterprise bar.
- PIPELINE: the product-qualified accounts ready for handoff, named, and the
  net-new logos attributable this week.
- THE ONE MOTION: the single motion tied to the biggest leak, with the metric it
  moves.
- The gate ledger: what ran on its own, what waits on you, and what the operator
  will not do unattended.

## The loop Anthropic's own growth team runs (CASH)

On a public podcast, Anthropic's growth org described an internal system they call
CASH: Claude runs the growth-experiment loop end to end, identify the opportunity,
build it, test it against the quality and brand bar, analyze the result, with
cross-functional alignment kept human. The head
of growth also has Claude read 20 to 25 charts every morning and surface what moved,
what is concerning, and what is interesting.

This repo is a runnable, human-gated analog of that pattern, not a copy of their
system. Claude proposes the next experiment against the biggest leak (`propose`) and
drafts the founder message (`--draft`), and a deterministic gate decides what ships.
The vendor stack and the metrics are inference from the public description, built on
a fictional cohort. Nothing here is a claim about Anthropic's internal tools.

## The gate

Only measurement and drafting run unattended. Every outward step is proposed and
waits for a human, and a fixed set is refused on a schedule by design.

- always: re-score, flag the leak, draft the report. Internal, runs on its own.
- ask: the second-build nudge, the build clinic, the GTM handoff. Outward, waits.
- never: send mail in your name, spend, post in public, grant credits, hand off an
  account that has not earned it.

The audit proves the boundary held, and `python -m activation operate
readout.json --audit-gates` turns that proof into a CI gate.

## Two harnesses

The same pipeline runs two ways.

- Local: `python -m activation agent` runs the Claude Agent SDK orchestrator, with
  the eleven queries as in-process MCP tools, a hook that enforces the gate, and a
  subagent that briefs each account. Without the SDK or a key it fails loud; use
  `python -m activation agent --dry-run` for the deterministic pipeline.
- Cloud: `python -m activation deploy` shows the Managed Agents deployment that
  fires the weekly run on a Monday cron, with the gate as a permission policy, a
  rubric that grades the report, and a vault for the data credentials.
  `agents/*.yaml` are the version-controlled definitions for the `ant` CLI.

## Where things are

| Path | What it holds |
| --- | --- |
| `activation/contracts.py` | the canonical stages, phases, and gates |
| `activation/capture/` | emit, the eleven queries, the roll-up, the backends |
| `activation/measure/` | the funnel and the retention metrics |
| `activation/enrich/` | the PQA research (web search, batch, citations) |
| `activation/decide/` | the one-motion decision (thinking, effort, advisor) |
| `activation/draft/` | the founder drafts and the report render |
| `activation/operate/` | the gate ledger, the report template, the memory |
| `activation/harness/` | the Agent SDK and Managed Agents harnesses, the MCP server |
| `activation/platform/` | the shared client and the coverage map |
| `agents/` | the version-controlled Managed Agents definitions |
| `skills/activation/` | the packaged Claude Skill |

## Limitations

- The sample cohort is fictional. The enrich step finds nothing about it, which is
  expected. Point the generative stages at a real cohort.
- The logo-retention and NRR lines need billing data from Stripe or Orb, so the
  report names the AI-native band instead of inventing a number.
- The generative stages need ANTHROPIC_API_KEY and a current anthropic SDK, and the
  effort and advisor path in decide needs the newest SDK. With no key or no SDK
  those stages raise a clear error rather than degrade. `make demo` runs them, so it
  needs both. The deterministic spine alone needs neither.

## Where this fits

This is the **Launch** module of [claude-founder-kit](../README.md). The full journey runs as modules in one repo: first_hour, idea, mvp, launch, scale, quality, cost. The playbook names what a founder does at each stage, and these are the runnable tools that do it. Claude runs the judgment on every stage, and a deterministic gate verifies the output before it ships. One `make demo` from the repo root runs the whole arc live.

## License

MIT. See [LICENSE](LICENSE).
