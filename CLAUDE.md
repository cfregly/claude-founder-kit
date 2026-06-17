# CLAUDE.md

Guidance for Claude Code, or any agent, working in claude-founder-kit. Read it, then run the gates.

## What this repo is

claude-founder-kit is Anthropic's Founder's Playbook as runnable code: the journey from a founder's
first Claude call to a scaling read, in one repo. Each stage is a co-located tool that keeps its own
working code, tests, and gate.

- `first_hour/` the platform ladder, one call up to a managed agent
- `idea/` validate the signal, lint the raise
- `mvp/` prompt to production, then a tool security review
- `launch/` capture a cohort, measure activation, gate the weekly motion
- `scale/` score the data moat and the next GTM motion
- `quality/` the de-slop linter
- `cost/` the platform cost levers

## Everything runs online

Every demo makes a real Claude call and fails fast without a key. There is no offline mode and no
sample-data fallback. CI runs the same live path on a repository secret, so a green build means the
demos really ran. Deterministic linters (de-slop, the tool-contract grader, pitch_lint) stay
deterministic because they are linters, and their Claude judge runs as well rather than being gated
off.

## Run it

```bash
make setup
make demo     # the whole arc live, needs ANTHROPIC_API_KEY
make test
make check
```

Each stage runs from inside its own subdir, so each keeps its own gate, tests, and demo. To work on
one alone, cd into it and run that subdir's make targets.

## Conventions

- Run make check and make test before you commit.
- Each stage keeps its own gates. Do not move a stage's gate up to the root or weaken it.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. Numbers over adjectives.
- Every number traces to a receipt. Reproduce before quoting, never quote from memory.
- Every claim about Claude or the platform traces to the live docs. Verify, do not assert from memory.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
