"""Step 8, remember: persist this week's state so next week shows deltas.

The week-over-week deltas in the report ("+5 pts vs last week") need last week's
numbers. Here that is a small JSON file; the platform layer maps the same shape
onto the memory tool locally and a Managed Agents memory store in the cloud, so
the deltas survive across scheduled runs. State is the readout subset the report
compares, nothing more.
"""

from __future__ import annotations

import json

STATE_KEYS = (
    "activation_rate", "retention_rate", "engagement_retention",
    "time_to_second_build_days", "pqas_ready_for_handoff",
)


def state_from(readout: dict, signals: dict | None = None) -> dict:
    """The comparable slice of the readout, plus signups for the new-this-week line."""
    s = {k: readout.get(k) for k in STATE_KEYS}
    if signals is not None:
        s["signups_total"] = signals.get("signups_total")
    return s


def load_prev_state(path: str) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_state(path: str, state: dict) -> None:
    with open(path, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
