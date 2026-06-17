from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import pathlib
import re
from typing import Any


@dataclass(frozen=True)
class StartupSignalScore:
    value_prop: int
    urgency: int
    differentiation: int
    platform_risk: int
    distribution: int
    data_boundary: int
    overall: int
    flags: list[str]
    suggested_wedge: str


def _has_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(p in t for p in patterns)


# Buzzwords that spend words without carrying signal. Slop costs a point because
# adjectives displace numbers. The shared canon (buzzword stems plus filler
# phrases) loads from slop_rules.json, synced from the claude-deslop repo; do
# not hand-edit it. Stems like "leverag" match as substrings.
_RULES = json.loads((pathlib.Path(__file__).parent / "slop_rules.json").read_text())
SLOP_TERMS = _RULES["buzzwords"] + _RULES["phrases"]


def _count_specifics(text: str) -> int:
    # A rough proxy for concrete claims: numbers, named buyers, before/after, integrations.
    return len(re.findall(r"\b\d+(?:\.\d+)?%?|\$\d+|[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+\b", text))


def clamp(value: int, low: int = 1, high: int = 10) -> int:
    return max(low, min(high, value))


def score_startup_signal(text: str) -> StartupSignalScore:
    """Score a startup pitch for founder-facing intervention.

    Scores are intentionally simple and explainable for live demos. In production,
    combine deterministic checks with Claude-as-judge evals and founder outcomes.
    """
    if not text or len(text.strip()) < 20:
        return StartupSignalScore(
            value_prop=1,
            urgency=1,
            differentiation=1,
            platform_risk=9,
            distribution=1,
            data_boundary=1,
            overall=1,
            flags=["Not enough signal to evaluate."],
            suggested_wedge="Start with a one-sentence painkiller claim for a specific buyer.",
        )

    specifics = _count_specifics(text)
    value_prop = 4 + min(3, specifics // 2)
    urgency = 4
    differentiation = 4
    platform_risk = 5
    distribution = 4
    data_boundary = 4
    flags: list[str] = []

    if _has_any(text, ["save", "reduce", "faster", "latency", "cost", "revenue", "conversion", "payback"]):
        value_prop += 2
        urgency += 1
    else:
        flags.append("Value proposition needs a measurable before/after claim.")

    if _has_any(text, ["compliance", "regulated", "audit", "security", "privacy", "pii", "hipaa", "soc 2", "sox"]):
        data_boundary += 3
        urgency += 1

    # Platform risk is whether you ANSWER "why won't the platform absorb this?",
    # not whether you name a vendor. Naming OpenAI with no answer raises the
    # risk; a real answer -- you own the workflow of record, the customer eval
    # set, the data boundary, a moat that compounds -- lowers it. The old check
    # only saw the vendor name, so the pitch that best answered platform risk
    # scored worst. Now an answer wins over a mention.
    answers_platform_risk = _has_any(text, [
        "why won't", "why wouldn't", "wouldn't the", "won't the model",
        "workflow of record", "system of record", "own the workflow",
        "eval set", "data boundary", "switching cost", "not the model",
        "compounds", "proprietary data", "privileged", "audit trail",
    ])
    names_platform = _has_any(text, [
        "openai", "anthropic", "claude", "gemini", "cloud", "aws", "bedrock",
        "azure", "model provider", "frontier model", "incumbent", "the platform",
    ])
    if answers_platform_risk:
        platform_risk -= 2
    elif names_platform:
        platform_risk += 2
        flags.append("Explicit platform-risk story required: why won't the model/cloud platform absorb this?")

    if _has_any(text, ["proprietary data", "workflow", "system of record", "network", "feedback loop", "usage data"]):
        differentiation += 3
    else:
        flags.append("Moat is not yet obvious; explain what compounds with each user or workflow.")

    if _has_any(text, ["yc", "design partner", "pilot", "customer", "paid", "usage", "arr", "retention"]):
        distribution += 3
    else:
        flags.append("Distribution path is fuzzy; name the first 25 buyers and the activation event.")

    if _has_any(text, ["always-on", "embedded", "inline", "copilot", "agent", "mcp", "ci", "ide"]):
        differentiation += 1
        value_prop += 1

    slop_hits = [t for t in SLOP_TERMS if t in text.lower()]
    if slop_hits:
        value_prop -= 1
        flags.append(
            "De-slop the pitch: buzzwords carry no signal ("
            + ", ".join(slop_hits[:3])
            + "); replace each with a number or a named workflow."
        )

    value_prop = clamp(value_prop)
    urgency = clamp(urgency)
    differentiation = clamp(differentiation)
    platform_risk = clamp(platform_risk)
    distribution = clamp(distribution)
    data_boundary = clamp(data_boundary)
    # Platform risk is inverted in the overall score: lower risk is better.
    overall = round((value_prop + urgency + differentiation + distribution + data_boundary + (11 - platform_risk)) / 6)

    # A strong pitch with no weak dimensions should hear "scale it", not the
    # generic "narrow the buyer" -- telling a founder who already named a narrow
    # buyer and a painful metric to narrow further is the wedge logic misfiring.
    if overall >= 8 or (overall >= 7 and not flags):
        wedge = "Strong signal across the board. Pick the single wedge workflow, then instrument time-to-value and cost per successful task as you scale it."
    elif platform_risk >= 7:
        wedge = "Lead with platform-risk mitigation: data, workflow ownership, evals, and customer-specific integrations."
    elif differentiation >= 7 and distribution <= 5:
        wedge = "The product may be sharp, but GTM is the bottleneck; define the partner/channel motion."
    else:
        wedge = "Narrow the buyer and convert the pitch from category language to a painful operational metric."

    return StartupSignalScore(
        value_prop=value_prop,
        urgency=urgency,
        differentiation=differentiation,
        platform_risk=platform_risk,
        distribution=distribution,
        data_boundary=data_boundary,
        overall=overall,
        flags=flags,
        suggested_wedge=wedge,
    )


def score_as_dict(text: str) -> dict[str, Any]:
    return asdict(score_startup_signal(text))


# The advisor's forcing questions: what an AI-startup advisor actually asks in
# office hours, keyed to the dimension each one pressure-tests. These are
# specific to AI startups, frontier-lab and cloud platform risk, model
# economics, data boundaries, and moats that compound with usage, not generic
# startup coaching. The linter doubles as an office-hours script the founder
# takes home.
ADVISOR_QUESTIONS: dict[str, list[str]] = {
    "value_prop": [
        "What painful job does this kill, for which exact buyer and role?",
        "What is the measured before/after in their world: hours, dollars, or conversion?",
    ],
    "urgency": [
        "Why now? What changed this year: model capability, cost per token, or regulation?",
        "If someone tried this 18 months ago, why did it fail then and work now?",
    ],
    "differentiation": [
        "What compounds with every user or workflow, so you get harder to rip out over time?",
        "If your accuracy or cost lead is one good prompt, what stops a competitor copying it next week?",
    ],
    "platform_risk": [
        "Why won't OpenAI or Anthropic fold this into the model or a first-party feature?",
        "Why won't AWS, GCP, or Azure ship it natively and win on distribution, the way the cloud absorbed the last wave of ML tooling?",
        "What do you own that a platform does not: proprietary data, the workflow of record, distribution, or compliance trust?",
    ],
    "distribution": [
        "Name the first 25 buyers. What is the activation event that turns a trial into production usage?",
        "Who already holds the trust and the install base, and could they be a channel instead of a competitor?",
    ],
    "data_boundary": [
        "What customer data leaves your boundary to a third-party model API, and how do you keep it in-bounds?",
        "What is the security and eval story a regulated buyer needs before they let an agent act?",
    ],
}

# Closers an advisor asks every founder, whatever the score.
ADVISOR_CLOSERS = [
    "What single metric would you stake the next 30 days on?",
    "Have you priced naive vs cached vs routed inference? What is your cost per successful task, and does it fall with scale?",
]


def advisor_questions(score: StartupSignalScore) -> list[dict[str, Any]]:
    """The office-hours script: forcing questions for the weak dimensions.

    Deterministic, so a founder gets the same interrogation every run and an
    advisor can hand it over as homework. A dimension surfaces when it scored
    weak; for platform_risk, weak means HIGH risk.
    """
    weak = {
        "value_prop": score.value_prop <= 5,
        "urgency": score.urgency <= 5,
        "differentiation": score.differentiation <= 5,
        "platform_risk": score.platform_risk >= 6,
        "distribution": score.distribution <= 5,
        "data_boundary": score.data_boundary <= 5,
    }
    agenda = [
        {"dimension": dim, "questions": ADVISOR_QUESTIONS[dim]}
        for dim, is_weak in weak.items()
        if is_weak
    ]
    agenda.append({"dimension": "closers", "questions": ADVISOR_CLOSERS})
    return agenda


def office_hours(text: str) -> dict[str, Any]:
    """Score a pitch, then return the office-hours agenda for its weak spots."""
    score = score_startup_signal(text)
    return {
        "overall": score.overall,
        "suggested_wedge": score.suggested_wedge,
        "agenda": advisor_questions(score),
    }
