# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

claude-deslop is a deterministic de-slop linter. One canonical ruleset finds AI-slop in two places, the prose (em-dashes, buzzwords, filler phrases, generic template copy) and the rendered HTML (purple gradients, centered-everything, emoji-as-design, border-left cards). A sloppy doc scores F, clean prose scores 100. This repo is also the single source of truth for the slop rules, which sync into sibling repos so nothing drifts by hand.

## Run it

```bash
make demo     # before and after: a sloppy doc (F) then clean prose (A), with the live judge (needs ANTHROPIC_API_KEY)
make test     # the rule test suite
make check    # the doc gate plus a self-deslop of the README
```

The rule score needs no dependencies and no API key, so the gate runs offline in every sibling repo's CI. Lint anything: `python -m deslop README.md`, `python -m deslop index.html`, or pipe stdin with `echo "..." | python -m deslop -`. As a library: `from deslop import lint, lint_text, lint_html`. The Claude judge reviews every interactive run and prints advisory notes below the score, never changing it. The gate (check_docs, CI, `--min-score`) stays deterministic and never calls the API.

## Where things are

| Path | What it is |
| --- | --- |
| `deslop/` | the linter package |
| `deslop/judge.py` | the Claude semantic-slop judge, reviews every interactive run, advisory only |
| `deslop/slop_rules.json` | THE canonical ruleset |
| `scripts/sync.py` | copy the canon into sibling repos, `--check` to fail on drift |
| `examples/sloppy.md`, `examples/clean.md` | the before and after |
| `tests/test_rules.py` | the rule test suite |
| `skills/deslop/SKILL.md` | the Claude Code skill |
| `scripts/check_docs.py` | the doc-correctness gate |
| `.desloprc.example` | bless intentional choices |

Verify each path with `ls`.

## How to extend

- Rules live in `deslop/slop_rules.json`, from DS001 (the prose dash tell) through the visual DS010 to DS013.
- Add a rule plus a test case, then run `python scripts/sync.py` so the sibling repos stay in lockstep. CI runs `python scripts/sync.py --check` and fails on drift.
- Bless an intentional word or rule with a `.desloprc`.
- The Claude judge (`deslop/judge.py`) reviews every interactive run: it uses `claude-opus-4-8` to surface semantic slop the rules cannot enumerate, and it never changes the score or the exit code. The gate (check_docs, CI, `--min-score`) stays deterministic and never calls the API, because the judge fires by default only when stdout is a TTY. The gate is deterministic by design and Claude rides on top. Keep it advisory so the gate stays reproducible, and keep it a no-op without a key so CI runs offline. `--judge` forces the attempt regardless of the TTY, `--no-judge` suppresses it.

## Conventions

- Run `make check` and `make test` before you commit. `make check` self-deslops this repo's own README.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. This repo's own linter enforces it. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
