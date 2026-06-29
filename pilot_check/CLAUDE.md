# CLAUDE.md

Conventions for the pilot-check path.

## Purpose

This stage keeps the minimum trust and safety controls visible before a founder's own Claude workflow
touches customer data or takes action. It consumes a programmatic tool calling receipt from that
workflow and checks the proof case, receipt, approval queue, fallback, and kill switch.

## Value Bar

The stage is a candidate until it is adversarially-confirmed to add value. Do not claim it proves
production safety or default launch readiness. It proves the pilot check can inspect a receipt and
keep the access level at pilot candidate unless the evidence supports more.

## Editing Rules

- Keep the demo deterministic and keyless.
- Keep the founder vocabulary literal: proof case, receipt, approval queue, fallback, kill switch,
  pilot check.
- Keep the control names literal where checks depend on them: permissions, logs, monitoring,
  rollback, stopping conditions.
- If a new control is added to README prose, add a fixture or check for it.
- Do not add live API calls to this stage. It may consume a receipt emitted by a live stage.
