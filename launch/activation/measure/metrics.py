"""Measure a founder cohort through the Relationship -> Activation -> Retention loop.

Input is a cohort dict from the capture stage:

    {"cohort": "...", "accounts": [
        {"name": "acct_01", "spend_trend": "up",
         "reached": {"touchpoint": 0, "signup": 0, "first_call": 0,
                     "first_build": 2, "second_build": 9, "production": 20,
                     "handoff": 25}}]}

`reached` maps a loop stage to the day it happened (day 0 is the touchpoint).
Stages a founder never reached are absent. `spend_trend` is up / flat / down.
Everything below is deterministic and explainable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import statistics
from typing import Any

from .. import contracts

STAGES = contracts.STAGES
STAGE_LABEL = contracts.STAGE_LABEL
BUILD_DEPENDENT = contracts.BUILD_DEPENDENT


def _reached(accounts: list[dict], stage: str) -> list[dict]:
    return [a for a in accounts if stage in (a.get("reached") or {})]


def _day(account: dict, stage: str):
    return (account.get("reached") or {}).get(stage)


@dataclass(frozen=True)
class FunnelStage:
    stage: str
    label: str
    count: int
    pct_of_top: float      # share of the top of funnel that got this far
    conv_from_prev: float  # conversion from the previous stage


def funnel(accounts: list[dict]) -> list[FunnelStage]:
    out: list[FunnelStage] = []
    top = len(_reached(accounts, STAGES[0])) or len(accounts) or 1
    prev = None
    for s in STAGES:
        n = len(_reached(accounts, s))
        conv = 1.0 if prev is None else (n / prev if prev else 0.0)
        out.append(FunnelStage(s, STAGE_LABEL[s], n, round(n / top, 2), round(conv, 2)))
        prev = n
    return out


def time_to_second_build(accounts: list[dict]) -> float | None:
    """Median days from first call to the second build, the best early predictor
    of who becomes a logo. Falls back to signup if first call is missing. A
    negative span is out-of-order data, not a result, so those are excluded."""
    days = []
    for a in accounts:
        sb = _day(a, "second_build")
        start = _day(a, "first_call")
        if start is None:
            start = _day(a, "signup")
        if sb is not None and start is not None and sb - start >= 0:
            days.append(sb - start)
    return round(statistics.median(days), 1) if days else None


def biggest_dropoff(stages: list[FunnelStage]) -> dict | None:
    """The largest relative drop in the activation funnel. The handoff gate is
    excluded on purpose: it is selective by design, not a leak."""
    worst = None
    for prev, cur in zip(stages, stages[1:]):
        if cur.stage == "handoff" or prev.count == 0:
            continue
        lost = 1.0 - cur.count / prev.count
        if worst is None or lost > worst["lost_pct"]:
            worst = {"from": prev.stage, "to": cur.stage, "lost_pct": round(lost, 2)}
    return worst


def pqas_ready(accounts: list[dict]) -> list[str]:
    """Product-qualified accounts ready for a named GTM owner: in production, a
    rising spend trend, and not handed off yet. Sustained usage is the trigger."""
    out = []
    for a in accounts:
        reached = a.get("reached") or {}
        if "production" in reached and "handoff" not in reached \
                and a.get("spend_trend") == "up":
            out.append(a.get("name", "<unnamed>"))
    return out


def data_integrity(accounts: list[dict]) -> list[str]:
    """Flag a messy cohort export before its rates get trusted: an account in a
    post-build stage with no first build, or an out-of-order span. The readout is
    only as honest as the export."""
    issues: list[str] = []
    broken = [a.get("name", "<unnamed>") for a in accounts
              if "first_build" not in (a.get("reached") or {})
              and any(s in (a.get("reached") or {}) for s in BUILD_DEPENDENT)]
    if broken:
        shown = ", ".join(broken[:3]) + (" ..." if len(broken) > 3 else "")
        issues.append(
            f"{len(broken)} account(s) reached a post-build stage with no first "
            f"build ({shown}). Impossible funnel: the first-build milestone is "
            "missing, which also understates the activation rate. Fix the export.")
    out_of_order = 0
    for a in accounts:
        sb = _day(a, "second_build")
        start = _day(a, "first_call")
        if start is None:
            start = _day(a, "signup")
        if sb is not None and start is not None and sb < start:
            out_of_order += 1
    if out_of_order:
        issues.append(
            f"{out_of_order} account(s) have a second build dated before the "
            "first call. Out-of-order timestamps, excluded from "
            "time-to-second-build. Fix the cohort export.")
    return issues


def summarize(cohort: dict) -> dict[str, Any]:
    accounts = cohort.get("accounts", [])
    stages = funnel(accounts)
    built = len(_reached(accounts, "first_build"))
    signed = len(_reached(accounts, "signup")) or len(accounts)
    rebuilt = len(_reached(accounts, "second_build"))
    weekly = len(_reached(accounts, "weekly_active"))
    in_prod = len(_reached(accounts, "production"))
    activation_rate = round(built / signed, 2) if signed else 0.0
    # The retention half of the loop: the second build is the best early
    # predictor, engagement retention is the leading indicator of paid retention,
    # and reaching production is the expansion that wins the renewal.
    retention_rate = round(rebuilt / built, 2) if built else 0.0
    engagement_retention = round(weekly / built, 2) if built else 0.0
    expansion_rate = round(in_prod / weekly, 2) if weekly else 0.0
    leaky = built > 0 and retention_rate < 0.5
    engagement_leak = built > 0 and engagement_retention < 0.5
    ready = pqas_ready(accounts)
    handoffs = len(_reached(accounts, "handoff"))
    ttsb = time_to_second_build(accounts)
    drop = biggest_dropoff(stages)

    flags = data_integrity(accounts)
    if drop and drop["to"] in ("first_call", "first_build"):
        flags.append("Biggest leak is reaching a first build. Every event must end in a working build.")
    elif drop and drop["to"] == "second_build":
        flags.append("Biggest leak is the second build, your activation signal. Tighten the 72-hour follow-up to shorten time-to-second-build.")
    if leaky:
        flags.append(f"Leaky bucket: only {retention_rate*100:.0f}% come back for a second build. The second build is the activation-to-retention bridge; tighten the 72-hour follow-up.")
    if engagement_leak:
        flags.append(f"Engagement leak: only {engagement_retention*100:.0f}% of builders become weekly-active. Engagement retention is the leading indicator of paid retention; if they do not return weekly, the renewal will not be there.")
    if ready:
        flags.append(f"{len(ready)} product-qualified account(s) not handed off. Package context and hand to a named GTM owner within 5 business days.")
    if not flags:
        flags.append("Healthy loop. Keep credits milestone-gated so they qualify intent, not vanity signups.")

    return {
        "cohort": cohort.get("cohort", "unnamed cohort"),
        "accounts": len(accounts),
        "funnel": [asdict(s) for s in stages],
        "activation_rate": activation_rate,
        "retention_rate": retention_rate,
        "engagement_retention": engagement_retention,
        "expansion_to_production": expansion_rate,
        "leaky_bucket": leaky,
        "engagement_leak": engagement_leak,
        "time_to_second_build_days": ttsb,
        "biggest_dropoff": drop,
        "pqas_ready_for_handoff": ready,
        "the_number": {
            "primary": "qualified PQA handoffs",
            "handoffs_this_cohort": handoffs,
            "leading_indicator": "time-to-second-build (days)",
            "value": ttsb,
        },
        "flags": flags,
    }
