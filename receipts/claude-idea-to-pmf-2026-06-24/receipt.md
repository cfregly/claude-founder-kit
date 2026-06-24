# Value Receipt: Claude Idea to PMF Startup Trial

Status: candidate, not external proof.

Date: 2026-06-24.

Reviewer role: internal founder-operator.

Workflow: shape Claude Idea to PMF, a startup that helps everyday founders move from raw idea to buyer evidence.

Baseline: [baseline.md](baseline.md).

Pitch tested: [pitch.md](pitch.md).

External proof protocol: [external-proof-plan.md](external-proof-plan.md).

Live outputs from the original working-name run:

- [idea_score.txt](idea_score.txt)
- [live_idea_intervention.txt](live_idea_intervention.txt)

## Decision So Far

The current wedge is:

> Help first-time, nontechnical founders send five buyer-specific outreach notes in seven days and make one continue, narrow, or kill decision from real replies.

That is narrower than "take an idea to product-market fit" and easier to test with skeptical users.

## Founder-Kit Output

Deterministic idea score:

```text
startup-signal - pitch: 8/10
```

Live intervention ran with `ANTHROPIC_API_KEY` from the local ignored `.env`.

The intervention strengthened the wedge:

> Get five real buyer conversations or one honest kill decision in seven days, before you waste months building the wrong thing.

It also changed the product emphasis:

- sell the kill decision, not an AI company operating system
- make the five outreach notes the hero workflow
- add a concierge tier before automating the whole system
- route routine work to a cheaper model and reserve the strongest model for skeptical evidence review
- cache the evidence rubric and anti-false-confidence rules
- track the percent of users who send all five notes as the top activation metric

## Internal Objection Captured

The strongest objection is that generated outreach may not beat a plain template or a free chatbot. The first external proof must compare the notes against a baseline and measure whether the user actually sends them or changes course.

## What Does Not Count Yet

- This is not external skeptical-user proof.
- This does not show that common folks will pay.
- This does not show that Paperclip is the right substrate.
- This does not show product-market fit.

## Next Receipt Needed

Run Session 1 from [external-proof-plan.md](external-proof-plan.md) with a real first-time founder. The receipt only upgrades if the founder had room to reject the output and still used or changed something because of it.
