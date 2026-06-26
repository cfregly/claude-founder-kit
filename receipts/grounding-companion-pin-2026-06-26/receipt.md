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
- Commit: `c6a51ba73191bf5503dd39de9eb15099e33f41a3`
- Tag: `founder-kit-grounding-ledger-2026-06-26`
- Ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-grounding/blob/c6a51ba73191bf5503dd39de9eb15099e33f41a3/docs/confirmed-improvements.md)

## Pin Bump

- Old pin: `e4e72ff351304b877c9292d6424efdd03dd2c01e`
- New pin: `c6a51ba73191bf5503dd39de9eb15099e33f41a3`
- What changed: added `docs/confirmed-improvements.md`, linked it from README and CLAUDE, and made the deslop gate require the ledger.
- Commands run: `python scripts/deslop_check.py`, `python -m compileall -q context_grounding run.py scripts`, `python -m unittest discover -s tests -q`, and the missing-key `run.py` check.
- Why founder-kit should move: every companion now has its own confirmed-improvements ledger instead of relying on README as the registry ledger.

This receipt does not say the recipe is adversarially-confirmed to add value. It records a
reproducible pointer to the companion workbench.
