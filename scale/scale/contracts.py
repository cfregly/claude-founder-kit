"""Canonical contracts every stage agrees on. One source of truth, not three.

The measure (moat) stage and the generative stage both import the Scale-stage
signals, the weights of the switching-cost proxy, the spend and data tiers, and
the GTM-ready rule from here. Defining them once is why a number cannot drift
between the deterministic readout and the prompt that grounds the Claude layer.
"""

from __future__ import annotations

# The Scale-stage signals each account carries. The Scale stage is about
# compounding usage into a moat, so these measure depth and lock-in, not the
# early-funnel milestones an activation tool tracks.
SIGNALS = [
    "integrations_built",   # how many of the customer's systems Claude is wired into
    "workflows_embedded",   # how many of their recurring workflows run through Claude
    "weekly_active_depth",  # weekly active seats or runs, the stickiness of daily use
    "spend_trend",          # up / flat / down: the expansion direction
    "data_volume",          # none / low / medium / high: the data accruing in the account
    "contract_tier",        # pilot / team / business / enterprise: the commercial depth
]

# The switching-cost proxy. Moat score = integration depth + workflow lock-in,
# each capped so one runaway signal cannot dominate, then summed to 0..100. A
# customer wired into many systems with many embedded workflows is expensive to
# rip out, which is the moat. Integrations and workflows are weighted because a
# rebuilt integration is a quarter of work and an embedded workflow is a habit.
INTEGRATION_POINTS = 8      # points per integration built
INTEGRATION_CAP = 40        # integration depth caps here (5 integrations)
WORKFLOW_POINTS = 10        # points per workflow embedded
WORKFLOW_CAP = 40           # workflow lock-in caps here (4 workflows)
DEPTH_POINTS = 4            # points per weekly-active-depth unit
DEPTH_CAP = 20              # usage depth caps here
MOAT_MAX = INTEGRATION_CAP + WORKFLOW_CAP + DEPTH_CAP  # 100

# The bar an account clears to count as a deep moat (high lock-in).
HIGH_MOAT = 60

# Spend trend, the expansion direction. Only a rising trend qualifies an account
# for the GTM-ready set: a deep moat that is not expanding is retained, not grown.
SPEND_TRENDS = ("up", "flat", "down")
RISING = "up"

# Data volume tiers, lowest to highest. The compounding-data signal fires when
# the account holds enough proprietary data that the moat widens on its own:
# every week of usage adds context a fresh competitor would have to re-earn.
DATA_TIERS = ("none", "low", "medium", "high")
COMPOUNDING_DATA = ("medium", "high")  # at or above this tier the data compounds

# Contract tiers, lowest to highest commercial depth.
CONTRACT_TIERS = ("pilot", "team", "business", "enterprise")

# Weekly-active-depth bar for the GTM-ready rule: sustained daily use, not a pilot
# that logs in once a week.
HIGH_DEPTH = 4

# The three autonomy gates, in order of how much trust an action needs. The
# deterministic readout and the GTM motion are internal and run on their own; the
# outward GTM steps wait for a human; a fixed set is refused on a schedule.
ALWAYS = "always"  # safe and internal (score, flag, draft the motion): runs unattended
ASK = "ask"        # outward-facing (the expansion offer, the exec brief): waits for a human
NEVER = "never"    # refused on a schedule, by design


def data_tier_index(tier: str) -> int:
    """The rank of a data-volume tier, or -1 for an unknown value."""
    return DATA_TIERS.index(tier) if tier in DATA_TIERS else -1


def contract_tier_index(tier: str) -> int:
    """The rank of a contract tier, or -1 for an unknown value."""
    return CONTRACT_TIERS.index(tier) if tier in CONTRACT_TIERS else -1
