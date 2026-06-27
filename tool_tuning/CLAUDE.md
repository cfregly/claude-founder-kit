# CLAUDE.md

Guidance for working on the `tool_tuning/` recipe.

## What This Is

`tool_tuning/` is a thin founder-kit recipe called "Tune your tools." It points builders to the companion `claude-agent-harness-optimization` repo for tool-contract tuning, MCP selection evals, model matrices, and harness grinding.

The companion repo is pinned at commit `200397d848367dcffab9607ca93254de6b187c33`. The pinned receipt is `docs/confirmed-improvements.md` at that commit.

The founder-facing commands are `optimize-tools`, `model-matrix`, and `grind-harness`. The pinned
before and after optimizer examples are `tool_tuning_before_bundle.json` and
`agent_audit_bundle.json`.

## Value Bar

Apply [../VALUE_BAR.md](../VALUE_BAR.md). This recipe is not called valuable until it is adversarially-confirmed to add value on a real tool workflow against a baseline. The pin and tests are mechanical evidence only.

## Rules

- Keep `claude-agent-harness-optimization` separate.
- Do not copy its package, eval matrices, recipes, or tests into this repo.
- Update [../companions/registry.json](../companions/registry.json), [README.md](README.md), and the local receipt together when the companion pin changes.
- Keep `make tune-tools` as the simple founder-facing entrypoint from the repo root.
- Run `make check` and `make test` from this directory before committing.

## Run It

```bash
make demo
make check
make test
```
