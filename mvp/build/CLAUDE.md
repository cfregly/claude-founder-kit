# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

The mvp/build module of claude-founder-kit is a founder's 15-minute path from a first Claude API call to an evaluated, cost-engineered, deployable agent. Every act runs Claude: the model ladder (`claude-haiku-4-5` to `claude-opus-4-8`), the Messages API, the eval gate, and the Agent SDK repo doctor. It runs as five acts: a first streaming call, tools as contracts, evals in CI including honesty cases, cost engineering (caching plus routing, measured at about 85 percent lower cost on the bundled workload), and an MCP encore. The `starter/` directory is a forkable FastAPI app you deploy.

## Run it

```bash
make setup    # install deps, one time
make demo     # measure the cost table live: 04_cost_engineering.py, about 36 real calls, needs ANTHROPIC_API_KEY
make test     # the eval-set self-test
make check    # the doc-correctness gate
```

`make demo` assumes the deps are installed, so run `make setup` first. The five acts also run individually: `python 01_first_call.py` through `python 05_agent_sdk_repo_doctor.py`. Acts that call the API need `ANTHROPIC_API_KEY` (copy `.env.example` to `.env`). `python 04_cost_engineering.py` measures your own numbers and writes them to `data/last_run.json` plus a paste-ready `data/last_run.md`.

## Where things are

Verify each path with `ls` before you rely on it.

| Path | What it is |
|---|---|
| `01_first_call.py` ... `05_agent_sdk_repo_doctor.py` | The five numbered acts, in order. |
| `06_structured_output.py` | The output contract: structured outputs with a JSON schema, the companion to Act 2. |
| `models.py` | The four-rung model ladder (junior to distinguished). The one place model ids live. |
| `eval_lint.py` | Gate the quality of your eval set. The bundled golden set scores 97/100. |
| `mcp_server/` | The same tools exposed over MCP. |
| `starter/` | The forkable FastAPI app, with its own Dockerfile. |
| `data/` | Fictional sample data plus measured run receipts. |
| `pricing.json` | Per-token rates, with a verify-before-quoting note. |
| `scripts/check_docs.py` | The doc-correctness gate that `make check` runs. |
| `skills/prompt-to-production/SKILL.md` | The packaged Claude Skill. |

## How to extend

- Add an eval case to `data/golden_set.jsonl`, then rerun `make test`.
- Add a routing strategy in `04_cost_engineering.py`.
- Change a model in one place: `models.py` holds the four-rung ladder every act imports. The forkable `starter/` keeps its own default so it stays self-contained.
- Fork `starter/` to ship a product of your own.
- The cost numbers come from one run on one workload. Rerun it before quoting them, and check rates against `pricing.json`, which carries a verify-before-quoting note. The README documents the 97/100 eval-lint score as a runnable command that CI re-runs, so keep the README and the code in sync.

## Conventions

- Run `make check` and `make test` before you commit.
- Prose is plain: no em-dashes, no semicolons in prose, no buzzwords. The deslop gate enforces this on the README. Numbers over adjectives.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
