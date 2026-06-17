"""The eleven adoption questions as logical retrievals over the event log.

Each query names the question a stakeholder actually asks, the signal it reads
(the logical retrieval, not a vendor's SQL), the R-A-R stage it sits in, and the
report line it feeds. The same logic runs as a PostHog funnel, a HogQL query, or
a dbt model over a warehouse. Here it runs over the local JSONL so the whole
thing works offline. The screenshot ids (Q1..Q11) are kept so the mapping to the
developer-adoption funnel is explicit: Q9, the new-SDK API key, is the
second-build line, the clearest commitment signal in the set.
"""

import json
import statistics

from .. import contracts as ev


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _orgs_with_event(rows, name):
    return {r["org_id"] for r in rows if r["event"] == name}


def _orgs_reaching(rows, stage):
    return {r["org_id"] for r in rows if r.get("stage") == stage}


def _count_events(rows, name):
    return sum(1 for r in rows if r["event"] == name)


def _sum_prop(rows, name, prop):
    return sum(r.get("props", {}).get(prop, 0) for r in rows if r["event"] == name)


def _first_ts_per_org(rows, stage):
    first = {}
    for r in rows:
        if r.get("stage") == stage:
            o, t = r["org_id"], r["ts"]
            if o not in first or t < first[o]:
                first[o] = t
    return first


def time_to_first_value_days(rows, org_filter=None):
    """Median days from signup to first successful call, the aha transition."""
    sign = _first_ts_per_org(rows, ev.AHA_FROM)
    call = _first_ts_per_org(rows, ev.AHA_TO)
    gaps = []
    for o in call:
        if o in sign and (org_filter is None or o in org_filter):
            gaps.append((call[o] - sign[o]) / 86400.0)
    return round(statistics.median(gaps), 1) if gaps else None


# Each query: id (screenshot), stage, the question, the logical retrieval, the
# report line it feeds, and fn(rows) -> value. The phase is derived from the
# stage in run_all, so it is never stored twice and cannot drift.
QUERIES = [
    {"id": "Q3", "stage": "signup",
     "question": "How many developers showed up to experiment at all?",
     "retrieval": "distinct org_id with a signup event",
     "line": "ACTIVATION: signups",
     "fn": lambda rows: len(_orgs_reaching(rows, "signup"))},
    {"id": "Q4", "stage": "first_call",
     "question": "Are they doing something, or landing and bouncing?",
     "retrieval": "api_call events per trial org (depth of the trial)",
     "line": "ACTIVATION: time-to-first-value / trial depth",
     "fn": lambda rows: round(
         _count_events(rows, "api_call") / max(1, len(_orgs_reaching(rows, "first_call"))), 1)},
    {"id": "Q5", "stage": "first_build",
     "question": "How many converted from tried-it-once to installed-and-using?",
     "retrieval": "distinct org_id with a build_succeeded event",
     "line": "ACTIVATION: activation rate (numerator)",
     "fn": lambda rows: len(_orgs_reaching(rows, "first_build"))},
    {"id": "Q7", "stage": "first_build",
     "question": "Is the adopter base growing?",
     "retrieval": "new build_succeeded org_ids in the window (inflow)",
     "line": "ACTIVATION: activation inflow",
     "fn": lambda rows: len(_orgs_reaching(rows, "first_build"))},
    {"id": "Q8", "stage": "second_build",
     "question": "How many serious builders are on the legacy path?",
     "retrieval": "distinct org_id with a legacy_sdk event (migration pressure)",
     "line": "RETENTION: migration pressure (context, not a core line)",
     "fn": lambda rows: len(_orgs_with_event(rows, "legacy_sdk"))},
    {"id": "Q9", "stage": "second_build",
     "question": "How many crossed the real commitment threshold (built something of their own)?",
     "retrieval": "distinct org_id with an api_key_created event",
     "line": "RETENTION: retention rate (numerator), the leading indicator",
     "fn": lambda rows: len(_orgs_reaching(rows, "second_build"))},
    {"id": "Q6", "stage": "weekly_active",
     "question": "How deeply are adopters working it into real coding?",
     "retrieval": "build_step events per first-build org (habit depth)",
     "line": "RETENTION: engagement retention",
     "fn": lambda rows: round(
         _count_events(rows, "build_step") / max(1, len(_orgs_reaching(rows, "first_build"))), 1)},
    {"id": "Q10", "stage": "production",
     "question": "How much production-shaped work are the builders running?",
     "retrieval": "production_traffic events per production org (intensity)",
     "line": "PIPELINE: intensity per builder",
     "fn": lambda rows: round(
         _count_events(rows, "production_traffic") / max(1, len(_orgs_reaching(rows, "production"))), 1)},
    {"id": "Q1", "stage": "production",
     "question": "How many accounts reached the paid, production surface?",
     "retrieval": "distinct org_id with a production_traffic event",
     "line": "PIPELINE: net-new logos / production count",
     "fn": lambda rows: len(_orgs_reaching(rows, "production"))},
    {"id": "Q2", "stage": "production",
     "question": "What consumption is driving the bill?",
     "retrieval": "sum of tokens across all token events",
     "line": "RETENTION: NRR / expansion input",
     "fn": lambda rows: _sum_prop(rows, "tokens", "tokens")},
    {"id": "Q11", "stage": "all",
     "question": "Where does activity concentrate (the shape of the whole funnel)?",
     "retrieval": "distinct org_id per stage, in order",
     "line": "the funnel shape, one view",
     "fn": lambda rows: {s: len(_orgs_reaching(rows, s)) for s in ev.STAGES}},
]


def run_all(rows):
    """Every query as {id, phase, stage, question, retrieval, line, value}. The
    phase is derived from the stage, the single source of truth, so it cannot
    drift, and the queries are in stage order so the phases stay sequential."""
    out = []
    for q in QUERIES:
        out.append({
            "id": q["id"], "phase": ev.phase_for(q["stage"]),
            **{k: q[k] for k in ("stage", "question", "retrieval", "line")},
            "value": q["fn"](rows),
        })
    return out
