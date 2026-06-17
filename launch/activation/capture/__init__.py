"""Step 1, capture: record R-A-R events on one durable id and roll them up.

emit() is the whole capture surface: one server-side call keyed on org_id, opt
out and idempotent. The eleven queries read milestones off the log, to_cohort
rolls the log into the activation-loop contract, and the backends are swappable
(local JSONL by default, PostHog, Statsig, or Amplitude when configured).
"""
