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
import re

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


# The use case within a segment. This is the hyper-personalization layer on top of the segment routing:
# same brief, but the opener names what the company actually builds. The phrases are noun phrases so they
# drop into "Quick tip for ...". The first matching use case wins, else the segment default.
USE_CASES = {
    "ptc": [
        (("usage", "billing", "meter", "plan-limit", "plan limit"), "an agent that rolls up usage across accounts"),
        (("log", "trace", "incident", "observability", "monitor"), "an agent that triages logs and traces across services"),
        (("analytic", "dashboard", "report", "bi "), "an agent that aggregates rows to answer a question"),
        (("churn", "health score", "retention", "crm"), "an agent that scores health across your customer base"),
        (("security", "vuln", "alert", "soc", "threat"), "an agent that triages findings across your fleet"),
    ],
    "citations": [
        (("contract", "clause", "legal", "law"), "a product that answers over contracts"),
        (("clinical", "medical", "patient", "health", "ehr"), "a product that answers over clinical notes"),
        (("filing", "kyc", "fintech", "finance", "bank"), "a product that answers over financial filings"),
        (("policy", "claim", "insurance"), "a product that answers over policies and claims"),
        (("support", "ticket", "knowledge", "help center"), "a product that answers over your support and knowledge docs"),
    ],
}
_USE_CASE_DEFAULT = {"ptc": "an agent that calls a tool many times",
                     "citations": "a product that answers over your users' own documents"}


def use_case(one_liner: str, brief: str) -> str:
    """The specific use case within a segment, for the opener. Falls back to the segment default."""
    text = (one_liner or "").lower()
    for keys, phrase in USE_CASES.get(brief, []):
        if any(k in text for k in keys):
            return phrase
    return _USE_CASE_DEFAULT.get(brief, "")


def _personalize(draft: str, phrase: str) -> str:
    """Tailor the opener to the use case: replace the generic 'Quick tip ...' line with one that names
    what this company builds. The rest of the email and every number stays exactly as written."""
    if not phrase:
        return draft
    return re.sub(r"Quick tip[^.\n]*\.", f"Quick tip for {phrase}.", draft, count=1)


# The body anchors in the two templates. The --refine pass replaces these with company-specific phrases
# so the whole email matches the workload, not just the opener. They are exact substrings of the
# committed templates; a test asserts they still exist so the substitution never silently no-ops.
PTC_WORKLOAD_ANCHOR = "your app calls your own tool to answer a question and that tool returns a lot of results"
PTC_TOOL_ANCHOR = "query_region_sales"
CITATIONS_DOC_ANCHOR = "a contract, a policy, or a support doc"


def _sanitize(phrase: str) -> str:
    """Keep a model-written phrase in house style: no dashes, no semicolons, trimmed."""
    return phrase.replace("—", " ").replace("–", " ").replace(";", ",").strip()


def _apply_body(text: str, brief: str, body: str, tool_name: str = "") -> str:
    """Substitute the company-specific body phrases into a draft at the known anchors. Pure: the model
    supplies only the short phrases, so the numbers, the code structure, and the links cannot drift."""
    body = _sanitize(body)
    if brief == "ptc":
        if body:
            text = text.replace(PTC_WORKLOAD_ANCHOR, body)
        tool = _sanitize(tool_name).replace(" ", "_")
        if tool:
            text = text.replace(PTC_TOOL_ANCHOR, tool)
    elif brief == "citations" and body:
        text = text.replace(CITATIONS_DOC_ANCHOR, body)
    return text


def _read_batch(batch_path) -> list[dict]:
    """Read the batch CSV, skipping blank lines and `#` comments so a sample file can label itself."""
    with open(batch_path, newline="") as f:
        rows = [ln for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
    return list(csv.DictReader(rows))


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
               "scores": scores, "draft": None, "use_case": None, "by": "keywords"}
        if brief != "unrouted":
            uc = use_case(one_liner, brief)
            path = outbox / f"{_slug(company)}.{brief}.md"
            path.write_text(_personalize(_fill(templates[brief], row), uc))
            rec["draft"], rec["use_case"] = _rel(path), uc
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


DEEPEN_TOOL = {
    "name": "personalize_bodies",
    "description": "Per company, the short phrases that tailor the email opener and body to its workload.",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "opener": {"type": "string"},
                        "body": {"type": "string"},
                        "tool_name": {"type": "string"},
                    },
                    "required": ["company", "opener", "body", "tool_name"],
                },
            }
        },
        "required": ["items"],
    },
}

