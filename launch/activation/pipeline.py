"""The pipeline that produces the weekly report: capture -> measure -> operate.

This is the deterministic spine: capture, measure, the gate, and the report
template run with no key, so `make demo` reproduces the report with nothing
installed. The generative steps (enrich, decide, draft) and render hang off the
same artifacts on the live path and run Claude every run; they raise when the key
is missing, so the live path needs a key.
"""

from __future__ import annotations

import json
import os
import tempfile

from .capture import cohort, queries, simulate
from .measure import metrics
from .operate import memory, plan as planning, report as reporting

DEFAULT_COHORT = "Founder day (sample, fictional)"
DEFAULT_WEEK_OF = "2026-06-15"


def capture_rows(seed: int = 7) -> list[dict]:
    """Run the deterministic cohort through emit() into a fresh local log, then
    load the rows back. The working log is a temp file, so the demo never leaves
    an artifact in the working directory and never depends on a prior run."""
    fd, path = tempfile.mkstemp(prefix="wr_events_", suffix=".jsonl")
    os.close(fd)
    prev_log = os.environ.get("ACTIVATION_EVENT_LOG")
    prev_backend = os.environ.get("ACTIVATION_BACKEND")
    os.environ["ACTIVATION_EVENT_LOG"] = path
    os.environ["ACTIVATION_BACKEND"] = "local"  # offline by construction
    try:
        open(path, "w").close()
        simulate.run(seed)
        return queries.load(path)
    finally:
        _restore("ACTIVATION_EVENT_LOG", prev_log)
        _restore("ACTIVATION_BACKEND", prev_backend)
        try:
            os.unlink(path)
        except OSError:
            pass


def _restore(key: str, value) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


def signals_from(rows: list[dict]) -> dict:
    """The report-line inputs the readout does not carry: signups, the aha
    transition, the token bill, and the production intensity."""
    q = {x["id"]: x["value"] for x in queries.run_all(rows)}
    return {
        "signups_total": q["Q3"],
        "time_to_first_value_days": queries.time_to_first_value_days(rows),
        "tokens": q["Q2"],
        "production_intensity": q["Q10"],
        "funnel": q["Q11"],
    }


def run(seed: int = 7, *, cohort_name: str = DEFAULT_COHORT,
        prev_state: dict | None = None, week_of: str = DEFAULT_WEEK_OF,
        live: bool = False) -> dict:
    """Produce the weekly report and every artifact behind it.

    Offline (live=False, the default) the report is the deterministic spine:
    capture, measure, the gate, and the report template, which run with no key and
    carry the receipt. With live=True the generative steps (enrich, decide, draft)
    run Claude and render is invoked; those steps raise a clear error when the key
    or the SDK is missing, so live=True needs a key."""
    rows = capture_rows(seed)
    signals = signals_from(rows)
    coh = cohort.to_cohort(rows, cohort_name)
    readout = metrics.summarize(coh)
    p = planning.plan(readout)

    enrichment = decision = rendered = None
    if live:
        from .decide import motion as deciding
        from .draft import nudges, render
        from .enrich import research
        enrichment = research.enrich_pqas(readout["pqas_ready_for_handoff"], cohort_name=cohort_name)
        decision = deciding.decide_motion(readout, p)
        nudges.attach(p, nudges.draft_nudges(p))

    text = reporting.weekly_report(readout, p, signals=signals, prev_state=prev_state,
                                   week_of=week_of, enrichment=enrichment, decision=decision)
    if live:
        rendered = render.render_report(text)

    return {
        "rows": rows,
        "signals": signals,
        "cohort": coh,
        "readout": readout,
        "plan": p,
        "state": memory.state_from(readout, signals),
        "enrichment": enrichment,
        "decision": decision,
        "rendered": rendered,
        "report": text,
    }


def generate_examples(dirpath: str = "examples") -> dict:
    """Write the committed sample inputs from the seed-7 run, so the standalone
    subcommands and the tests have a fixed cohort and readout to read."""
    os.makedirs(dirpath, exist_ok=True)
    rows = capture_rows()
    signals = signals_from(rows)
    coh = cohort.to_cohort(rows, DEFAULT_COHORT)
    readout = metrics.summarize(coh)
    # A plausible prior week so the report shows week-over-week deltas. Fictional.
    prev = {
        "activation_rate": 0.62, "retention_rate": 0.57,
        "engagement_retention": 0.5, "time_to_second_build_days": 9,
        "pqas_ready_for_handoff": ["acct_02"], "signups_total": 9,
    }
    paths = {
        "cohort": os.path.join(dirpath, "cohort.json"),
        "readout": os.path.join(dirpath, "readout.json"),
        "prev": os.path.join(dirpath, "prev_week_state.json"),
    }
    with open(paths["cohort"], "w") as f:
        json.dump(coh, f, indent=2)
    with open(paths["readout"], "w") as f:
        json.dump(readout, f, indent=2)
    with open(paths["prev"], "w") as f:
        json.dump(prev, f, indent=2, sort_keys=True)
    return paths
