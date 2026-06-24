# Founder Activation Field Guide

An operator field guide for turning founders into builders on Claude. It is the human
process that runs alongside the launch module's code: the loop the code measures, the motions a
person runs, and the line where a person stops and the gate takes over. Every number here
reproduces from the launch module's deterministic spine (seeded at 7) or traces to saved evidence.

Read it with `CLAUDE.md`. State facts, trace numbers to evidence, deslop before shipping.

Value bar: this guide is a candidate until it is adversarially-confirmed to add value against an operator's baseline activation motion. Treat the reference cohort as mechanical evidence, not field proof.

## 1. Thesis

Activation is the work: get a founder from a first Claude call to a working build to a second build
they start on their own, then keep them. The demo wins the trial. The eval set wins the renewal.
This guide turns that loop into a repeatable motion with saved output, so a win for one founder
becomes a recipe the next founder runs from.

## 2. Who it is for

Founders and founding engineers shipping a product on Claude. Technical go-to-market and partner
teams who run founder programs. Accelerator and VC partners who want their portfolio building, not
just signed up. The reader is doing specific work: a product copilot, an agent over tools and MCP,
a support flow over their own documents.

## 3. The loop, not a funnel

Relationship, then activation, then retention. One line each:

- **Relationship.** Earn trust before any build. Partners, communities, office hours, build in
  public. Trust is the entry, and it is perishable.
- **Activation.** Get to first value fast. First API call same-day, first working build inside 7
  days. Instrument the aha, which is the signup-to-first-call step.
- **Retention.** Keep them and grow them. Second build, weekly active building, production traffic,
  expansion. For an AI product the eval set is the moat.

It is a loop because retained founders recruit the next room, so retention feeds the top of the
next cohort. The launch module measures the loop as eight stages on one durable id: ecosystem
touchpoint, signup, first API call, first working build, second build (unprompted), weekly active
builder, production pilot, and GTM handoff. A founder who never reached a stage is simply absent
from it.

## 4. The activation motion

One founder session, four moves, every one ending in working code.

- **The diagnostic (about 30 minutes).** What are you building, what does it do for your users, and
  what does the workload look like: the task, the agent shape, the request volume, the document
  set, the long-running job. Name the one Claude feature that changes that workload.
- **The workshop (60 to 90 minutes).** Build one working integration live against the founder's
  real workload. Pick the format that maps to their pain (section 5). Every session ends in code
  that runs, not a slide.
- **The follow-up (inside 72 hours).** Office hours on the build, plus the measured run: what the
  change did to cost, speed, reliability, accuracy, or security on their workload.
- **The next step.** One repo, one file to edit, one command to run, one cost and time estimate.
  Then the second build is theirs to start.

## 5. Workshop formats

Five formats, each tied to a founder pain, a Claude surface, and saved output. Lead with the pillar
blocking the next production step: cost, speed, reliability, accuracy, or security.

**a. Cost is architecture, not accounting.**
- Founder pain: the token bill climbs with usage and nobody knows which call is expensive.
- The change: route by consequence (Haiku for lookups, Sonnet as the workhorse, Opus and Fable for
  high-consequence agentic work), cache the stable context so it never resends at full price, and
  clear stale tool results from the window.
- Measured run: routing and caching cut a 12-question workshop run from $0.22 to $0.03, about 85% lower
  (`../mvp`). Context editing cut carried tokens 68% on a multi-turn run (`../cost`). Both measured
  off the usage object, not asserted.

**b. Speed is a workflow choice.**
- Founder pain: the agent does the right thing, but the user waits too long or the large deliverable
  needs multiple fragile turns.
- The change: move bulky work into code execution, use programmatic tool calling for fan-out, choose
  fast paths only when the quality bar holds, and use extended output when one un-truncated turn is
  the product.
- Measured run: the feature-hit briefs cover bulk output for one large deliverable and exact-ledger
  work where the same exact answer completes faster than the exact competitor arms.

**c. Governed agent reliability.**
- Founder pain: the agent works in the demo and falls over in production when a tool fails or the
  context fills.
- The change: treat tool descriptions as API contracts, keep durable state outside the model, and
  put a governor on the loop (gates and stop conditions). For long-running work, use managed
  sessions and the memory tool so an agent survives a restart and carries what it learned.