_DEEPEN_SYSTEM = (
    "You tailor a cold outreach email to each company's workload, written in the second person to the "
    "founder. Always say 'your', never 'its' or 'their'. Plain language, no em-dashes, no semicolons, no "
    "buzzwords. Per company return an opener and a body that name the same workload, plus a tool name.\n"
    "ptc (cost at scale): `opener` is a noun phrase that follows 'Quick tip for ', naming what their "
    "agent does, for example 'an on-call agent that finds root causes across your logs and traces'. "
    "`body` completes 'If <body>, every result it pulls back lands in the model context' with a singular "
    "subject that starts with 'your' so it agrees with 'it pulls back', for example 'your on-call agent "
    "reads the logs, metrics, and traces to find a root cause'. `tool_name` is a snake_case tool for that "
    "workload, for example query_logs.\n"
    "citations (trust to ship): `opener` is 'a product that answers over <documents>', for example 'a "
    "product that answers over clinical notes'. `body` is a singular noun phrase for one such document "
    "that follows 'When you answer over ', for example 'a clinical note'. `tool_name` is an empty string.\n"
    "Keep the opener and the body under 18 words each, and make them name the same documents or workload."
)


def refine(summary: dict, *, outbox=None, model: str | None = None) -> dict:
    """The Claude layer over the deterministic route. First classify the companies the keywords left
    unrouted, then deepen every routed draft so the whole body matches the company, not just the opener.
    Needs a key and the SDK, raises without them, and never sends. Updates and returns the receipt."""
    from ..platform import client as _client

    outbox = pathlib.Path(outbox) if outbox else (ROOT / "out" / "outbox")
    c = _client.require_client()
    model = model or _client.MODEL
    summary = _classify_unrouted(summary, c=c, model=model, outbox=outbox)
    summary = _deepen_bodies(summary, c=c, model=model, outbox=outbox)
    return summary


def _classify_unrouted(summary: dict, *, c, model: str, outbox: pathlib.Path) -> dict:
    """Ask Claude to classify the companies the keyword router left unrouted, and draft the newly routed
    into the same outbox with the opener personalized."""
    unrouted = [r for r in summary["routed"] if r["brief"] == "unrouted"]
    if not unrouted:
        return summary
    templates = {brief: (EXAMPLES / fname).read_text() for brief, fname in BRIEF_EMAIL.items()}
    listing = "\n".join(f"- {r['company']}: {r['one_liner']}" for r in unrouted)
    resp = c.messages.create(
        model=model, max_tokens=1024, system=_SYSTEM, tools=[ROUTE_TOOL],
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
        uc = use_case(r["one_liner"], brief)
        path = outbox / f"{_slug(r['company'])}.{brief}.md"
        path.write_text(_personalize(templates[brief].replace("{first_name}", "there"), uc))
        r.update(brief=brief, draft=_rel(path), use_case=uc, by="claude", why=d.get("why", ""))
        by_company[r["company"]] = r
    return _summary(list(by_company.values()), outbox)


def _deepen_bodies(summary: dict, *, c, model: str, outbox: pathlib.Path) -> dict:
    """Rewrite every routed draft's body to the company's workload: the example sentence and, for ptc,
    the code tool name. Claude returns only the short phrases; the substitution is deterministic, so the
    numbers and links never move. This closes the gap between a personalized opener and a generic body."""
    routed = [r for r in summary["routed"] if r["brief"] in ("ptc", "citations")]
    if not routed:
        return summary
    listing = "\n".join(f"- {r['company']} [{r['brief']}]: {r['one_liner']}" for r in routed)
    resp = c.messages.create(
        model=model, max_tokens=1024, system=_DEEPEN_SYSTEM, tools=[DEEPEN_TOOL],
        tool_choice={"type": "tool", "name": "personalize_bodies"},
        messages=[{"role": "user", "content": f"Tailor the body for each company:\n{listing}"}],
    )
    calls = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
    pieces = {d["company"]: d for call in calls for d in call.input.get("items", [])}
    for r in routed:
        d = pieces.get(r["company"])
        draft_path = outbox / f"{_slug(r['company'])}.{r['brief']}.md"
        if not d or not draft_path.exists():
            continue
        # rewrite the opener to match the deepened body, so the two lines name one workload, not two
        opener = _sanitize(d.get("opener", "")) or r.get("use_case") or use_case(r["one_liner"], r["brief"])
        text = _personalize(draft_path.read_text(), opener)
        text = _apply_body(text, r["brief"], d.get("body", ""), d.get("tool_name", ""))
        draft_path.write_text(text)
        r["opener"], r["body"], r["deepened"] = opener, _sanitize(d.get("body", "")), True
    return summary
