"""Shared Claude client: the model id, the run guard, token counting.

Every stage runs Claude on every run. The deterministic stages (capture, measure,
the gate, the audit) carry the receipt and the CI gate, so they run with no key.
The generative stages (enrich, decide, draft) call `require_client()` and raise a
clear error when the SDK or the key is missing, so a misconfiguration is loud, not
a silent downgrade. The model defaults to claude-opus-4-8 for judgment, with
claude-opus-4-8 again as the advisor second opinion in the decide step.
"""

from __future__ import annotations

import os

MODEL = "claude-opus-4-8"          # the default for every judgment call
ADVISOR_MODEL = "claude-opus-4-8"  # the advisor in the decide step (the API rejects a lesser tier than the request model)

try:
    from anthropic import Anthropic
except Exception:  # the SDK is a hard dependency of the generative stages
    Anthropic = None  # type: ignore

try:  # honor a .env without making dotenv a hard dependency
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


def available() -> bool:
    """True when a live call is possible: the SDK imports and a key is set.

    The harnesses (deploy, the local agent) use this to choose between the live
    path and a dry-run plan. The generative stages do not: they require the client
    and raise, so a missing key fails loud rather than degrading."""
    return Anthropic is not None and bool(os.getenv("ANTHROPIC_API_KEY"))


def require_client():
    """An Anthropic client for a generative stage, or a clear RuntimeError.

    Every generative stage runs Claude every run. With no SDK or no key this
    raises instead of returning a quiet fallback, so the failure names what is
    missing. The deterministic stages never call this, which is why they run
    offline."""
    if Anthropic is None:
        raise RuntimeError(
            "this step runs Claude and needs the anthropic SDK: pip install anthropic"
        )
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "this step runs Claude and needs ANTHROPIC_API_KEY set. It runs every "
            "run, there is no offline mode. Put the key in .env or export it."
        )
    return Anthropic()


def client():
    """An Anthropic client, or None when no key or no SDK. The harnesses fall back
    to a dry-run plan when this is None. Generative stages use require_client."""
    return Anthropic() if available() else None


def count_tokens(messages, *, system=None, model=MODEL):
    """Token count for a request, the cost receipt before a batch goes out.
    Returns None offline. Never tiktoken: token counts are model-specific."""
    c = client()
    if c is None:
        return None
    kw = {"model": model, "messages": messages}
    if system is not None:
        kw["system"] = system
    return c.messages.count_tokens(**kw).input_tokens
