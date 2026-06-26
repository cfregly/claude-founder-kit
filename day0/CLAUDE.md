# CLAUDE.md

Conventions for the day-0 trust path.

## Purpose

This stage keeps the minimum trust and safety controls visible before a live Claude app touches
customer data or takes action. The controls are evals, permissions, monitoring, rollback, and
stopping conditions.

## Value Bar

The stage is a candidate until it is adversarially-confirmed to add value. Do not claim it proves
production safety. It proves the local control shape runs and can be inspected.

## Editing Rules

- Keep the demo deterministic and keyless.
- Keep the control names literal: evals, permissions, monitoring, rollback, stopping conditions.
- If a new control is added to README prose, add a fixture or check for it.
- Do not add live API calls to this stage. Link to the live stages instead.
