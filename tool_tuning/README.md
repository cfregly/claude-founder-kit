# Tool Tuning

Thin founder-kit recipe for the moment when a Claude app has real tools and the next blocker is routing, arguments, or response shape.

This recipe does not copy the harness implementation. It points to the companion repo that owns tool-contract tuning, MCP selection evals, model matrices, and harness grinding.

Use it after you can name the workload. Build the narrow tool contract, test it with a held-out
tool-selection eval, avoid broad or side-effectful tools without policy, and only then widen access
from offline to shadow, canary, and default.

Tune one tool means pick one callable in your product and tighten its name, `use_when`,
`avoid_when`, `input_schema`, output contract, context controls, error guidance, examples, negative
guidance, and held-out cases. The pinned companion now includes a before bundle that fails and an
after bundle that passes.

## Value Bar

The recipe is a candidate until it is adversarially-confirmed to add value for a real tool workflow. The pin and gates prove the reference is reproducible. They do not prove a founder saved time, reduced mistakes, or improved reliability until a skeptical builder compares it with a baseline and leaves a receipt.

## Run It

```bash
make tune-tools
cd tool_tuning && make demo
```

The command prints the pinned companion workflow. It does not make live calls and it does not install the companion repo for you.

## Companion Snapshot

| Field | Pin |
| --- | --- |
| Repo | [`claude-agent-harness-optimization`](https://github.com/cfregly/claude-agent-harness-optimization) |
| Commit | `200397d848367dcffab9607ca93254de6b187c33` |
| Tag | `founder-kit-tool-tuning-before-after-2026-06-27` |
| Ledger | [`docs/confirmed-improvements.md`](https://github.com/cfregly/claude-agent-harness-optimization/blob/200397d848367dcffab9607ca93254de6b187c33/docs/confirmed-improvements.md) |
| Local receipt | [`../receipts/tool-tuning-before-after-companion-pin-2026-06-27/receipt.md`](../receipts/tool-tuning-before-after-companion-pin-2026-06-27/receipt.md) |

## When To Use It

- Claude chooses the wrong adjacent tool.
- Arguments are valid JSON but wrong for the workflow.
- A tool returns too much context or hides the evidence needed to audit the answer.
- A prompt change helps one case and regresses another.
- You need to compare tool behavior across model, harness, and instruction variants.

## Pinned Workflow

```bash
git clone https://github.com/cfregly/claude-agent-harness-optimization.git
cd claude-agent-harness-optimization
git checkout founder-kit-tool-tuning-before-after-2026-06-27
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .

python -m claude_agent_harness_optimization optimize-tools evals/examples/tool_tuning_before_bundle.json --markdown || true
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --markdown
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --heldout-cases "find python files,read known file" --markdown
```

First watch the weak bundle fail. Then run the passing bundle. Use `optimize-tools` for the first contract pass. Use `model-matrix` when the right tool depends on model or harness. Use `grind-harness` only after you have live eval cases and held-out checks.

## Boundary

`claude-founder-kit` keeps the founder journey and one-command recipe. `claude-agent-harness-optimization` keeps the implementation workbench. The boundary is intentional so founder-kit stays small while the companion repo can stay deep.

## Gate

```bash
cd tool_tuning
make check
make test
```

The gate checks the [companion registry](../companions/registry.json), the ledger URL, the local receipt link, the command names, and the no-vendoring boundary.
