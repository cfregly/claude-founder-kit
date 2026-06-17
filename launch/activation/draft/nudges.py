"""Draft the founder message for each proposed action. The only place a model writes.

This step runs Claude every run. Forced structured output returns one draft per
ask-gated action, and when the sibling deslop linter is importable each draft is
graded against the brand bar, the CASH quality step. With no key or no SDK it
raises a clear error, so a misconfiguration is loud rather than a silent skip. It
needs ANTHROPIC_API_KEY and the anthropic SDK, and it never touches `did` or the
gate.
"""

from __future__ import annotations

from ..platform import client as _client

try:  # the brand bar is the deslop linter, an optional cross-repo check
    from deslop import lint as _deslop_lint
except Exception:
    _deslop_lint = None  # type: ignore

DRAFTS_TOOL = {
    "name": "founder_drafts",
    "description": "One short founder message per proposed action.",
    "input_schema": {
        "type": "object",
        "properties": {
            "drafts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["id", "subject", "body"],
                },
            }
        },
        "required": ["drafts"],
    },
}


def draft_nudges(plan: dict, *, model: str | None = None) -> dict:
    """Draft one founder message per proposed action. Runs Claude every run; raises
    when the SDK or the key is missing. With nothing proposed there is nothing to
    draft."""
    model = model or _client.MODEL
    proposed = plan.get("proposed", [])
    if not proposed:
        return {"live": True, "drafts": {}, "model": model}
    c = _client.require_client()

    items = "\n".join(f"- [{a['id']}] {a['motion']} (moves {a['moves']}; {a['rationale']})"
                      for a in proposed)
    system = ("You draft short, specific founder messages a growth operator could send. "
              "Plain language, no buzzwords, no em-dashes. One message per action.")
    resp = c.messages.create(
        model=model,
        max_tokens=4000,
        system=system,
        tools=[DRAFTS_TOOL],
        tool_choice={"type": "tool", "name": "founder_drafts"},
        messages=[{"role": "user", "content": f"Draft one message per action:\n{items}"}],
    )
    block = next((b for b in resp.content if getattr(b, "type", "") == "tool_use"), None)
    drafts = {d["id"]: {"subject": d["subject"], "body": d["body"]}
              for d in (block.input.get("drafts", []) if block else [])}
    return {"live": True, "drafts": drafts, "model": model,
            "usage": {"input_tokens": resp.usage.input_tokens,
                      "output_tokens": resp.usage.output_tokens}}


def brand_check(text: str) -> dict | None:
    """Grade a draft against the deslop brand bar. None when deslop is absent."""
    if _deslop_lint is None:
        return None
    try:
        findings = _deslop_lint(text)
        n = len(findings) if hasattr(findings, "__len__") else int(bool(findings))
        score = max(0, 100 - n * 10)
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"
        return {"grade": grade, "score": score, "findings": n}
    except Exception:
        return None


def attach(plan: dict, drafted: dict) -> dict:
    """Attach each draft (and its brand grade) to its proposed action, so the gate
    ledger renders the message under the motion. Mutates and returns the plan."""
    drafts = drafted.get("drafts", {})
    for a in plan.get("proposed", []):
        d = drafts.get(a["id"])
        if d:
            a["draft"] = {"subject": d["subject"], "body": d["body"]}
            b = brand_check(d["body"])
            if b:
                a["draft"]["brand"] = b
    return plan
