"""Decide the one motion: adaptive thinking, high effort, an advisor second opinion.

The deterministic plan proposes the gated motions, and the gate ledger already
carries the deterministic pick. This step runs Claude every run to choose the
single highest-leverage motion and say why, reasoning with adaptive thinking and
consulting the advisor tool. The output is constrained to a schema so the decision
is machine-readable. With no key or no SDK it raises a clear error, so a
misconfiguration is loud rather than a silent downgrade. It needs ANTHROPIC_API_KEY
and the anthropic SDK.
"""

from __future__ import annotations

import json

from ..platform import client as _client

MOTION_SCHEMA = {
    "type": "object",
    "properties": {
        "motion": {"type": "string"},
        "moves": {"type": "string"},
        "rationale": {"type": "string"},
        "why_not_alternatives": {"type": "string"},
    },
    "required": ["motion", "moves", "rationale"],
    "additionalProperties": False,
}

_STATE_KEYS = ("activation_rate", "retention_rate", "engagement_retention",
               "time_to_second_build_days", "biggest_dropoff", "leaky_bucket")


def _compact(readout: dict) -> str:
    return "\n".join(f"  {k}: {readout.get(k)}" for k in _STATE_KEYS)


def decide_motion(readout: dict, plan: dict) -> dict:
    """Have Claude pick the one motion against the biggest leak, with the advisor
    as a second opinion. Runs every run; raises when the SDK or the key is missing.
    Returns the decision as machine-readable JSON."""
    c = _client.require_client()

    system = [{
        "type": "text",
        "text": ("You are a growth operator for a founder cohort. Decide the single "
                 "highest-leverage motion this week, tied to the biggest funnel leak. "
                 "One motion, not a list. Judgment only; you do not send anything."),
        "cache_control": {"type": "ephemeral"},
    }]
    user = ("Readout:\n" + _compact(readout) + "\n\nGated motions already proposed:\n"
            + "\n".join(f"- [{a['id']}] {a['motion']} (moves {a['moves']})"
                        for a in plan.get("proposed", []))
            + "\n\nConsult the advisor tool for a second opinion, then return the decision.")
    resp = c.beta.messages.create(
        model=_client.MODEL,
        max_tokens=6000,
        betas=["advisor-tool-2026-03-01"],
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": MOTION_SCHEMA}},
        tools=[{"type": "advisor_20260301", "name": "advisor", "model": _client.ADVISOR_MODEL}],
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(getattr(b, "text", "") for b in resp.content
                   if getattr(b, "type", "") == "text").strip()
    data = json.loads(text)
    data["live"] = True
    return data
