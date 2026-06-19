"""Optional Claude judge: catch the semantic slop a rule list cannot.

The deterministic rules in slop_rules.json catch the slop you can enumerate:
em-dashes, a fixed buzzword list, filler phrases, template HTML. They cannot
catch slop that needs reading: a vague claim, a hedge, an unsupported
superlative, a sentence that says nothing. This judge reads the text with
claude-opus-4-8 and surfaces those as advisory notes. It never changes the
deterministic score or the exit code, so the gate stays reproducible. With no
key it is a no-op and the linter behaves exactly as before.

Best practice: this is a single structured read of text you already have, so it
uses the Messages API, not the Agent SDK. Structured output is forced with
tool_choice, so the result is reliable JSON on every SDK version.

Requires ANTHROPIC_API_KEY and `pip install anthropic`.
"""
from __future__ import annotations

import os

try:
    from anthropic import Anthropic
except Exception:  # optional dependency: the linter is stdlib-only without it
    Anthropic = None  # type: ignore

try:  # honor the .env setup path without making dotenv a hard dependency
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

MODEL = "claude-opus-4-8"

SYSTEM = """You find AI-writing slop that a rule list cannot catch. The rules
already flag em-dashes, a fixed buzzword list, filler phrases, and template
HTML, so do not repeat those. Read for meaning and flag only these: a vague
claim with no specifics, a hedge that weakens the point, an unsupported
superlative, a sentence that carries no information, or generic template
phrasing that could sit in any document. For each one return the exact quote,
one line on why it reads as slop, and a tighter rewrite.

Example. In the text "We help teams do more with their data, and results may
vary by setup.", flag "We help teams do more with their data" with the reason
"vague claim, no specific outcome or number" and the rewrite "We cut a 45-minute
report to under 5 minutes." Then flag "results may vary by setup" with the reason
"a hedge that weakens the claim" and the rewrite "state the condition instead:
results assume a connected warehouse."

If the text is clean, return no findings. Write your own output plain: no
em-dashes, no semicolons, no buzzwords."""

# Forced tool_choice makes the result reliable JSON on every SDK version.
_TOOL = {
    "name": "semantic_slop",
    "description": "Return the semantic slop a deterministic rule list would miss.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "quote": {"type": "string", "description": "the exact text flagged"},
                        "why": {"type": "string", "description": "one line on why it reads as slop"},
                        "suggestion": {"type": "string", "description": "a tighter rewrite"},
                    },
                    "required": ["quote", "why", "suggestion"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["findings"],
        "additionalProperties": False,
    },
}


def available() -> bool:
    """True when a live judge is possible: the SDK imports and a key is set."""
    return Anthropic is not None and bool(os.getenv("ANTHROPIC_API_KEY"))


def judge_text(text: str, *, model: str = MODEL) -> dict:
    """Advisory semantic-slop findings from Claude.

    Returns {"live": bool, "findings": [{quote, why, suggestion}], "model": ...}.
    It never raises and never affects the deterministic score: with no key, no
    SDK, empty text, or an API error, it returns live False and no findings.
    """
    if not text.strip() or not available():
        return {"live": False, "findings": [], "model": model}
    try:
        client = Anthropic()
        # No temperature is set: it is removed on claude-opus-4-8 and sending it
        # returns a 400. Determinism comes from the forced tool call below.
        msg = client.messages.create(
            model=model,
            max_tokens=900,
            system=SYSTEM,
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "semantic_slop"},
            messages=[{"role": "user", "content":
                       "Find the semantic slop in the text between the tags.\n\n"
                       "<text_to_review>\n" + text + "\n</text_to_review>"}],
        )
        block = next(b for b in msg.content if getattr(b, "type", None) == "tool_use")
        return {"live": True, "findings": block.input.get("findings", []),
                "model": model, "usage": msg.usage.model_dump()}
    except Exception as exc:  # any failure is a no-op: the rules already scored
        return {"live": False, "findings": [], "model": model, "error": str(exc)[:200]}
