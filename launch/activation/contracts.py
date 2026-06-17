"""Canonical contracts every stage agrees on. One source of truth, not three.

The capture, measure, and operate stages all import the loop stages, the
raw-event-to-stage map, the four adoption phases, and the three autonomy gates
from here. Defining them once is why the captured events feed the computation
with no translation layer, and why a number cannot drift between stages.
"""

from __future__ import annotations

# The Relationship -> Activation -> Retention loop, in order. Day 0 is the
# touchpoint. A stage a founder never reached is simply absent.
STAGES = [
    "touchpoint", "signup", "first_call", "first_build",
    "second_build", "weekly_active", "production", "handoff",
]

STAGE_LABEL = {
    "touchpoint": "ecosystem touchpoint",
    "signup": "signup / account",
    "first_call": "first API call",
    "first_build": "first working build",
    "second_build": "second build (unprompted)",
    "weekly_active": "weekly active builder",
    "production": "production pilot",
    "handoff": "GTM handoff (PQA)",
}

# Raw developer-tool events, emitted server-side from the SDK and CLI, that cross
# a milestone line on their first occurrence. Instrument the tool, not the site.
EVENT_TO_STAGE = {
    "ecosystem_touch": "touchpoint",
    "account_created": "signup",
    "api_call": "first_call",           # first successful call crosses first_call
    "build_succeeded": "first_build",
    "api_key_created": "second_build",   # the clearest "committing to build" signal
    "weekly_active": "weekly_active",
    "production_traffic": "production",
    "gtm_handoff": "handoff",
}

# Events that also measure depth or consumption on every occurrence.
VOLUME_EVENTS = {"api_call", "build_step", "tokens", "production_traffic"}

# The aha transition. Signup to first successful call predicts retention better
# than raw volume, so it is the one transition to instrument cleanly.
AHA_FROM, AHA_TO = "signup", "first_call"

# The four developer-adoption phases the funnel rolls up to, as contiguous slices
# of the eight stages, so reading the funnel top to bottom stays sequential.
PHASE = {
    "touchpoint": "Try", "signup": "Try", "first_call": "Try",
    "first_build": "Adopt",
    "second_build": "Build", "weekly_active": "Build",
    "production": "Monetize", "handoff": "Monetize",
}

# Stages that definitionally require a first build. Reaching one with no logged
# first build means the export dropped the first-build milestone, which also
# understates the activation rate.
BUILD_DEPENDENT = ("second_build", "weekly_active", "production", "handoff")

# The three autonomy gates, in order of how much trust an action needs. This
# boundary is the contract that makes a scheduled operator accountable.
ALWAYS = "always"  # safe and internal (measure, draft): runs unattended
ASK = "ask"        # outward-facing: proposed, waits for a human
NEVER = "never"    # refused on a schedule, by design


def stage_for(event_name):
    """The milestone stage an event crosses, or None for a volume-only event."""
    return EVENT_TO_STAGE.get(event_name)


def phase_for(stage):
    """The developer-adoption phase a stage rolls up to."""
    return PHASE.get(stage, "All four")
