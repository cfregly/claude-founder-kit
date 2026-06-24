# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The idea module of claude-founder-kit is the Idea stage of a founder playbook for Claude builders: validate the idea before you build, and pressure-test the raise. It bundles two co-located sub-tools, each keeping its own working code, tests, and gate.

- `validate/` scores the startup signal and argues against the idea. It is the startup validation linter.
- `raise/` builds and lints the pitch deck on the Sequoia arc. It is the pitch and raise linter.

In both tools the deterministic score is the gate, and Claude runs the judgment. The score runs offline and is what CI re-runs. The Claude layer (`claude-opus-4-8`) reads the score and writes the call the rules cannot, and it fires only when stdout is a TTY, so the gate stays reproducible and runs without an API key.

## Value Bar

Apply [../VALUE_BAR.md](../VALUE_BAR.md). The Idea tools stay candidates until they are adversarially-confirmed to add value against a founder's baseline. Do not call the score valuable by itself. It is mechanical evidence only.

## Run it

```bash
make check    # both sub-tools doc-correctness gates
make test     # both sub-tools test suites
make demo     # each sub-tools demo
```

Each target runs both sub-tools from inside their own subdir, so each keeps its own gate, tests, and demo unchanged. To work on one tool alone, `cd validate` or `cd raise` and run that subdir's own `make check`, `make test`, and `make demo`.

## Where things are

| Path | What it holds |
| --- | --- |
| `validate/` | the startup validation linter, with its own package, skill, tests, and gate |
| `raise/` | the pitch and raise linter, with its own package, skill, tests, and gate |
| `validate/scripts/check_docs.py` | the validate doc-correctness gate |
| `raise/scripts/check_docs.py` | the raise doc-correctness gate |
| `validate/skills/startup-linter/SKILL.md` | the validate Claude skill |
| `raise/skills/pitch-deck/SKILL.md` | the raise Claude skill |

Each subdir carries its own `CLAUDE.md`, `README.md`, `Makefile`, and `.doccheck.json`. Read the subdir's `CLAUDE.md` before changing that tool.

## Conventions

- Run `make check` and `make test` before you commit.
- Each subdir keeps its own gates. Do not move a tool's gate up to the root or weaken it. The deterministic score stays the gate, Claude stays the judgment, and the model wording stays as written.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
