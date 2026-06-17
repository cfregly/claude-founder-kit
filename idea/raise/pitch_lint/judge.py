"""The Claude narrative read: the arc the deterministic rules cannot score.

The deterministic rules score what you can check slide by slide: a missing
source tier, a hedge, a vague ask, a slide with no number. They cannot read the
story across slides: whether each slide earns the next, whether the arc has a
gap, whether the deck answers "why now". claude-opus-4-8 reads the deck in order
and returns that critique. It runs by default when a key is set and prints below
the score. It never changes the score or the exit code, so the deterministic
gate stays reproducible. With no key it skips and the linter is the score alone.

Best practice: reading one deck you already have is a single structured
generation, so it uses the Messages API, not the Agent SDK. Structured output is
forced with tool_choice for reliable JSON on every SDK version.

Needs ANTHROPIC_API_KEY and `pip install anthropic`.
"""
from __future__ import annotations

import json
import os

try:
    from anthropic import Anthropic
except Exception:  # optional dependency: the linter is stdlib-only without it
    Anthropic = None  # type: ignore

try:  # honor the .env setup path without making dotenv a hard dependency
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

MODEL = "claude-opus-4-8"

SYSTEM = """You judge the narrative arc of a pitch deck the way an investor reads
it in the room. You receive the slides in order, each with its arc beat,
headline, and lines. Do not score formatting, single words, or whether a number
has a source. A deterministic linter already does that. Read the story: does each
slide earn the next, is there a gap in the arc (a missing why-now, an
unsupported leap from problem to solution), and which slide carries the deck.
First reason briefly about the arc, then return an advisory arc score from 1 to
10, the slides whose narrative is weak with one line each, the gaps in the arc,
and the single strongest slide.

Score the arc on this scale: 9 to 10, every slide earns the next and the why-now
is explicit. 7 to 8, the arc holds but one leap is under-supported. 5 to 6, the
pieces are there but the order or the why-now is unclear. 3 to 4, it reads as a
list of facts, not a story. 1 to 2, no arc. Write your output plain: no em-dashes,
no semicolons, no buzzwords."""

# Forced tool_choice makes the result reliable JSON on every SDK version.
_TOOL = {
    "name": "narrative_read",
    "description": "Return an investor's read of the deck's narrative arc.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "reasoning": {"type": "string",
                          "description": "two or three sentences reasoning about the arc before the score"},
            "arc_score": {"type": "integer", "description": "advisory arc coherence, 1 to 10, per the scale in the instructions"},
            "weak_slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "arc": {"type": "string", "description": "the arc beat or headline of the slide"},
                        "issue": {"type": "string", "description": "one line on why the narrative is weak"},
                    },
                    "required": ["arc", "issue"],
                    "additionalProperties": False,
                },
            },
            "gaps": {"type": "array", "items": {"type": "string"},
                     "description": "gaps in the arc, for example a missing why-now"},
            "strongest": {"type": "string", "description": "the single slide that carries the deck"},
        },
        "required": ["reasoning", "arc_score", "weak_slides", "gaps", "strongest"],
        "additionalProperties": False,
    },
}


def available() -> bool:
    """True when a live judge is possible: the SDK imports and a key is set."""
    return Anthropic is not None and bool(os.getenv("ANTHROPIC_API_KEY"))


def judge_deck(deck: dict, *, model: str = MODEL) -> dict:
    """Advisory narrative read of a deck spec.

    Returns {"live": bool, "model": ..., and on a live call arc_score, weak_slides,
    gaps, strongest}. It never raises and never affects the deterministic score:
    with no key, no SDK, no slides, or an API error, it returns live False.
    """
    slides = deck.get("slides", [])
    if not slides or not available():
        return {"live": False, "model": model}

    payload = {
        "company": deck.get("company"),
        "slides": [{"arc": s.get("arc"), "headline": s.get("headline"),
                    "lines": s.get("lines", [])} for s in slides],
    }
    try:
        client = Anthropic()
        # No temperature is set: it is removed on claude-opus-4-8 and sending it
        # returns a 400. Determinism comes from the forced tool call below.
        msg = client.messages.create(
            model=model,
            max_tokens=900,
            system=SYSTEM,
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "narrative_read"},
            messages=[{"role": "user", "content":
                       "Read this deck's narrative arc. Slides in order:\n```json\n"
                       + json.dumps(payload, indent=2) + "\n```"}],
        )
        block = next(b for b in msg.content if getattr(b, "type", None) == "tool_use")
        return {"live": True, "model": model, "usage": msg.usage.model_dump(), **block.input}
    except Exception as exc:  # any failure is a no-op: the rules already scored
        return {"live": False, "model": model, "error": str(exc)[:200]}


def render(jr: dict) -> str:
    """The narrative read as a short advisory block, printed below the score."""
    if not jr.get("live"):
        why = jr.get("error", "no ANTHROPIC_API_KEY or anthropic not installed")
        return f"\nNarrative read: skipped ({why})"
    L = [f"\nNarrative read ({jr['model']}, advisory, not scored):",
         f"  arc coherence ... {jr.get('arc_score', '?')}/10"]
    weak = jr.get("weak_slides", [])
    if weak:
        L.append("  weak slides:")
        L += [f"    - [{w['arc']}] {w['issue']}" for w in weak]
    gaps = jr.get("gaps", [])
    if gaps:
        L.append("  gaps:")
        L += [f"    - {g}" for g in gaps]
    if jr.get("strongest"):
        L.append(f"  strongest ....... {jr['strongest']}")
    return "\n".join(L)
