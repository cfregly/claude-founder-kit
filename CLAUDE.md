# CLAUDE.md

Guidance for Claude Code, or any agent, working in claude-founder-kit. Read it, then run the gates.

## What this repo is

claude-founder-kit is a founder workflow kit for Claude builders as runnable code: the journey from a founder's
first Claude call to a scaling read, in one repo. Each stage is a co-located tool that keeps its own
working code, tests, and gate.

- `first_hour/` the platform ladder, one call up to a managed agent
- `idea/` validate the signal, lint the raise
- `mvp/` prompt to production, then a tool security review
- `launch/` capture a cohort, measure activation, gate the weekly motion
- `scale/` score the data moat and the next GTM motion
- `quality/` the de-slop linter
- `cost/` the platform cost levers

## Live runs and gates

`make demo` is the live walkthrough and needs `ANTHROPIC_API_KEY` from `.env` or the shell. `make check` and `make test`
are the reproducible gates and run without a key. Some modules also expose explicit offline
subcommands, such as JSON readouts or deterministic reports. Keep the boundary clear: live calls
measure or generate, deterministic gates verify structure and drift.

## Value Bar

Apply [VALUE_BAR.md](VALUE_BAR.md) everywhere. Nothing is called valuable until it is adversarially-confirmed to add value. Tests, receipts, and doc gates make a candidate mechanically vetted, not proven useful. If a stage lacks skeptical user evidence against a baseline, say that directly.

## Run it

```bash
make setup
make demo     # live walkthrough, needs ANTHROPIC_API_KEY
make test
make check
make adversarial
```

Each stage runs from inside its own subdir, so each keeps its own gate, tests, and demo. To work on
one alone, cd into it and run that subdir's make targets.

## Trust Docs

- [GETTING_STARTED.md](GETTING_STARTED.md) tells a new user which path to run first.
- [TRUST.md](TRUST.md) explains what the gates check and how to record value evidence.
- [VALIDATION.md](VALIDATION.md) states current evidence and missing evidence.

## Conventions

- Run make check and make test before you commit.
- Each stage keeps its own gates. Do not move a stage's gate up to the root or weaken it.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. Numbers over adjectives.
- Every number traces to a receipt. Reproduce before quoting, never quote from memory.
- Every claim about Claude or the platform traces to the live docs. Verify, do not assert from memory.
- Every value claim traces to skeptical evidence. Candidate is the default label until the value bar is met.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
