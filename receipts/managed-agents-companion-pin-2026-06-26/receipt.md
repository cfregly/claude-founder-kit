# Value Receipt: Managed Agents Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to the companion Managed Agents repo
Baseline: no founder-kit companion registry entry for Managed Agents
Command or artifact tested: `make companion ID=managed-agents`
Objection tried: does this imply a value claim without a baseline
Outcome axis: repo boundary and reproducibility
Observed result: founder-kit points to a pinned companion commit and README without copying the implementation
Decision: keep as candidate until a skeptical builder tests Managed Agents against a control path
Follow-up: create a stronger companion ledger before upgrading the status

## Pinned Companion Snapshot

- Repo: [claude-managed-agents](https://github.com/cfregly/claude-managed-agents)
- Commit: `2fa751ab2dc71460dc87307254c30f56f3162dbb`
- Tag: `founder-kit-managed-agents-ledger-2026-06-26`
- Ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-managed-agents/blob/2fa751ab2dc71460dc87307254c30f56f3162dbb/docs/confirmed-improvements.md)

## Pin Bump

- Old pin: `e2364b026401aafe6aa77aeb87a29809b096800a`
- New pin: `2fa751ab2dc71460dc87307254c30f56f3162dbb`
- What changed: added `docs/confirmed-improvements.md`, linked it from README and CLAUDE, and made the deslop gate require the ledger.
- Commands run: `python scripts/deslop_check.py`, `python -m compileall -q managed_agents run.py scripts`, `python -m unittest discover -s tests -q`, and the missing-key `run.py` check.
- Why founder-kit should move: every companion now has its own confirmed-improvements ledger instead of relying on README as the registry ledger.

This receipt does not say the recipe is adversarially-confirmed to add value. It records a
reproducible pointer to the companion workbench.
