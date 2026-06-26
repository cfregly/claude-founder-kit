# Value Receipt: Grounding Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to the companion grounding repo
Baseline: no founder-kit companion registry entry for grounding
Command or artifact tested: `make companion ID=grounding`
Objection tried: does this imply a value claim without a baseline
Outcome axis: repo boundary and reproducibility
Observed result: founder-kit points to a pinned companion commit and README without copying the implementation
Decision: keep as candidate until a skeptical builder runs grounding on a real source workflow
Follow-up: create a stronger companion ledger before upgrading the status

## Pinned Companion Snapshot

- Repo: [claude-grounding](https://github.com/cfregly/claude-grounding)
- Commit: `e4e72ff351304b877c9292d6424efdd03dd2c01e`
- Tag: `founder-kit-grounding-2026-06-26`
- Ledger: [README.md](https://github.com/cfregly/claude-grounding/blob/e4e72ff351304b877c9292d6424efdd03dd2c01e/README.md)

This receipt does not say the recipe is adversarially-confirmed to add value. It records a
reproducible pointer to the companion workbench.
