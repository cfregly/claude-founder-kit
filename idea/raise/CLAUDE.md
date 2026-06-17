# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The `raise/` module (pitch-deck builder and linter) of claude-startup-idea is a Sequoia-arc pitch-deck builder and a deterministic linter where every word fights for its place. A sloppy example deck scores 0/100 and fails CI. The same company rewritten on the arc scores 100/100. It enforces a claims ledger (every number carries a source tier of measured, attested, public, or modeled), the four dimensions an investor judges, and 15 rules. A renderer turns a JSON spec into a PPTX or PDF.

## Run it

```bash
make demo     # before and after: a sloppy deck (0) then the sharp rewrite (100)
make test     # the rule test suite
make check    # the doc-correctness gate
```

The score is the gate and needs no key: `make check` and `--min-score` run offline. `make demo` passes `--judge`, so it runs the live claude-opus-4-8 narrative read and needs `ANTHROPIC_API_KEY`. The narrative read reviews every interactive run, and the gate (check_docs, CI, `--min-score`) stays deterministic and never calls the API. Rendering a deck needs Node: `npm install --prefix render` once, then `node render/deck_from_spec.mjs deck.json` (add `NO_NOTES=1` for the share-safe variant).

## Where things are

| Path | What it holds |
|---|---|
| `pitch_lint/` | the rules and the scorer |
| `pitch_lint/judge.py` | the claude-opus-4-8 narrative read, reviews every interactive run, advisory only |
| `examples/` | the sloppy deck, the sharp rewrite, and a realistic deck spec |
| `render/` | the pptxgenjs renderer |
| `templates/` | the Sequoia spec template |
| `tests/test_rules.py` | the rule test suite |
| `skills/pitch-deck/SKILL.md` | the Claude skill |
| `scripts/check_docs.py` | the doc-correctness gate |
| `.doccheck.json` | gate config: the rule count and the marquee scores CI re-runs |

Verify each path with `ls` before you rely on it.

## How to extend

- Add a rule as a `PD0NN` check in `pitch_lint/`, plus a test in `tests/test_rules.py`, plus a row in the README table. The rule count is gated against the code, so the README has to match.
- The README documents the scores 0, 100, and 74 as runnable commands, and CI re-runs them. After a rule change, rerun `make demo` and update those numbers in the README if they moved.
- Run `make test` and `make check` after any change to confirm the gates still pass.
- The Claude narrative read (`pitch_lint/judge.py`) reads the arc with `claude-opus-4-8` and structured output. It reviews every interactive run and skips cleanly without a key. The gate (check_docs, CI, `--min-score`) stays deterministic and never calls the API, because the read fires by default only when stdout is a TTY. It is advisory: it never changes the score or the exit code. Keep it that way so the deterministic gate stays reproducible and CI runs it without a key.

## Conventions

- Run `make check` and `make test` before you commit.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. The deslop gate enforces it on the README. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
