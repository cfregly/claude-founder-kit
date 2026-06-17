"""Decide the next motion from the readout, and gate every outward step.

This turns the funnel state into a plan a human approves, not a black box that
acts on its own. The boundary is fixed and stated, not discovered at runtime.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .. import contracts

ALWAYS = contracts.ALWAYS
ASK = contracts.ASK
NEVER = contracts.NEVER


@dataclass(frozen=True)
class Action:
    id: str
    gate: str       # always | ask | never
    outward: bool   # does it touch someone outside the loop?
    motion: str     # what to do
    rationale: str  # why, tied to the state
    moves: str      # the metric it intends to move ("" for internal)


# What the operator refuses to do on a schedule. The line autonomy does not cross.
NEVER_ACTIONS = [
    Action("auto_email", NEVER, True,
           "Send founder emails without your review.",
           "Outbound in your name is yours to approve.", ""),
    Action("auto_spend", NEVER, True,
           "Spend on ads or any paid channel.",
           "Money leaves only on a human decision and a cap.", ""),
    Action("auto_post", NEVER, True,
           "Post to public or social channels.",
           "A public voice is not delegated to a schedule.", ""),
    Action("auto_credits", NEVER, True,
           "Promise or grant credits.",
           "Credits qualify intent, and granting them is a human call.", ""),
    Action("auto_handoff", NEVER, True,
           "Hand off an account that has not met the production-and-rising-spend trigger.",
           "Sustained usage is the trigger, never a vibe.", ""),
]


def _always_actions(readout: dict) -> list[Action]:
    """The work that is safe to run on its own: measure and draft."""
    acts = [
        Action("rescore", ALWAYS, False,
               "Re-score the cohort and recompute the funnel.",
               "Each run starts from the current state, not last week's.", ""),
    ]
    drop = readout.get("biggest_dropoff")
    if drop and all(k in drop for k in ("from", "to", "lost_pct")):
        acts.append(Action("flag_leak", ALWAYS, False,
                           f"Flag the biggest leak: {drop['from']} -> {drop['to']} "
                           f"({round(drop['lost_pct'] * 100)}% lost).",
                           "Name the leak before proposing a fix.", ""))
    acts.append(Action("draft_report", ALWAYS, False,
                       "Draft this report.",
                       "An update read in a minute beats a dashboard nobody opens.", ""))
    return acts


def _proposed_actions(readout: dict) -> list[Action]:
    """The outward motions the state calls for. Each waits for approval."""
    out: list[Action] = []
    drop = readout.get("biggest_dropoff") or {}
    to = drop.get("to")
    leaky = bool(readout.get("leaky_bucket"))
    funnel = {f["stage"]: f["count"] for f in readout.get("funnel", [])}
    stuck = max(funnel.get("first_build", 0) - funnel.get("second_build", 0), 0)

    if to in ("first_call", "first_build"):
        out.append(Action("first_build_clinic", ASK, True,
                          "Schedule a build-clinic follow-up for accounts stuck before a first build.",
                          "The leak is reaching a first build; every touch must end in a working build.",
                          "activation rate"))
    if to == "second_build" or leaky:
        who = f"{stuck} account(s)" if stuck else "first-build accounts with no second build"
        out.append(Action("second_build_nudge", ASK, True,
                          f"Send the 72-hour second-build nudge to {who}.",
                          "The leak is the second build, the real activation signal.",
                          "time-to-second-build"))
    if readout.get("engagement_leak"):
        quiet = max(funnel.get("first_build", 0) - funnel.get("weekly_active", 0), 0)
        who = f"{quiet} builder(s)" if quiet else "builders who did not return weekly"
        out.append(Action("reengage_weekly", ASK, True,
                          f"Send the week-2 re-engagement prompt to {who}.",
                          "Engagement retention is the leading indicator of paid retention. "
                          "Builders who do not return weekly do not renew.",
                          "engagement retention"))
    ready = readout.get("pqas_ready_for_handoff") or []
    if ready:
        out.append(Action("pqa_handoff", ASK, True,
                          f"Hand {len(ready)} product-qualified account(s) to a named GTM owner: "
                          f"{', '.join(ready)}.",
                          "In production with rising spend and not yet handed off.",
                          "qualified PQA handoffs"))
    return out


def plan(readout: dict) -> dict[str, Any]:
    """Turn an activation readout into a gated plan: what ran, what waits on you,
    and what the operator refuses to do on its own."""
    did = _always_actions(readout)
    proposed = _proposed_actions(readout)

    notes: list[str] = []
    if not proposed:
        notes.append("Healthy loop. Nothing needs your approval. Keep credits "
                     "milestone-gated so they qualify intent, not vanity signups.")

    return {
        "cohort": readout.get("cohort", "unnamed cohort"),
        "state": {
            "activation_rate": readout.get("activation_rate"),
            "retention_rate": readout.get("retention_rate"),
            "engagement_retention": readout.get("engagement_retention"),
            "time_to_second_build_days": readout.get("time_to_second_build_days"),
            "biggest_dropoff": readout.get("biggest_dropoff"),
            "pqas_ready_for_handoff": readout.get("pqas_ready_for_handoff", []),
            "the_number": readout.get("the_number"),
        },
        "did": [asdict(a) for a in did],
        "proposed": [asdict(a) for a in proposed],
        "will_not": [asdict(a) for a in NEVER_ACTIONS],
        "notes": notes,
    }


def audit(p: dict) -> list[str]:
    """The boundary that makes autonomy accountable: nothing outward-facing and
    nothing gated above `always` may land in `did`, the work that ran unattended.
    Returns the violations; an empty list means the boundary held."""
    out: list[str] = []
    for a in p.get("did", []):
        if a.get("outward"):
            out.append(f"outward action ran unattended: {a['id']}")
        if a.get("gate") != ALWAYS:
            out.append(f"non-always action ran unattended: {a['id']} ({a.get('gate')})")
    return out


def _action_sections(p: dict) -> list[str]:
    """The gate ledger under the metrics: what ran, what waits, what the operator
    will not do, and the notes. Shared by the morning and the weekly report, so
    the cadence differs but the gated content does not."""
    L = ["", "Ran on its own (measurement and drafting only, no approval needed)"]
    L += [f"  - {a['motion']}" for a in p["did"]]

    L.append("")
    if p["proposed"]:
        L.append("Waiting on you (approve to run)")
        for a in p["proposed"]:
            L.append(f"  - [{a['id']}] {a['motion']} Moves: {a['moves']}.")
            d = a.get("draft")  # optional Claude-drafted message (draft stage)
            if d:
                L.append(f"      draft subject: {d['subject']}")
                L += [f"      {ln.strip()}" for ln in str(d["body"]).splitlines() if ln.strip()]
                b = d.get("brand")  # optional deslop brand-bar grade (CASH quality step)
                if b:
                    tail = "" if b["findings"] == 0 else f", {b['findings']} to fix before send"
                    L.append(f"      brand bar: {b['grade']} ({b['score']}/100){tail}")
    else:
        L.append("Waiting on you: nothing.")

    L += ["", "Will not do on its own (by design)"]
    L += [f"  - {a['motion']}" for a in p["will_not"]]

    if p["notes"]:
        L.append("")
        L += p["notes"]
    if p["proposed"]:
        L += ["", "Reply approve <id> or skip <id> for each item above."]
    return L


def morning_report(p: dict) -> str:
    """The founder's one-minute update on a daily cadence: the state, what ran,
    what waits on them, and the line autonomy did not cross."""
    s = p["state"]
    ar, rr = s.get("activation_rate"), s.get("retention_rate")
    ttsb, drop = s.get("time_to_second_build_days"), s.get("biggest_dropoff")
    ready = s.get("pqas_ready_for_handoff") or []

    L = [f"operator morning report: {p['cohort']}", "", "State"]
    L.append(f"  activation rate ......... {ar * 100:.0f}%" if ar is not None
             else "  activation rate ......... n/a")
    L.append(f"  retention (2nd build) ... {rr * 100:.0f}%" if rr is not None
             else "  retention (2nd build) ... n/a")
    L.append(f"  time-to-second-build .... {ttsb if ttsb is not None else 'n/a'} days")
    if drop and all(k in drop for k in ("from", "to", "lost_pct")):
        L.append(f"  biggest leak ............ {drop['from']} -> {drop['to']} "
                 f"({drop['lost_pct'] * 100:.0f}% lost)")
    L.append(f"  PQAs ready .............. {len(ready)}")

    L += _action_sections(p)
    return "\n".join(L).rstrip() + "\n"
