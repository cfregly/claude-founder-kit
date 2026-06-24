# CLAUDE.md

Conventions for any agent working on the `cost/` stage of claude-founder-kit. Read this first.

## What this is

A runnable reference for cutting your Claude bill: one small, correct demo of each cost lever, in
one repo. Prompt caching, context editing, tool search, programmatic tool calling, adaptive
thinking and effort, token counting, and the Batches API. Each demo makes a real API call and
reports what came back, with the numbers read from the usage object.

This stage is about Claude platform cost, the token-spend knobs the API gives you. It is not about
GPU or serving cost, which live in the separate `claude-gpu-perf-tune`. It is the `cost/` stage of
claude-founder-kit, the cost discipline alongside the de-slop linter in `quality/`. It is built on
shipped primitives. Where a lever needs a beta, the demo says so and never fakes a call.

## Value Bar

Apply [../VALUE_BAR.md](../VALUE_BAR.md). A cost lever is not called valuable until it is adversarially-confirmed to add value on a real workload against a baseline bill or token trace. Receipts are mechanical evidence only.

## Run it

    pip install -r requirements.txt
    ANTHROPIC_API_KEY=... python run.py                  # every lever, real calls
    ANTHROPIC_API_KEY=... python run.py prompt_caching   # one lever, real call

## Rules

- Key required, fail fast. Every run calls the real Anthropic API, so `ANTHROPIC_API_KEY` is
  required. Without a key the run fails fast with a clear error and a non-zero exit. There is no
  offline mode and no fallback.
- Numbers are receipts. Every number a demo prints comes from the usage object on the real call,
  never from memory.
- Stay in scope. This stage is platform token cost. GPU and kernel cost live in claude-gpu-perf-tune.
- Claim only what runs. Beta levers are labeled, not demonstrated as if GA.
- Prose is deslop-clean: no em-dashes, no en-dashes, no semicolons, no buzzwords. CI runs the
  deslop gate on the README and this file, a compile check, and a fail-fast-without-a-key check.
- Never commit a key. `.env` stays git-ignored.
