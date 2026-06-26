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
- Commit: `e2364b026401aafe6aa77aeb87a29809b096800a`
- Tag: `founder-kit-managed-agents-2026-06-26`
- Ledger: [README.md](https://github.com/cfregly/claude-managed-agents/blob/e2364b026401aafe6aa77aeb87a29809b096800a/README.md)

This receipt does not say the recipe is adversarially-confirmed to add value. It records a
reproducible pointer to the companion workbench.
