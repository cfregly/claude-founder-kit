"""Read the moat readout and write the GTM motion and the moat narrative.

This step runs Claude every run. A forced tool call returns two things grounded in
the deterministic numbers: (a) the GTM motion for the cohort, which accounts to
target and the play to run, and (b) the moat narrative, the case for why a
well-funded incumbent copying this product today would not catch up within two
years. With no key or no SDK it raises a clear error, so a misconfiguration is
loud rather than a silent skip. It needs ANTHROPIC_API_KEY and the anthropic SDK.
"""

from __future__ import annotations

from ..platform import client as _client

GTM_TOOL = {
    "name": "gtm_and_moat",
    "description": (
        "The GTM motion for this cohort and the moat narrative, both grounded in "
        "the moat readout numbers."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "gtm_motion": {
                "type": "object",
                "description": "The go-to-market motion for the cohort this week.",
                "properties": {
                    "target_accounts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The account names to target now, from the GTM-ready set.",
                    },
                    "play": {
                        "type": "string",
                        "description": "The single play to run against the targeted accounts.",
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this play and these accounts, tied to the numbers.",
                    },
                },
                "required": ["target_accounts", "play", "rationale"],
            },
            "moat_narrative": {
                "type": "string",
                "description": (
                    "Two to four sentences: why a well-funded incumbent copying this "
                    "product today would not catch up within two years, grounded in the "
                    "integration depth, the workflow lock-in, and the compounding data."
                ),
            },
        },
        "required": ["gtm_motion", "moat_narrative"],
    },
}

# The readout keys that ground the prompt. The moat is a switching-cost proxy, so
# the narrative must reason from the depth and the compounding data, not adjectives.
_STATE_KEYS = (
    "cohort", "accounts", "moat_distribution", "median_moat",
    "gtm_ready_accounts", "compounding_data_accounts",
)


def _compact(readout: dict) -> str:
    lines = [f"  {k}: {readout.get(k)}" for k in _STATE_KEYS]
    top = sorted(readout.get("scores", []), key=lambda s: s["moat"], reverse=True)[:8]
    lines.append("  per-account (top by moat):")
    for s in top:
        lines.append(
            f"    {s['name']}: moat {s['moat']} ({s['band']}), "
            f"integration_depth {s['integration_depth']}, workflow_lockin {s['workflow_lockin']}, "
            f"compounding_data {s['compounding_data']}, gtm_ready {s['gtm_ready']}")
    return "\n".join(lines)


def gtm_and_moat(readout: dict, *, model: str | None = None) -> dict:
    """Have Claude write the GTM motion and the moat narrative from the moat
    readout. Runs Claude every run; raises when the SDK or the key is missing.
    Returns the motion and the narrative as machine-readable JSON."""
    model = model or _client.MODEL
    c = _client.require_client()

    system = (
        "You are a growth operator for a Scale-stage software company. You read a "
        "deterministic moat readout, where the moat is a switching-cost proxy built "
        "from how many of a customer's systems the product is wired into, how many "
        "of their recurring workflows run through it, and how much proprietary data "
        "has accrued. Write the one GTM motion for the cohort and the moat narrative. "
        "Ground every claim in the numbers you are given. Plain language, no buzzwords, "
        "no em-dashes. You decide and draft only; you do not send anything."
    )
    user = (
        "Moat readout:\n" + _compact(readout)
        + "\n\nReturn the GTM motion (which accounts to target from the GTM-ready set, "
        "and the one play) and the moat narrative (why a well-funded incumbent copying "
        "this product today would not catch up within two years)."
    )
    resp = c.messages.create(
        model=model,
        max_tokens=2000,
        system=system,
        tools=[GTM_TOOL],
        tool_choice={"type": "tool", "name": "gtm_and_moat"},
        messages=[{"role": "user", "content": user}],
    )
    block = next((b for b in resp.content if getattr(b, "type", "") == "tool_use"), None)
    data = dict(block.input) if block else {}
    data["live"] = True
    data["model"] = model
    data["usage"] = {
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }
    return data
