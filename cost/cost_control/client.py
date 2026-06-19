"""Anthropic client and model routing.

This is a real tool. Every run calls the Anthropic API, so ANTHROPIC_API_KEY is required. If the
key is missing, the run fails fast with a clear error and a non-zero exit. There is no offline
mode and no fallback. Haiku is used where the lesson is carried tokens not the model, Opus where
the lever wants a frontier model.
"""

import os
from pathlib import Path

try:  # honor this stage's ignored .env without weakening the fail-fast path
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:  # pragma: no cover - dotenv is a setup helper, not the runtime contract
    pass

FAST_MODEL = "claude-haiku-4-5"
MAIN_MODEL = "claude-opus-4-8"


def require_key() -> None:
    """Raise immediately if ANTHROPIC_API_KEY is missing, so the run fails fast."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is required. Put it in .env or set it in the environment, "
            "then run `python run.py`."
        )


def get_client():
    """Return a real Anthropic client. Fails fast if the key is missing."""
    require_key()
    import anthropic

    return anthropic.Anthropic()
