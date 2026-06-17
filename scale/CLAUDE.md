# CLAUDE.md

Guidance for Claude Code, or any agent, working in this repo. Read it, then run the gates.

## What this repo is

claude-startup-scale is the Scale stage of Anthropic's Founder's Playbook: build a
go-to-market function, compound usage into a data moat, and turn workflow lock-in
into a switching cost. It scores a cohort into a moat readout and writes the one GTM
motion to run next. The deterministic moat core (`scale/measure/metrics.py`,
`scale/contracts.py`) is stdlib only, carries the receipt, and runs offline. The
Claude layer (`scale/generate/gtm.py`) runs on every human readout and raises a
clear error with no key, so a misconfiguration is loud, not a silent downgrade.

## Run it

```bash
make demo    # the deterministic moat readout from the sample cohort, offline
make test    # the test suite
make check   # the doc-correctness gate
```

No dependencies and no key for the demo. `python3 -m scale examples/cohort.json`
prints the human readout and runs Claude for the GTM motion and the moat narrative.
Add `--json` for the raw deterministic readout offline, or `--min-moat N` for a CI
gate on the median moat that runs before any Claude call.

## How to extend

- The contracts are the spine. `contracts.py` owns the Scale-stage signals, the
  moat weights and caps, the spend and data tiers, and the GTM-ready rule. A number
  cannot drift between the readout and the prompt because both import it from there.
- The moat core is stdlib only and deterministic. The same cohort gives the same
  readout every run, which is why it is the receipt and the CI gate. Re-run the demo
  before changing a number in the docs, do not edit it by hand.
- The Claude layer is mandatory and the only place a model runs. It calls
  `require_client` in `platform/client.py` and raises with no key or no SDK, so a
  missing key fails loud rather than degrading. Keep that boundary: determinism on
  the gate, Claude on the judgment, and the gate verifies the output offline.

## Conventions

- Run `make check` and `make test` before you commit. Both pass offline with no key.
- Prose is plain: no em-dashes, no en-dashes, no semicolons in prose, no buzzwords.
  The deslop gate enforces it on the README in CI. Numbers over adjectives.
- Never commit a key. `.env` stays git-ignored.
- Surgical changes only. Match the existing style. Do not refactor what is not broken.
