"""Shared Claude client: the model id, the run guard, token counting.

The deterministic moat core carries the receipt and the CI gate, so it runs with
no key. The generative stage (the GTM motion and the moat narrative) calls
`require_client()` and raises a clear error when the SDK or the key is missing, so
a misconfiguration is loud, not a silent downgrade. The model is claude-opus-4-8.
"""

from __future__ import annotations

import os

MODEL = "claude-opus-4-8"  # the model for the GTM motion and the moat narrative

try:
    from anthropic import Anthropic
except Exception:  # the SDK is a hard dependency of the generative stage
    Anthropic = None  # type: ignore

try:  # honor a .env without making dotenv a hard dependency
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


def available() -> bool:
    """True when a live call is possible: the SDK imports and a key is set.

    The generative stage does not use this to degrade: it requires the client and
    raises, so a missing key fails loud rather than skipping. This is here for a
    caller that wants to check before it commits to the human readout."""
    return Anthropic is not None and bool(os.getenv("ANTHROPIC_API_KEY"))


def require_client():
    """An Anthropic client for the generative stage, or a clear RuntimeError.

    The generative stage runs Claude every run. With no SDK or no key this raises
    instead of returning a quiet fallback, so the failure names what is missing.
    The deterministic core never calls this, which is why it runs offline."""
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
    """An Anthropic client, or None when no key or no SDK. The generative stage
    uses require_client; this is for an optional caller that tolerates None."""
    return Anthropic() if available() else None


def count_tokens(messages, *, system=None, model=MODEL):
    """Token count for a request, the cost receipt before a call goes out.
    Returns None offline. Never tiktoken: token counts are model-specific."""
    c = client()
    if c is None:
        return None
    kw = {"model": model, "messages": messages}
    if system is not None:
        kw["system"] = system
    return c.messages.count_tokens(**kw).input_tokens
