# Cost, the platform cost levers

A runnable reference for cutting your Claude bill: **one small, correct demo of each cost lever**,
in one repo. Every demo makes a real API call and reads the saving off the usage object.

```bash
pip install -r requirements.txt

ANTHROPIC_API_KEY=... python run.py                  # every lever, real calls
ANTHROPIC_API_KEY=... python run.py prompt_caching   # one lever, real call
```

This is a real tool. Every run calls the Anthropic API, so `ANTHROPIC_API_KEY` is required. Without
a key it fails fast with a clear error and a non-zero exit. There is no offline mode and no fallback.

## A note on scope

This stage is about **Claude platform cost**: the token-spend knobs the API gives you. It is not
about GPU or serving cost, which live in the separate [`claude-gpu-perf-tune`](https://github.com/cfregly/claude-gpu-perf-tune). Every demo is built
on shipped primitives and the request shapes are current. Where a lever is beta, the demo labels it
and does not pretend otherwise.

## The levers

Reach for them in this order: cut what you send, tune how hard it thinks, measure, then halve the
rest with batch.

| Lever | What it saves |
|---|---|
| `prompt_caching` | a cache read is about a tenth of input price, and the demo proves the hit from `usage` |
| `context_editing` | prunes stale tool results, so every later turn carries fewer tokens |
| `tool_search` | loads tool schemas on demand instead of paying for 50k+ tokens of schema every call |
| `programmatic_tool_calling` | keeps large intermediate tool output in the script, out of the context you pay for |
| `thinking_effort` | adaptive thinking plus effort (low through max) tunes the thinking tokens you buy |
| `token_counting` | exact, model-specific counts before you send, so you budget and catch blowups early |
| `batch` | the Batches API runs anything non-interactive async at 50% of the token price |

This stage also ships a `verify` skill and a Stop hook under `.claude/`, which is the skills and
hooks feature demonstrating itself.

## Measured: carrying fewer tokens

The levers split into two axes. Axis one is **do not pay for the same tokens twice**: prompt
caching and routing. That is measured in the kit's `mvp/` stage, where caching plus routing cut a
12-question workload from $0.22 to $0.03, about 86 percent.

This stage measures axis two: **do not carry tokens you do not need**. The same six-turn tool loop,
run three ways on Haiku, every number read from `usage.input_tokens` on the real calls:

| strategy | model | turns | total input tokens | output tokens | cost | vs naive |
|---|---|---|---|---|---|---|
| naive (keep every full tool result) | claude-haiku-4-5 | 6 | 140,020 | 96 | $0.1405 | baseline |
| trimmed (carry a one-line stub) | claude-haiku-4-5 | 6 | 43,945 | 101 | $0.0445 | -68% |
| edited (context-management beta clears stale tool_uses) | claude-haiku-4-5 | 6 | 43,809 | 114 | $0.0444 | -68% |

```bash
ANTHROPIC_API_KEY=... python run.py context_receipt
```

By the last turn the naive run resends every earlier document on every call, so its input grows
turn over turn. Trimming rewrites history on the client, carrying a one-line stub once a result has
been used. Context editing prunes the same stale tool results server-side under the
context-management beta. Both land near 68 percent on this loop. Numbers move run to run, so
rerun and quote your own.

One caution where the two axes meet: trimming and context editing rewrite the message history,
which is the cached prefix, so they invalidate the cache from the edit point forward. Caching wants
a frozen prefix, pruning rewrites it. Sequence them: cache the stable prefix, keep the growing
turns at the end, and prune or compact only when the window is near its limit or the cache has
already gone cold.

## Order of operations for a real bill

1. Measure with `token_counting` so you know where the tokens are.
2. Cache the stable prefix with `prompt_caching`. This is usually the largest single win.
3. Stop carrying dead weight: `context_editing`, `tool_search`, `programmatic_tool_calling`.
4. Right-size the thinking with `thinking_effort`. Easy turns do not need high effort.
5. Move everything non-interactive to `batch` for the standing 50% cut.

## Layout

```
cost_control/
  client.py    # the real client, key required, and model routing
  demos.py     # one function per lever, plus the registry
run.py         # one-command entry: all levers, or one, all live
scripts/       # the self-contained deslop gate for CI
.claude/       # the verify skill and the Stop hook (skills + hooks, demonstrated)
```

## Where this fits

This is the `cost/` stage of [claude-founder-kit](../README.md),
Anthropic's Founder's Playbook as runnable code: the founder journey from a first Claude call to a
scaling read, one repo, a co-located tool per stage. Claude runs the judgment on every stage, and a
deterministic gate verifies the output before it ships.

- `first_hour/` the platform ladder, one call up to a managed agent
- `idea/` validate the signal, lint the raise
- `mvp/` prompt to production, then a tool security review
- `launch/` capture a cohort, measure activation, gate the weekly motion
- `scale/` score the data moat and the next GTM motion
- `quality/` the de-slop linter
- `cost/` the platform cost levers (this stage)

## License

MIT.
