"""Render the weekly startup-signal report: the deliverable.

This is the artifact the role ships every Monday. It is an operating document,
not a dashboard: every line triggers a decision. The metrics come from the
measure stage, the one motion and the gate ledger from the decide-and-gate stage,
and the week-over-week deltas from the remembered prior state. Deterministic: the
caller passes week_of so there is no wall clock here.
"""

from __future__ import annotations

from . import plan as planning


def _pts_delta(cur, prev) -> str:
    """Week-over-week annotation for a rate-like metric, in percentage points."""
    if cur is None or prev is None:
        return ""
    d = round(cur * 100) - round(prev * 100)
    return f"   ({d:+d} pts vs last week)"


def _day_delta(cur, prev) -> str:
    """Week-over-week annotation for time-to-second-build, in days."""
    if cur is None or prev is None:
        return ""
    d = round(cur - prev)
    return f"   ({d:+d} day{'' if abs(d) == 1 else 's'} vs last week)"


def _count_delta(cur, prev) -> str:
    """Week-over-week annotation for a plain count."""
    if prev is None:
        return ""
    d = cur - prev
    return f"   ({d:+d} vs last week)"


def _row(label: str, value: str) -> str:
    """One report line with dotted leaders to a fixed column."""
    lead = (label + " ").ljust(34, ".")
    return f"  {lead} {value}"


def the_one_motion(p: dict) -> dict | None:
    """The single motion for the week, the first proposed action against the
    biggest leak. None when the loop is healthy and nothing is proposed."""
    proposed = p.get("proposed") or []
    return proposed[0] if proposed else None


def weekly_report(readout: dict, p: dict, *, signals: dict | None = None,
                  prev_state: dict | None = None, week_of: str = "",
                  enrichment: dict | None = None, decision: dict | None = None) -> str:
    signals = signals or {}
    prev = prev_state or {}
    funnel = {f["stage"]: f["count"] for f in readout.get("funnel", [])}

    ar = readout.get("activation_rate")
    rr = readout.get("retention_rate")
    er = readout.get("engagement_retention")
    ttsb = readout.get("time_to_second_build_days")
    drop = readout.get("biggest_dropoff")
    ready = readout.get("pqas_ready_for_handoff") or []
    handoffs = (readout.get("the_number") or {}).get("handoffs_this_cohort", funnel.get("handoff", 0))

    signups_total = signals.get("signups_total", funnel.get("signup", 0))
    prev_signups = prev.get("signups_total")
    signups_new = signups_total - prev_signups if prev_signups is not None else None
    ttfv = signals.get("time_to_first_value_days")

    L = [f"Weekly startup-signal report -- cohort {readout.get('cohort', 'unnamed cohort')}"]
    if week_of:
        L.append(f"Week of {week_of}")

    # ACTIVATION
    L += ["", "ACTIVATION"]
    new_str = f"{signups_new} new, " if signups_new is not None else ""
    L.append(_row("signups", f"{new_str}{signups_total} total"))
    if ar is not None:
        L.append(_row("activation rate (build/signup)",
                      f"{ar * 100:.0f}%{_pts_delta(ar, prev.get('activation_rate'))}"))
    else:
        L.append(_row("activation rate (build/signup)", "n/a"))
    L.append(_row("time-to-first-value",
                  f"{ttfv} days (signup -> first call)" if ttfv is not None else "n/a"))
    if drop and all(k in drop for k in ("from", "to", "lost_pct")):
        L.append(_row("biggest leak",
                      f"{drop['from']} -> {drop['to']} ({drop['lost_pct'] * 100:.0f}% lost)   <- the onboarding fix"))

    # RETENTION, judged against the AI-native bar, not the enterprise bar.
    L += ["", "RETENTION"]
    L.append(_row("time-to-second-build",
                  (f"{ttsb} days{_day_delta(ttsb, prev.get('time_to_second_build_days'))}   <- the leading indicator")
                  if ttsb is not None else "n/a days"))
    if rr is not None:
        leaky = "   leaky-bucket flag" if readout.get("leaky_bucket") else ""
        L.append(_row("retention rate (2nd/1st build)",
                      f"{rr * 100:.0f}%{_pts_delta(rr, prev.get('retention_rate'))}{leaky}"))
    if er is not None:
        L.append(_row("engagement retention", f"{er * 100:.0f}% weekly-active of first-build"))
    L.append(_row("logo retention (paid)", "needs billing data; AI-native band 65-75% good, under 50% leaky"))
    L.append(_row("NRR / expansion", "needs billing data; AI-native 90-110% strong vs the 48% AI-native norm"))

    # PIPELINE
    L += ["", "PIPELINE"]
    names = f": {', '.join(ready)} (rising spend)" if ready else ""
    L.append(_row("PQAs ready for handoff",
                  f"{len(ready)} account(s){names}{_count_delta(len(ready), _prev_len(prev.get('pqas_ready_for_handoff')))}"))
    L.append(_row("net-new logos attributable", f"{handoffs} this week"))

    # PQA BRIEFS, only when the enrich step ran (a key was present).
    if enrichment and enrichment.get("briefs"):
        L += ["", "PQA BRIEFS (enrich step)"]
        for name, b in enrichment["briefs"].items():
            L.append(f"  - {name}: {b.get('brief', '')}")
            for url in (b.get("citations") or [])[:2]:
                L.append(f"      cite: {url}")

    # THE ONE MOTION, the model's decision when the decide step ran, else the
    # deterministic pick from the gated plan.
    motion = the_one_motion(p)
    L += ["", "THE ONE MOTION"]
    if decision and decision.get("motion"):
        L.append(f"  - {decision['motion']} Moves: {decision.get('moves', '')}.")
        if decision.get("rationale"):
            L.append(f"    why: {decision['rationale']}")
    elif motion:
        L.append(f"  - {motion['motion']} Moves: {motion['moves']}.")
    else:
        L.append("  - Hold. Healthy loop, keep credits milestone-gated so they qualify intent.")

    # The gate ledger: what ran on its own, what waits on you, what it will not do.
    L += planning._action_sections(p)
    return "\n".join(L).rstrip() + "\n"


def _prev_len(value):
    return len(value) if value is not None else None
