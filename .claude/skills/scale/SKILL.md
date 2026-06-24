---
name: scale
description: >-
  Score a software cohort into a data-moat readout and the one go-to-market motion
  to run next, at the Scale stage of a founder workflow kit for Claude builders. Given a cohort
  of accounts carrying the Scale-stage signals (integrations built, workflows
  embedded, weekly-active depth, spend trend, data volume, contract tier), it
  computes a moat score (a switching-cost proxy from integration depth, workflow
  lock-in, and usage depth), the moat distribution across deep, forming, and shallow
  bands, the accounts that accrue compounding data, and the expansion-ready set: a
  deep moat with rising spend and sustained use. Then Claude reads those numbers and
  writes the GTM motion and the moat narrative. Use when a growth lead wants to score
  a cohort's moat, find the accounts ready to expand, build the GTM motion, or make
  the case for why an incumbent could not copy the product fast. Triggers on "score
  my moat", "which accounts are ready to expand", "build my GTM motion", "is my moat
  deep enough", "compound data into a moat", or "what is my switching cost".
---

# Scale stage

Value bar: this skill is a candidate until it is adversarially-confirmed to add value against a baseline account-planning or GTM workflow. A moat score is mechanical evidence, not proof of a better decision.

Score a cohort into a moat readout and build the GTM motion. A growth lead runs this
at the Scale stage of a founder workflow kit for Claude builders, once the product has users and
the question turns to widening the gap: compound usage into a moat, lock in the
workflows, and grow the accounts that have earned it.

## Run it

The deterministic readout, offline, with no key:

```bash
python3 -m scale examples/cohort.json --json       # the same, explicitly
python3 -m scale examples/cohort.json --min-moat 40  # a CI gate on the median moat
```

The human readout, which adds the Claude GTM motion and moat narrative:

```bash
make demo
python3 -m scale examples/cohort.json              # needs ANTHROPIC_API_KEY
```

## The cohort shape

Each account carries the Scale-stage signals: the integrations built, the workflows
embedded, the weekly-active depth, a spend trend (up, flat, down), a data volume
(none, low, medium, high), and a contract tier (pilot, team, business, enterprise).

```json
{
  "cohort": "Scale cohort",
  "accounts": [
    {"name": "acct_01", "integrations_built": 5, "workflows_embedded": 4,
     "weekly_active_depth": 6, "spend_trend": "up", "data_volume": "high",
     "contract_tier": "enterprise"}
  ]
}
```

## What it returns

- The moat score per account, a switching-cost proxy from integration depth, workflow
  lock-in, and usage depth, with the band: deep, forming, or shallow.
- The moat distribution, the median moat, and the accounts that accrue compounding
  data.
- The expansion-ready set, named: a deep moat, rising spend, and sustained use.
- From Claude: the one GTM motion (which accounts to target, the play, the reason)
  and the moat narrative grounded in the numbers.

## The boundary

The deterministic moat core is the receipt and the gate, and it runs offline. The
Claude layer runs on the readout and raises a clear error with no key, so a missing
key fails loud rather than degrading. Determinism on the gate, Claude on the
judgment.
