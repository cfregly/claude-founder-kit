"""Synthesize a founder cohort that emits real R-A-R events through emit().

Deterministic at a seed, so the demo reproduces. The journeys are shaped to a
known funnel so the whole pipeline tells one story: 12 signups, 10 first calls, 8
builds, 5 second builds, 4 weekly active, 3 production, 1 handoff. A copy
experiment (first_call_copy) gives the treatment arm a one-day-faster aha, which
the report reads back as the win. The cohort is fictional.
"""

import datetime
import random

from .. import contracts as ev
from .experiments import variant
from .instrument import emit

# Fixed epoch so timestamps do not depend on the wall clock.
START = datetime.datetime(2026, 4, 1, tzinfo=datetime.timezone.utc).timestamp()
EXPERIMENT = "first_call_copy"

# (org_id, deepest stage reached, billing trend). Matches the sample funnel.
JOURNEYS = [
    ("acct_01", "handoff", "up"),
    ("acct_02", "production", "up"),
    ("acct_03", "production", "up"),
    ("acct_04", "weekly_active", "flat"),
    ("acct_05", "second_build", "flat"),
    ("acct_06", "first_build", "flat"),
    ("acct_07", "first_build", "down"),
    ("acct_08", "first_build", "flat"),
    ("acct_09", "first_call", "flat"),
    ("acct_10", "first_call", "flat"),
    ("acct_11", "signup", "flat"),
    ("acct_12", "signup", "flat"),
]


def _ts(day, rng):
    return START + day * 86400 + rng.randint(0, 6) * 3600


def _depth(stage):
    return ev.STAGES.index(stage)


def run(seed=7):
    rng = random.Random(seed)
    for org, maxstage, trend in JOURNEYS:
        arm = variant(org, EXPERIMENT)
        depth = _depth(maxstage)

        emit(org, "ecosystem_touch", ts=_ts(0, rng), variant=arm)
        emit(org, "account_created", ts=_ts(0, rng), variant=arm)
        if depth < _depth("first_call"):
            emit(org, "billing", ts=_ts(1, rng), variant=arm, trend=trend)
            continue

        # first call (the aha). Treatment lands a day sooner.
        d_call = max(1, rng.choice([2, 3]) - (1 if arm == "treatment" else 0))
        for k in range(rng.randint(2, 5)):
            emit(org, "api_call", ts=_ts(d_call + k, rng), variant=arm)
        if depth < _depth("first_build"):
            emit(org, "billing", ts=_ts(d_call + 2, rng), variant=arm, trend=trend)
            continue

        d_build = d_call + rng.choice([2, 3, 4])
        emit(org, "build_succeeded", ts=_ts(d_build, rng), variant=arm)
        for k in range(rng.randint(3, 8)):
            emit(org, "build_step", ts=_ts(d_build + k, rng), variant=arm)
        if depth < _depth("second_build"):
            emit(org, "billing", ts=_ts(d_build + 2, rng), variant=arm, trend=trend)
            continue

        # second build: the API key, the clearest commitment signal.
        d_key = d_build + rng.choice([4, 5, 6])
        emit(org, "api_key_created", ts=_ts(d_key, rng), variant=arm)
        if depth < _depth("weekly_active"):
            emit(org, "billing", ts=_ts(d_key + 2, rng), variant=arm, trend=trend)
            continue

        d_wa = d_key + rng.choice([3, 4, 5])
        emit(org, "weekly_active", ts=_ts(d_wa, rng), variant=arm)
        if depth < _depth("production"):
            emit(org, "billing", ts=_ts(d_wa + 2, rng), variant=arm, trend=trend)
            continue

        d_prod = d_wa + rng.choice([4, 5, 6])
        for k in range(rng.randint(4, 9)):
            emit(org, "production_traffic", ts=_ts(d_prod + k, rng), variant=arm)
            emit(org, "tokens", ts=_ts(d_prod + k, rng), variant=arm, tokens=rng.randint(50000, 200000))
        if depth < _depth("handoff"):
            emit(org, "billing", ts=_ts(d_prod + 3, rng), variant=arm, trend=trend)
            continue

        d_ho = d_prod + rng.choice([4, 5, 6])
        emit(org, "gtm_handoff", ts=_ts(d_ho, rng), variant=arm)
        emit(org, "billing", ts=_ts(d_ho + 1, rng), variant=arm, trend=trend)
