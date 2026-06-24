# MVP, build the product then a security review

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**The MVP stage of a founder workflow kit for Claude builders: build the product, then a security review before any user touches it.**

This repo bundles two co-located tools, one per half of the MVP stage. You build the agent in `build/`, then you review its tool and agent surface in `harden/` before a single user touches it. Claude runs both halves, and a deterministic gate proves each output before it ships. Each tool keeps its own working code, tests, and gate, so you can run them apart or together.

## Value Bar

The MVP tools are candidates until they are adversarially-confirmed to add value for a builder shipping a Claude product. Passing evals, cost receipts, and tool-contract gates proves internal quality. It does not prove user value until a skeptical builder compares the workflow with their baseline and leaves a receipt.

```bash
make setup   # install build/ deps, one time (for the live acts)
make demo    # both demos: the cost receipt, then the before/after lint
make test    # both test suites: the eval-set self-test and the rule suite
make check   # both deterministic gates: the doc-correctness checks
```

## build: from a first call to a deployable agent

[`build/`](build/) is the path from a first Claude API call to an evaluated, cost-engineered agent you can deploy. It runs as five acts:

1. A first streaming call, with tokens and cost visible from minute one.
2. Tools as contracts: give the model hands, and write each tool description as an API contract.
3. Evals before vibes: a golden set with honesty cases, routed across the model ladder and gated per tier, wired into CI.
4. Cost is architecture: the same workload three ways (naive, cached, routed), measured rather than asserted.
5. An MCP encore: the same tools made portable over MCP for Claude Code and Desktop, plus an Agent SDK repo doctor.

Every act runs Claude. The model ladder runs from `claude-haiku-4-5` for cheap lookups up to `claude-opus-4-8`, the stable default for high-consequence work, with the access-gated `claude-fable-5` as the top rung. The model ids live in one place, [`build/models.py`](build/models.py). The live acts need `ANTHROPIC_API_KEY`. `make demo` runs `04_cost_engineering.py --live`, which measures the cost table with about 36 real calls, so it needs `ANTHROPIC_API_KEY` and fails fast without it. The [`build/starter/`](build/starter/) directory is a forkable FastAPI app you deploy to ship a product of your own.

## harden: the security review before any user

[`harden/`](harden/) is the security review you run before any user touches the agent. It turns vague MCP tools into contract-grade interfaces. It reads the wire format an MCP server publishes, the `tools/list` response, and scores each tool against 16 rules, including an OWASP and STRIDE security lens (a raw secret as a model-visible argument, a destructive op with no safety contract, free-form input into a code, shell, SQL, or URL sink) and a tool-discovery check. A vague example server scores 14 out of 100. The contract-grade rewrite scores 100 out of 100. It also grades an agent protocol and a harness manifest.

The rule score is the deterministic gate. It runs offline and reproduces in CI. With a key set, `claude-opus-4-8` rewrites the worst tool from its findings, and the same rules re-score the rewrite. Claude does the judgment, the gate proves it. The rewrite fires only when stdout is a TTY, so the gate stays green offline.

## How the two fit together

The order is the point. `build/` produces an agent with a tool surface, and `harden/` reviews that surface before it ships. The build tool already pressured the first tool contracts into shape in act 2. The harden tool is the standalone review that holds the whole surface to a bar and gates it in CI. Run `build/` to get a working agent, then run `harden/` on its tools before any user sees it.

## Where this fits

This is the **MVP** module of [claude-founder-kit](../README.md). The full journey runs as modules in one repo: first_hour, idea, mvp, launch, scale, quality, cost. The kit names what a founder does at each stage, and these are the runnable tools that do it. Each stage keeps a deterministic gate, and live Claude calls run only where the command says a key is required. One `make demo` from the repo root runs the live walkthrough when a key is set.

## Layout

| Path | What it is |
|---|---|
| [`build/`](build/) | The five-act path to a deployable agent: tools, evals, cost engineering, MCP. Keeps its own package, tests, gate, and forkable starter. |
| [`harden/`](harden/) | The security review: tool contracts, the OWASP and STRIDE lens, the protocol and harness graders. Keeps its own package, tests, and gate. |
| [`build/skills/prompt-to-production/SKILL.md`](build/skills/prompt-to-production/SKILL.md) | The build tool packaged as a Claude Skill. |
| [`harden/skills/agent-linter/SKILL.md`](harden/skills/agent-linter/SKILL.md) | The harden tool packaged as a Claude Skill. |

Each subdir carries its own README, CLAUDE.md, Makefile, and `.doccheck.json`. Run `make check` and `make test` from a subdir to gate that tool alone, or from the repo root to gate both.

## About

All bundled company data is fictional.

MIT licensed.
