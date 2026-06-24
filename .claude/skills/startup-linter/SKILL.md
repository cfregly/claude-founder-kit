---
name: startup-linter
description: >-
  Diagnose an AI startup with Claude. Score a founder pitch on value
  proposition, urgency, differentiation, platform risk, distribution, and data
  boundary. Score the Relationship, Activation, Retention growth spine and name
  the weakest stage to fix first. Sort the AI use cases into Dot (ship now),
  Dash (build next), Star (the vision bet), and run the office-hours forcing
  questions. Use when a founder wants a product, GTM, or architecture
  diagnosis, a path to product-market fit, a platform-risk answer, a model
  route, a week-one activation metric, or a growth-readiness read. Triggers on
  "diagnose my startup", "score my pitch", "is this a good wedge", "platform
  risk", "what should I build with Claude", "growth readiness", "activation
  metric", or "founder office hours".
---

# startup-linter

Value bar: this skill is a candidate until it is adversarially-confirmed to add value against a founder's baseline wedge or product decision process. Scores focus the review, but they do not prove usefulness.

A founder runs this at the Idea stage of a founder workflow kit for Claude builders, to validate before they build. It scores raw startup signal into product, GTM, and architecture decisions. Built on the Claude Developer Platform: claude-opus-4-8 reads the deterministic scores and writes the founder intervention on every run. The scoring is the gate that runs offline, and the intervention needs ANTHROPIC_API_KEY set.

Turn messy founder signal into a sharper product, GTM, and architecture
decision in one sitting. Deterministic scoring first, then a Claude
intervention, so the advice is grounded in the same numbers every run.

## Workflow

### 1. Intake
Collect the pitch, website copy, or README. One paragraph is enough to start.

### 2. Score the signal
The deterministic scores are a fast, explainable triage signal that focuses the
Claude intervention on the weak dimensions. They are not the final grade: the
judgment is the intervention in step 4. Run the scorers (the repo exposes them
as functions and MCP tools):
- `score_startup_signal`: value prop, urgency, differentiation, platform risk, distribution, data boundary.
- `score_growth_readiness`: the Relationship, Activation, Retention spine, with the weakest stage named.
- `classify_ai_use_cases`: Dot (small, proven, ship now), Dash (connective, build next), Star (high-ceiling bet).

### 3. Run office hours
`founder_office_hours` and `founder_growth_office_hours` return the forcing
questions for the weak spots: why now, why not the frontier labs or the cloud,
what compounds, the data boundary, the unit economics, and the retention loop
(net dollar retention above 100%, engagement retention as the leading indicator).

### 4. Produce the intervention
A founder-ready brief: a one-sentence value-prop rewrite, the 30-day wedge, the
architecture decision (model routing, tools and MCP, prompt caching, data
boundaries, evals), the platform-risk answer, and the metrics to watch this
week (first build, second build, engagement retention).

### 5. Route the model
`route_claude_model` picks Haiku for lookups, Sonnet for synthesis, Opus or
Fable for high-consequence work, and flags when caching and human review apply.

## What NOT to do
- Never invent a fact about the company. Label every assumption.
- Never let a big reach number stand in for a real outcome. Activation that
  does not retain is the AI-tourist trap.
- Never skip the platform-risk question because the demo looks good.
