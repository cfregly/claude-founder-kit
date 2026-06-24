---
name: activation
description: >-
  Produce the founder-to-builder weekly startup-signal report from a cohort of
  accounts and the loop stages each reached (touchpoint, signup, first call, first
  build, second build, weekly active, production, handoff) plus a spend trend. It
  returns the activation and retention funnel, the activation rate, the biggest
  leak, time-to-second-build, the engagement and leaky-bucket flags, the
  product-qualified accounts ready for a GTM handoff, and the one motion that moves
  the biggest leak, with every outward step gated for human approval. Use when
  someone wants a weekly growth report on a founder or developer cohort, to measure
  an activation funnel, find where it leaks, decide the next motion, or set the
  boundary on what an agent may do on its own. Triggers on "weekly report",
  "startup-signal report", "measure my activation", "where is my funnel leaking",
  "which accounts are ready for sales", "the one motion this week", or "gate the
  agent's outward actions".
---

# Weekly report

Produce the founder-to-builder weekly report from a cohort. The report is an
operating document, not a dashboard: every line triggers a decision.

## Run it

Offline, with no key:

```bash
python -m activation measure cohort.json        # the activation readout
python -m activation operate readout.json --weekly  # the gated weekly report
```

Live, with `ANTHROPIC_API_KEY`:

```bash
make demo                                       # enrich -> decide -> draft -> render
```

## The cohort shape

Each account carries the stages it reached, the day it reached each (day 0 is the
touchpoint), and a spend trend (up, flat, down):

```json
{
  "cohort": "Q3 founder day",
  "accounts": [
    {"name": "acct_01", "spend_trend": "up",
     "reached": {"touchpoint": 0, "signup": 0, "first_call": 1,
                 "first_build": 3, "second_build": 9, "production": 20, "handoff": 25}}
  ]
}
```

## What it returns

- The funnel, the activation rate, and time-to-first-value.
- Time-to-second-build, the leading indicator, and the retention and engagement
  rates with a leaky-bucket flag, judged against the AI-native bar.
- The product-qualified accounts ready for handoff, named.
- The one motion tied to the biggest leak, with the metric it moves.
- The gate ledger: what ran on its own, what waits on you, and what the operator
  will not do unattended.

## The gate

Only measurement and drafting run unattended. The outward motions (the
second-build nudge, the build clinic, the GTM handoff) are proposed and wait for a
human. Sending mail, spending, posting in public, and granting credits are refused
on a schedule by design. Keep that boundary: determinism on the gate, Claude on
the draft.
