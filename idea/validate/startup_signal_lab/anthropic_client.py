"""Claude reads the startup signal and writes the founder intervention, every run.

The diagnose stage runs on Claude. The deterministic scorers (scoring_tools.py,
growth.py, router.py) compute the signal score, the Relationship-Activation-Retention
read, the Dot/Dash/Star sort, and the model route. That is the receipt CI re-runs
offline. Claude reads those numbers and writes the founder intervention: the value-prop
rewrite, the wedge, the architecture call, the platform-risk answer, and the metrics.

This assumes a key is set. The intervention is not optional and there is no offline
mode for it: the tool runs Claude. With no key or no SDK it raises a clear error
instead of degrading to a canned response. The deterministic scores stay the gate
that verifies the run; the Claude-written diagnosis is the judgment.

Requires ANTHROPIC_API_KEY and `pip install anthropic`.
"""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - the SDK is a hard runtime dependency
    Anthropic = None  # type: ignore

try:  # honor the README's `cp .env.example .env` setup path
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

from .prompts import FOUNDER_SYSTEM_PROMPT, founder_intervention_prompt
from .router import route_as_dict
from .scoring_tools import score_as_dict


def _json(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


def analyze_pitch_with_claude(pitch: str) -> dict[str, Any]:
    """Score the pitch deterministically, then have Claude write the intervention.

    Runs Claude every time. Raises RuntimeError when the SDK or the key is missing,
    so a misconfiguration is loud, not a silent downgrade to a canned response. The
    deterministic score and route are computed first and returned alongside the
    Claude narrative as the gate that verifies the run.
    """
    if Anthropic is None:
        raise RuntimeError(
            "the founder intervention needs the anthropic SDK: pip install anthropic"
        )
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "the founder intervention needs ANTHROPIC_API_KEY set. This tool runs "
            "Claude every run. Put the key in .env or export it."
        )

    score = score_as_dict(pitch)
    route = route_as_dict(
        task="founder strategy, architecture, platform risk, and GTM intervention",
        risk="medium" if score["platform_risk"] < 8 else "high",
        context_tokens=max(1000, len(pitch) // 4),
    )
    prompt = founder_intervention_prompt(pitch, _json(score), _json(route))

    client = Anthropic()
    model = route["model"]
    # Honor the router's caching decision. When it flags the static context as
    # cacheable, send the system prompt as a cache_control block so repeated calls
    # reuse the prefix. Below the model's minimum cacheable size this is a silent
    # no-op, never an error.
    system: Any = FOUNDER_SYSTEM_PROMPT
    if route.get("cache_static_context"):
        system = [{
            "type": "text",
            "text": FOUNDER_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }]
    message = client.messages.create(
        model=model,
        max_tokens=1800,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "\n".join(block.text for block in message.content if block.type == "text")

    return {
        "score": score,
        "route": route,
        "response": text,
        "usage": message.usage.model_dump(),
    }
