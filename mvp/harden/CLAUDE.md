# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The `harden/` module of claude-startup-mvp turns vague MCP tools into contract-grade agent interfaces. It reads the
wire format an MCP server publishes (the `tools/list` response) and scores each tool against 16
rules, including an OWASP and STRIDE security lens and a tool-discovery check. It also grades an
agent protocol (AGENTS.md), a harness manifest, and a SKILL.md. A vague example server scores
14/100. The contract-grade rewrite scores 100/100.

The idea this enforces: the model is the caller of your API and it cannot
read your source, so the tool contract is the interface. Context is a finite budget, so a tool
that forces the model to guess wastes both tokens and reliability.

## Run it

```bash
make demo     # the before and after: a vague server (14) then the contract-grade rewrite (100)
make test     # the rule test suite
make check    # the doc-correctness and rule-count gate
```

`make demo` passes `--judge`, so it runs the live Claude (`claude-opus-4-8`) rewrite of the worst
tool and needs `ANTHROPIC_API_KEY`. The same rules re-score the rewrite, so the score reproduces.
`make check`, `make test`, and `--min-score` are the deterministic gate and need no key. The gate
(check_docs, CI, `--min-score`) stays deterministic and never calls the API, because the rewrite
fires by default only when stdout is a TTY. With no key the rewrite is skipped and the score is
identical, so CI stays green offline. Pass `--no-judge` to force the deterministic-only path, or
`--judge` to force it on regardless of the TTY.

## Where things are

| Path | What it is |
| --- | --- |
| `contract_doctor/rules.py` | the 16 tool rules, CD001 to CD016 |
| `contract_doctor/harness.py` | the harness grader, HA001 to HA010 |
| `contract_doctor/skill.py` | the SKILL.md grader, SK001 to SK007 |
| `examples/` | before and after tool sets, a realistic server, harness and skill samples |
| `tests/test_rules.py` | the rule suite CI runs |
| `skills/agent-linter/SKILL.md` | the Claude skill packaging |
| `scripts/check_docs.py` | the doc-correctness gate |
| `.doccheck.json` | gate config: the rule count and the marquee scores CI re-runs |

## How to extend

- Add a rule: add a `CD0NN` check in `contract_doctor/rules.py`, a case in
  `tests/test_rules.py`, and a row in the README rules table. The README rule count is gated
  against the code, so change both.
- The README documents scores as runnable commands (for example `# 14/100`). CI re-runs them
  and fails if the live score drifts, so rerun `make demo` after a rule change and update the
  README numbers to match.

## Conventions

- Run `make check` and `make test` before you commit.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. The deslop gate enforces
  it on the README. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
