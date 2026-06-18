# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The idea/validate module (startup signal lab) of claude-founder-kit scores a startup's raw signal, a pitch, site copy, or a README, into product, GTM, and architecture decisions. It runs local deterministic scoring for value proposition, urgency, platform risk, moat, and customer pain, a Relationship-Activation-Retention growth read that names the weakest stage, and a Dot/Dash/Star use-case sort. Claude reads those scores and writes the founder intervention on every run. The deterministic scoring runs offline and is the gate CI re-runs. The intervention runs Claude (`claude-opus-4-8`) and needs `ANTHROPIC_API_KEY` set: with no key or no SDK it raises a clear error rather than degrading to a canned response.

## Run it

```bash
make demo     # score a strong pitch (8/10) deterministically, then write the live intervention (needs ANTHROPIC_API_KEY)
make test     # the test suite
make check    # the doc-correctness gate
```

The full app is `streamlit run app.py` after `pip install -r requirements.txt`. The Streamlit app and the eval harness run Claude on every analysis and need `ANTHROPIC_API_KEY` set. `make demo` prints the deterministic score and then runs the live founder intervention, so it needs the key too and fails fast without it. `make check` is the doc-correctness gate and stays deterministic offline.

## Where things are

| Path | What it holds |
| --- | --- |
| `app.py` | the Streamlit demo |
| `startup_signal_lab/` | scoring, routing, MCP server, the score CLI |
| `examples/` | sample pitches |
| `tests/` | the test suite |
| `skills/startup-linter/SKILL.md` | the Claude skill |
| `scripts/check_docs.py` | the doc-correctness gate |
| `pricing.json` | model pricing for the unit-economics estimate |

## How to extend

- Scoring lives in `startup_signal_lab/`: `score.py` is the CLI, `scoring_tools.py` and `growth.py` hold the dimensions, `router.py` picks the model.
- The MCP tools are exposed with `python -m startup_signal_lab.mcp_server`.
- The README documents the strong-pitch score 8/10 as a runnable command that CI re-runs, so keep the score and the README in sync.

## Conventions

- Run `make check` and `make test` before you commit.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. The deslop gate enforces it on the README. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
