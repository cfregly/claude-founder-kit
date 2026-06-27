# Value Receipt: Prompt Cache Rigor Companion Pin

Status: mechanical receipt
Reviewer role: maintainer
Workflow: point founder-kit users to the prompt-cache diagnostics utility
Baseline: founder-kit pinned a prompt-cache snapshot that lacked the repo-wide value-bar phrase
Command or artifact tested: `make companion ID=prompt-cache`
Objection tried: does the companion look like a promoted feature hit instead of an operations utility
Outcome axis: repo boundary and reproducibility
Observed result: founder-kit points to a pinned prompt-cache commit whose README and agent instructions state the value-bar limit
Decision: keep as candidate until a skeptical builder runs it on a real cache-miss workflow
Follow-up: update this receipt when the prompt-cache pin changes

## Pinned Companion Snapshot

- Repo: [claude-prompt-cache](https://github.com/cfregly/claude-prompt-cache)
- Commit: `5d5d3f1c61143ed482dbd7f0c84c71b1bb79f753`
- Tag: `founder-kit-prompt-cache-rigor-2026-06-27`
- Ledger: [docs/confirmed-improvements.md](https://github.com/cfregly/claude-prompt-cache/blob/5d5d3f1c61143ed482dbd7f0c84c71b1bb79f753/docs/confirmed-improvements.md)

## Commands Run

```bash
cd /Users/admin/dev/anthropic/claude-prompt-cache
make ci
ANTHROPIC_API_KEY=... make check
git tag founder-kit-prompt-cache-rigor-2026-06-27
git push origin main
git push origin founder-kit-prompt-cache-rigor-2026-06-27
```

## Pin Bump

- Old pin: `dfa874e93d4e42f3f968f13fca3a0c9014fee6c0`
- New pin: `5d5d3f1c61143ed482dbd7f0c84c71b1bb79f753`
- What changed: prompt-cache README and agent instructions now say the utility is not adversarially-confirmed to add value without an external builder receipt.
- Commands run: `make ci`, `ANTHROPIC_API_KEY=... make check`, `make companion ID=prompt-cache`, `make check-companions`, and `make check-companions CLONE=1`.
- Why founder-kit should move: founder-kit should point at companion repos that preserve the day-zero trust language and do not overstate utility receipts as value proof.

This receipt records a reproducible companion pin. It is not an external value receipt.
