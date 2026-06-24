# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The mvp module of claude-founder-kit is the MVP stage of a founder workflow kit for Claude builders: build the product, then a security review before any user touches it. It bundles two co-located tools, each self-contained with its own package, tests, and gate:

- [`build/`](build/) takes a founder from a first Claude API call to an evaluated, cost-engineered, deployable agent. Five acts: a first streaming call, tools as contracts, evals in CI including honesty cases, cost engineering (caching plus routing), and an MCP encore. Its `starter/` is a forkable FastAPI app.
- [`harden/`](harden/) is the security review of the agent surface. It turns vague MCP tools into contract-grade interfaces, scored against 16 rules with an OWASP and STRIDE security lens, and grades an agent protocol and a harness manifest.

The order is the point: build the agent, then review its tool surface before any user sees it.

## Value Bar

Apply [../VALUE_BAR.md](../VALUE_BAR.md). The MVP stage is not called valuable until it is adversarially-confirmed to add value for a builder against a baseline build, eval, cost, or hardening workflow. Tests are mechanical evidence only.

## Run it

```bash
make setup    # install build/ deps, one time (for the live acts)
make demo     # both demos: the cost receipt, then the before/after lint
make test     # both test suites
make check    # both deterministic gates
```

Each target fans out into both subdirs and fails if either fails. The top-level `make check` runs `(cd build && make check) && (cd harden && make check)`. To work on one tool alone, run the same targets from its subdir.

## Where things are

| Path | What it is |
|---|---|
| `build/` | The five-act path to a deployable agent. Its CLAUDE.md has the detail. |
| `harden/` | The security review. Its CLAUDE.md has the detail. |
| `build/models.py` | The model ladder. The one place build's model ids live. |
| `build/scripts/check_docs.py`, `harden/scripts/check_docs.py` | Each tool's doc-correctness gate, scoped to its own subtree. |
| `Makefile` | The top-level fan-out into both subdirs. |

## Conventions

- Each subdir is self-contained. A change to one tool stays in its subdir. Do not reach across `build/` and `harden/` to share code, because each ships as its own runnable tool.
- Run `make check` and `make test` before you commit.
- The model wording is honest: `claude-opus-4-8` is the stable default, `claude-fable-5` is the access-gated top rung, and there is no "latest model" claim. Pin a dated snapshot in production.
- The deterministic gate is the gate. Claude runs as the mandatory or TTY-gated judgment layer, and the score reproduces offline without a key. Keep that split.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
