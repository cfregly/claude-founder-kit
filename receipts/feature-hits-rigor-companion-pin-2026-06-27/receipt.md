# Value Receipt: Feature Hits Rigor Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to promoted Claude feature proofs
Baseline: founder-kit pinned a broader feature-hits repo snapshot
Command or artifact tested: `make companion ID=feature-hits`
Objection tried: does founder-kit point at stale public hits after the radar gate demotes candidates
Outcome axis: repo boundary and reproducibility
Observed result: founder-kit points to a pinned feature-hits commit whose public surface contains only the surviving PTC proofs
Decision: keep as candidate until a skeptical builder runs the promoted proofs on a real workload
Follow-up: update this receipt when the feature-hits pin changes

## Pinned Companion Snapshot

- Repo: [claude-feature-hits](https://github.com/cfregly/claude-feature-hits)
- Commit: `bbcd7731df693159b8f666680e69e04991dba008`
- Tag: `founder-kit-feature-hits-rigor-2026-06-27`
- Ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-feature-hits/blob/bbcd7731df693159b8f666680e69e04991dba008/docs/confirmed-improvements.md)

## Commands Run

```bash
cd /Users/admin/dev/anthropic/takehome-experiments/claude-feature-hits
make ci
ANTHROPIC_API_KEY=... make check
git tag founder-kit-feature-hits-rigor-2026-06-27
git push origin main
git push origin founder-kit-feature-hits-rigor-2026-06-27
```

## Pin Bump

- Old pin: `842034c4dcd72cf6fe065eb7e9f57eaac2ed4f5a`
- New pin: `bbcd7731df693159b8f666680e69e04991dba008`
- What changed: feature-hits removed stale public accuracy and Operations artifacts that the current radar adversarial gate marks below the promoted bar, leaving the PTC token proof and cache/context cost proof.
- Commands run: `make ci`, `ANTHROPIC_API_KEY=... make check`, `make companion ID=feature-hits`, `make check-companions`, and `make check-companions CLONE=1`.
- Why founder-kit should move: founder-kit should direct builders to the current reproducible proof surface, not a stale broader snapshot.

This receipt does not say the feature proofs are externally confirmed to add value. It records a
reproducible pointer to the current companion proof repo.