- Saved output: [`claude-managed-agents`](https://github.com/cfregly/claude-managed-agents) runs one real
  end-to-end agent under the `managed-agents-2026-04-01` beta, provision to teardown.
  [`claude-memory`](https://github.com/cfregly/claude-memory) runs the memory tool plus a two-day
  consolidation loop and measures the delta.
  [`claude-parallel`](https://github.com/cfregly/claude-parallel) runs a bounded, measured fan-out of
  concurrent calls.

**d. Accuracy is the answer plus the source.**
- Founder pain: the demo impresses, then quality drifts and the customer leaves.
- The change: write the eval set that encodes the customer's definition of good, run it in CI, and
  use Citations when the user needs to verify the source behind an answer.
- Saved output: the `../mvp` module frames the eval set as the retention instrument and gates the
  build on it. `claude-feature-hits` adds PDF, text, search-result, and web citation briefs when a
  founder's workload is answering over their own documents.

**e. Security is the production gate.**
- Founder pain: an agent can read private data, call tools, or act through MCP before the team has
  named the boundary.
- The change: run a tool-boundary review before the first user, add prompt-injection evals and
  destructive-action rules, then map enterprise needs to CMEK, the Compliance API, Claude Security,
  enterprise-managed MCP auth, connector action restrictions, or self-hosted sandboxes.
- Saved output: the `../mvp/harden` module scores the MCP and agent surface with an OWASP and STRIDE
  lens before any user touches it.

Source-grounded answers with citations stay a deep-dive
([`claude-grounding`](https://github.com/cfregly/claude-grounding)), pulled when a founder's workload
is answering over their own documents, not one of the three headline formats.

## 6. The feedback loop

Every session produces more than a build.

- **Capture.** What the founder is building, the workload shape, the one feature that moved the
  number, and the blocker that stopped them. Emitted as events on one durable id, opt-out, so the
  cohort scores itself.
- **Objections become docs and demos.** A recurring objection the platform answers today becomes a
  public recipe, a runnable demo with saved output. One that needs a feature becomes a product note
  routed to the platform team. Track which, and how many.
- **Wins become recipes.** Every repeatable win ships as a runnable demo, so the next founder
  starts from working code, not a blank page. The recipes pull inbound, which refills the top of
  the loop.

## 7. Metrics

The launch module computes these every run, so the guide reads them, it does not invent them.

- **Activation.** Signups, the activation rate (first build over signup), time-to-first-value
  (signup to first call), and the biggest leak.
- **Retention.** Time-to-second-build, the leading indicator. The retention rate (second build over
  first build) with a leaky-bucket flag that trips under 50%. Engagement retention (weekly active
  over first build). Judged against the AI-native bar, not the enterprise bar.
- **Pipeline.** The product-qualified accounts ready for a named GTM owner, and the net-new logos
  attributable.
- **The one motion.** The single motion tied to the biggest leak, with the metric it moves.

The reference cohort, the launch module's deterministic spine seeded at 7, is the worked example:
12 accounts, 165 events, the funnel 12 / 12 / 10 / 8 / 5 / 4 / 3 / 1, activation 67%, retention
62%, time-to-first-value 2.0 days, an 8-day time-to-second-build, and 2 product-qualified accounts
ready for handoff. The cohort is fictional, so these are a reproducible reference, not a field
result. Point the loop at a real cohort and the same code reports the real numbers.

## 8. The 90-day ramp

Three phases: instrument and learn, ship the kit, then measure the next scale step. The milestones are targets the
weekly loop drives toward, read off the launch module's metrics, not a separate cadence. The
reference cohort above is the bar each target is measured against.

**Days 0 to 30, instrument and learn.**
- Ride along the existing motion: partner days, office hours, founder calls. Map the funnel on one
  durable id: touchpoint, signup, first call, first build, pilot, logo.
- Agree one definition of activated across go-to-market, product, and partnerships. The standard: a
  developer known by name, a first API call, Claude in their product, inside 7 days.
- Stand up the weekly startup-signal report: objections, friction, and product gaps, each with
  repro code.
- Exit: the funnel is instrumented and scoring, and the biggest leak is named. In the reference
  cohort the first leak to watch is first call to first build, the activation step.

**Days 31 to 60, ship the kit.**
- Ship the activation kit to founders (anchor: `claude-founder-kit`). Run two accelerator or VC
  cohorts and one office-hours sprint, plus a weekly build-with-Claude guide.
- Ship three quickstarts that map to the headline formats: a product copilot, a tool-contract and
  governed-loop hardening pass, and routing with evals in CI.
- Stand up the conversion read: activation by partner and channel.
- Exit: the motion runs at cohort volume without a bottleneck on one person, and time-to-second-
  build is measured and trending toward the 8-day reference, not widening as volume grows.

**Days 61 to 90, measure and scale.**
- Run a flagship build-a-thon: first API call same-day, working build inside 7 days.
- Write the operator guide v1: ecosystem to activation, the motion another operator can run.
- Publish the 90-day readout: activated developers, the second-build rate, pilots, and partner
  return. Route the top 5 frictions to product issues with repro code.
- Hand the product-qualified accounts to a named GTM owner, each with the measured handoff packet: what they built,
  their usage, their spend trend. In the reference cohort that is 2 accounts ready.
- Exit: net-new production logos from the cohort, a measured demo-to-adoption rate, and a public
  recipe library founders find on their own.

Each phase feeds the next. The day-30 objection log becomes the day-60 quickstarts and guides. The
day-60 cohort data becomes the day-90 retention and handoff work. The day-90 recipes refill the top
of the loop for the next quarter.

## 9. The gate

The loop runs on a schedule, and a person stays accountable for everything outward. The launch
module enforces the boundary in code and proves it with an audit.

- **Runs on its own.** Re-score the cohort, flag the biggest leak, draft the report. Internal and
  safe.
- **Waits for approval.** The second-build nudge, the build clinic, the GTM handoff. Outward, so a
  person approves each one.
- **Refused on a schedule, by design.** Send mail in your name, spend, post in public, grant
  credits, or hand off an account that has not earned it.

Claude drafts the founder message for each gated step. The deterministic gate still decides what
ships, so the copy is written and waiting, never sent on its own.

## Run it

```bash
make demo    # score the reference cohort and print the weekly report (needs ANTHROPIC_API_KEY)
```

Point it at a real cohort and the same code reports the real loop.
