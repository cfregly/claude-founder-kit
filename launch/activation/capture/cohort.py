"""Roll the event log up into the cohort shape the measure stage reads.

For each org: the earliest day it crossed each stage, plus a spend trend joined
from billing (a billing event here, Stripe or Orb in production). The output is
exactly the {cohort, accounts:[{name, spend_trend, reached}]} contract the
measure stage consumes, so there is no glue between capture and computation.
"""

from .. import contracts as ev


def _start_ts(rows):
    return min((r["ts"] for r in rows), default=0.0)


def _spend_trend(rows_by_org):
    """Last billing event wins, flat if a billing signal never arrived."""
    trend = "flat"
    for r in rows_by_org:
        if r["event"] == "billing":
            trend = r.get("props", {}).get("trend", "flat")
    return trend


def to_cohort(rows, cohort_name):
    start = _start_ts(rows)
    by_org = {}
    for r in rows:
        by_org.setdefault(r["org_id"], []).append(r)

    accounts = []
    for org, rs in sorted(by_org.items()):
        reached = {}
        for stage in ev.STAGES:
            ts = [r["ts"] for r in rs if r.get("stage") == stage]
            if ts:
                reached[stage] = int((min(ts) - start) // 86400)
        if not reached:
            continue
        accounts.append({"name": org, "spend_trend": _spend_trend(rs), "reached": reached})
    return {"cohort": cohort_name, "accounts": accounts}
