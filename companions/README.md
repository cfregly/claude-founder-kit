# Companion Registry

Founder-kit is the front door. Companion repos keep the deep implementation work.

The registry in [registry.json](registry.json) pins each companion repo to a commit, tag, ledger,
local receipt, stage, status, and command list. The pin makes founder-kit stable even when a
companion repo keeps moving.

## Value Bar

A companion recipe is a candidate until it is adversarially-confirmed to add value on a real
workflow. A registry entry proves reproducibility and boundary discipline. It does not prove value
until a skeptical builder compares the companion with a baseline and leaves a receipt.

## Current Companions

| ID | Stage | Status | Repo | Pin |
| --- | --- | --- | --- | --- |
| `feature-hits` | `cost` | candidate | [`claude-feature-hits`](https://github.com/cfregly/claude-feature-hits) | `founder-kit-feature-hits-2026-06-26` |
| `tool-tuning` | `tool_tuning` | candidate | [`claude-agent-harness-optimization`](https://github.com/cfregly/claude-agent-harness-optimization) | `founder-kit-tool-tuning-2026-06-26` |
| `grounding` | `mvp` | candidate | [`claude-grounding`](https://github.com/cfregly/claude-grounding) | `founder-kit-grounding-ledger-2026-06-26` |
| `managed-agents` | `mvp` | candidate | [`claude-managed-agents`](https://github.com/cfregly/claude-managed-agents) | `founder-kit-managed-agents-ledger-2026-06-26` |

## Commands

```bash
make companions
make companion ID=feature-hits
make companion ID=grounding
make check-companions
make check-companions CLONE=1
```

`make check-companions` verifies registry shape, local receipts, repo URLs, ledger URLs, and tag
URLs. `CLONE=1` also clones each pinned tag into a temporary directory and confirms that the tag
resolves to the registered commit.

## Pin Bump Rule

Move a pin only through a receipt update. The receipt must include:

- old pin
- new pin
- what changed
- commands run
- why founder-kit should move

If the companion repo changes after a pin, founder-kit does not move until this process updates the
registry.
