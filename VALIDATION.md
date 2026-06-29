# Validation Status

Current repo status: mechanically vetted, not externally confirmed.

The code, docs, and gates are internally tested. That is not the same as being adversarially-confirmed to add value. The modules remain candidate tools until skeptical users or reviewers test them against real workflows and leave receipts.

## Current Evidence

- Offline `make check` passes.
- Offline `make test` passes.
- Offline `make adversarial` passes.
- Pilot-check controls run keylessly for evals, permissions, logs, monitoring, rollback, and stopping conditions.
- Dependency resolution passes with pinned direct dependencies.
- Live paths are documented as live and key-required.
- Live entrypoints fail cleanly without a key.
- Receipts exist for measured cost outputs.
- The companion registry pins tool tuning, grounding, and Managed Agents repos without copying their implementations.
- One internal founder simulation receipt with live Claude calls exists in [receipts/internal-founder-simulation-2026-06-24/receipt.md](receipts/internal-founder-simulation-2026-06-24/receipt.md).

## Missing Evidence

- Independent founder or operator runs for each stage.
- Baseline comparisons against the current manual workflow.
- Recorded objections from skeptical reviewers.
- Outcome measures by stage, such as time saved, risk caught, cost reduced, activation clarity, pitch clarity, or decision speed.
- External live-path receipts from skeptical users.

## Required Before Strong Claims

Before any stage claims it adds value, add a receipt that follows [VALUE_BAR.md](VALUE_BAR.md). Until then, describe it as runnable, mechanically vetted, or candidate.

Use [TRUST.md](TRUST.md) for the receipt template and stage trust map.
