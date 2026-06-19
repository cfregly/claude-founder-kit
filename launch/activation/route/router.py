"""Route a batch of companies to the outreach brief that hits their bottleneck, and draft each email
into the gated outbox.

Deterministic by construction. A keyword router scores each company's one-line description against the
two briefs' signal words and routes it: programmatic tool calling (Token MINNing) for builders whose
bottleneck is cost at scale, Citations for builders whose bottleneck is trust to ship. The matching
outreach-example template is filled per company. The signal words and the dividing line are the ones
written in outreach-examples/README.md, kept in sync here.

Nothing is sent. Drafts land in the inert outbox for a human to approve, the same gate boundary the rest
of the loop carries: drafting is allowed, sending never runs unattended. The optional refine pass asks
Claude to classify the companies the keywords could not call and add a one-line reason. It needs a key
and it also only drafts, never sends.
"""

from __future__ import annotations

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]  # the launch/ module root
EXAMPLES = ROOT / "outreach-examples"

# The signal words per brief. ptc = cost at scale (an agent that fans out over data it then crunches).
# citations = trust to ship (answers over the user's own documents that must be verifiable). These
# mirror the segmentation note in outreach-examples/README.md.
SIGNALS = {
    "ptc": ["agent", "automat", "ops", "observability", "monitor", "log", "trace", "usage",
            "meter", "billing", "account", "cohort", "analytic", "incident", "pipeline", "ingest",
            "scrape", "crawl", "rollup", "roll-up", "telemetry", "dashboard"],
    "citations": ["document", "contract", "record", "filing", "claim", "policy", "policies",
                  "complian", "regulat", "legal", "law", "health", "clinical", "medical", "patient",
                  "fintech", "finance", "insurance", "kyc", "diligence", "knowledge base", "citation",
                  "source", "ground"],
}
BRIEF_EMAIL = {"ptc": "ptc-email.md", "citations": "citations-email.md"}


def classify(one_liner: str) -> tuple[str, dict]:
    """Score a one-line description against each brief's signal words. Returns (brief, scores), where
    brief is 'ptc', 'citations', or 'unrouted' when there is no signal or the two tie."""
    text = (one_liner or "").lower()
    scores = {brief: sum(1 for w in words if w in text) for brief, words in SIGNALS.items()}
    top = max(scores, key=scores.get)
    tied = [b for b in scores if scores[b] == scores[top]]
    if scores[top] == 0 or len(tied) > 1:
        return "unrouted", scores
    return top, scores


def _slug(company: str) -> str:
    s = "".join(ch if ch.isalnum() else "-" for ch in (company or "company").lower())
    return "-".join(p for p in s.split("-") if p) or "company"


def _rel(path: pathlib.Path) -> str:
    """A path relative to the launch root when it sits under it, else the path as given. Keeps the
    receipt readable for the default outbox without breaking when a caller points it elsewhere."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _fill(template: str, row: dict) -> str:
    """Fill the outreach template for one company. Only the first-name placeholder is substituted, so
    the neutral your-name sign-off and the links stay as written."""
    first = (row.get("first_name") or "there").strip() or "there"
    return template.replace("{first_name}", first)


def _read_batch(batch_path) -> list[dict]:
    with open(batch_path, newline="") as f:
        return list(csv.DictReader(f))


def route(batch_path, *, outbox=None) -> dict:
    """Classify every company in the batch CSV and draft the matching email into the outbox. Pure
    deterministic: no key, no network. The CSV needs a `company` column and a one-line description in
    `one_liner` or `description`, and an optional `first_name`. Returns a routing receipt."""
    outbox = pathlib.Path(outbox) if outbox else (ROOT / "out" / "outbox")
    outbox.mkdir(parents=True, exist_ok=True)
    templates = {brief: (EXAMPLES / fname).read_text() for brief, fname in BRIEF_EMAIL.items()}

    routed = []
    for row in _read_batch(batch_path):
        company = (row.get("company") or "").strip()
        one_liner = row.get("one_liner") or row.get("description") or ""
        brief, scores = classify(one_liner)
        rec = {"company": company, "one_liner": one_liner, "brief": brief,
               "scores": scores, "draft": None, "by": "keywords"}
        if brief != "unrouted":
            path = outbox / f"{_slug(company)}.{brief}.md"
            path.write_text(_fill(templates[brief], row))
            rec["draft"] = _rel(path)
        routed.append(rec)

    return _summary(routed, outbox)


def _summary(routed: list, outbox: pathlib.Path) -> dict:
    return {
        "total": len(routed),
        "ptc": sum(1 for r in routed if r["brief"] == "ptc"),
        "citations": sum(1 for r in routed if r["brief"] == "citations"),
        "unrouted": sum(1 for r in routed if r["brief"] == "unrouted"),
        "outbox": _rel(outbox),
        "routed": routed,
    }


# --- the optional judgment layer: Claude classifies the ones the keywords could not call ---

ROUTE_TOOL = {
    "name": "route_companies",
    "description": "Classify each company to the brief that fits its bottleneck, or neither.",
    "input_schema": {
        "type": "object",
        "properties": {
            "routes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "brief": {"type": "string", "enum": ["ptc", "citations", "neither"]},
                        "why": {"type": "string"},
                    },
                    "required": ["company", "brief", "why"],
                },
            }
        },
        "required": ["routes"],
    },
}

_SYSTEM = (
    "You route a startup to one of two Claude feature briefs by its bottleneck, or to neither. "
    "ptc (programmatic tool calling) is for builders whose bottleneck is cost at scale: an agent that "
    "calls a tool many times over data it then crunches, so the bill grows with the data. citations is "
    "for builders whose bottleneck is trust to ship: a product that answers over the user's own "
    "documents where a wrong source is a non-starter. If neither fits, say neither. One short reason each."
)


def refine(summary: dict, *, outbox=None, model: str | None = None) -> dict:
    """Ask Claude to classify the companies the keyword router left unrouted, and draft the newly routed
    into the same outbox. Needs a key and the SDK, raises without them, and never sends. Updates and
    returns the receipt. This is the judgment layer over the deterministic spine."""
    from ..platform import client as _client

    unrouted = [r for r in summary["routed"] if r["brief"] == "unrouted"]
    if not unrouted:
        return summary
    outbox = pathlib.Path(outbox) if outbox else (ROOT / "out" / "outbox")
    c = _client.require_client()
    model = model or _client.MODEL
    templates = {brief: (EXAMPLES / fname).read_text() for brief, fname in BRIEF_EMAIL.items()}

    listing = "\n".join(f"- {r['company']}: {r['one_liner']}" for r in unrouted)
    resp = c.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM,
        tools=[ROUTE_TOOL],
        tool_choice={"type": "tool", "name": "route_companies"},
        messages=[{"role": "user", "content": f"Route these companies:\n{listing}"}],
    )
    calls = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
    decided = {d["company"]: d for call in calls for d in call.input.get("routes", [])}

    by_company = {r["company"]: r for r in summary["routed"]}
    for r in unrouted:
        d = decided.get(r["company"])
        if not d or d["brief"] == "neither":
            r["by"] = "claude:neither"
            continue
        brief = d["brief"]
        path = outbox / f"{_slug(r['company'])}.{brief}.md"
        # find the original row's first name from the receipt if present, else greet plainly
        path.write_text(templates[brief].replace("{first_name}", "there"))
        r.update(brief=brief, draft=_rel(path), by="claude", why=d.get("why", ""))
        by_company[r["company"]] = r

    return _summary(list(by_company.values()), outbox)
