# Value Receipt: Feature Hits Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to promoted Claude feature proofs
Baseline: founder-kit linked feature-hits in prose but did not pin it in the companion registry
Command or artifact tested: `make companion ID=feature-hits`
Objection tried: does this make founder-kit depend on a moving feature proof repo
Outcome axis: repo boundary and reproducibility
Observed result: founder-kit points to a pinned feature-hits commit and ledger without copying the implementation
Decision: keep as candidate until a skeptical builder runs the promoted proofs on a real workload
Follow-up: update this receipt when the feature-hits pin changes

## Pinned Companion Snapshot

- Repo: [claude-feature-hits](https://github.com/cfregly/claude-feature-hits)
- Commit: `842034c4dcd72cf6fe065eb7e9f57eaac2ed4f5a`
- Tag: `founder-kit-feature-hits-2026-06-26`
- Ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-feature-hits/blob/842034c4dcd72cf6fe065eb7e9f57eaac2ed4f5a/docs/confirmed-improvements.md)

## Commands Run

```bash
cd /Users/admin/dev/anthropic/claude-feature-hits
make ci
make check
git tag founder-kit-feature-hits-2026-06-26
git push origin main
git push origin founder-kit-feature-hits-2026-06-26
```

## Pin Bump

- Old pin: none
- New pin: `842034c4dcd72cf6fe065eb7e9f57eaac2ed4f5a`
- What changed: added `docs/confirmed-improvements.md` to feature-hits and pinned the repo from founder-kit.
- Commands run: `make ci`, `make check`, `make companion ID=feature-hits`, `make check-companions`, and `make check-companions CLONE=1`.
- Why founder-kit should move: founder-kit is the main entry point, and promoted feature proofs need the same reproducible companion boundary as tool tuning, grounding, and Managed Agents.

This receipt does not say the feature proofs are adversarially-confirmed to add value. It records a
reproducible pointer to the companion proof repo.
