from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import pathlib
from typing import Any

from .scoring_tools import clamp

# Relationship -> Activation -> Retention (R-A-R) is the founder growth spine this
# linter scores. It is the same loop the advisor runs on the founder's own
# company: earn trust, get them to first value fast, then keep them and expand.
# Why a loop and not a funnel: retained users are the cheapest acquisition you
# have, so retention feeds the top of the next cohort.
#
# Motions this borrows from, in plain terms:
#   - Growth loops over funnels, retention as the engine of acquisition: the
#     product-led trilogy of acquisition / retention / monetization loops.
#   - Time-to-value: shorten sign-up to the aha moment, and pick an activation
#     metric because it correlates with retention, not because it looks big.
#   - A use-case portfolio split by return horizon and risk: ship the small
#     proven bets now, build the connective ones, narrate the high-ceiling one.

_RULES = json.loads((pathlib.Path(__file__).parent / "slop_rules.json").read_text())
SLOP_TERMS = _RULES["buzzwords"] + _RULES["phrases"]


def _has_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(p in t for p in patterns)


@dataclass(frozen=True)
class GrowthReadinessScore:
    relationship: int
    activation: int
    retention: int
    overall: int
    weakest_stage: str
    stage_focus: str
    flags: list[str]


RELATIONSHIP_SIGNALS = [
    "community", "design partner", "waitlist", "referral", "word of mouth",
    "invite", "accelerator", "yc", "techstars", "investor", "vc", "newsletter",
    "discord", "champion", "build in public", "open source", "office hours",
]
ACTIVATION_SIGNALS = [
    "onboarding", "time to value", "time-to-value", "first value", "aha",
    "first run", "first build", "first call", "setup", "quickstart", "activation",
    "free trial", "freemium", "self-serve", "self serve", "sign up", "signup",
]
RETENTION_SIGNALS = [
    "retention", "retained", "weekly active", "daily active", "habit", "renewal",
    "renew", "expansion", "net revenue retention", "nrr", "net dollar retention",
    "ndr", "engagement retention", "churn", "stickiness", "system of record",
    "second use", "comes back", "recurring", "production usage",
]


def score_growth_readiness(text: str) -> GrowthReadinessScore:
    """Score a startup pitch on the Relationship -> Activation -> Retention spine.

    Deterministic and explainable for live demos. In production, pair these checks
    with real funnel telemetry: time-to-value, an activation metric chosen because
    it correlates with retention, and net revenue retention by cohort.
    """
    if not text or len(text.strip()) < 20:
        return GrowthReadinessScore(
            relationship=1, activation=1, retention=1, overall=1,
            weakest_stage="relationship",
            stage_focus="No signal yet. Name one buyer who already trusts you, and the first value they would feel.",
            flags=["Not enough signal to evaluate."],
        )

    relationship = 4
    activation = 4
    retention = 4
    flags: list[str] = []

    if _has_any(text, RELATIONSHIP_SIGNALS):
        relationship += 3
    else:
        flags.append("Relationship is thin: who already trusts you, and what community or partner brings the next 25 buyers?")

    if _has_any(text, ACTIVATION_SIGNALS):
        activation += 3
    else:
        flags.append("Activation is undefined: name the aha moment and the time-to-value from sign-up to first useful result.")

    # A measurable first-value claim is the strongest activation signal.
    if _has_any(text, ["minutes", "same day", "same-day", "first day", "under "]):
        activation += 1

    if _has_any(text, RETENTION_SIGNALS):
        retention += 3
    else:
        flags.append("Retention is unproven: what brings a user back the second time, and what expands as they grow?")

    # Evals and workflow ownership are the retention moat for an AI product:
    # the eval set wins the renewal after the demo wins the trial.
    if _has_any(text, ["evals", "eval set", "workflow", "system of record"]):
        retention += 1

    # All top-of-funnel, no retention is the leaky-bucket failure.
    if relationship >= 7 and retention <= 4:
        flags.append("Leaky bucket: strong top of funnel, weak retention. Acquisition poured into low retention compounds to near zero.")

    slop_hits = [t for t in SLOP_TERMS if t in text.lower()]
    if slop_hits:
        flags.append(
            "De-slop the growth story: " + ", ".join(slop_hits[:3]) + "; replace each with a metric or a named motion."
        )

    relationship = clamp(relationship)
    activation = clamp(activation)
    retention = clamp(retention)
    overall = round((relationship + activation + retention) / 3)

    stages = {"relationship": relationship, "activation": activation, "retention": retention}
    weakest = min(stages, key=stages.get)
    focus = {
        "relationship": "Earn the next cohort's trust before chasing volume: pick one community or partner and become the obvious helper there.",
        "activation": "Shorten time-to-value. Cut every step between sign-up and the first useful result, and instrument the aha moment.",
        "retention": "Build the second-use loop before scaling spend. Retained users are the cheapest acquisition channel you have.",
    }[weakest]

    return GrowthReadinessScore(
        relationship=relationship,
        activation=activation,
        retention=retention,
        overall=overall,
        weakest_stage=weakest,
        stage_focus=focus,
        flags=flags,
    )


def score_growth_as_dict(text: str) -> dict[str, Any]:
    return asdict(score_growth_readiness(text))


@dataclass(frozen=True)
class UseCasePortfolio:
    dot: list[str]   # small, proven, fast payback: ship now, drives activation
    dash: list[str]  # connective, multi-step work: build next, the retention layer
    star: list[str]  # high-ceiling bet: narrate it, do not stake the company yet
    advice: str


DOT_SIGNALS = ["classify", "extract", "summariz", "transcript", "tag", "draft",
               "lookup", "faq", "ticket", "categoriz", "label"]
DASH_SIGNALS = ["agent", "workflow", "copilot", "multi-step", "tool use", "mcp",
                "integration", "pipeline", "automation", "orchestrat"]
STAR_SIGNALS = ["autonomous", "self-improving", "new category", "moonshot",
                "general-purpose", "research lab"]


def classify_use_cases(text: str) -> UseCasePortfolio:
    """Sort the AI use cases in a pitch by return horizon and risk.

    Dot: small, proven, fast payback. Ship these now; they fund the rest and
    drive activation. Dash: connective, multi-step work; build these as the
    retention and expansion layer. Star: the high-ceiling bet; narrate it, but
    do not stake the company on it before the Dots are paying.
    """
    t = text.lower()
    dot = [w for w in DOT_SIGNALS if w in t]
    dash = [w for w in DASH_SIGNALS if w in t]
    star = [w for w in STAR_SIGNALS if w in t]

    if not dot and (dash or star):
        advice = "No fast-payback Dot in sight. Pick one small, proven use case that pays back in about a quarter, ship it, and let it fund the bigger bets."
    elif dot and not dash:
        advice = "Good Dot. Now design the Dash that keeps them: the connective workflow that turns one win into daily use."
    elif star and not dot and not dash:
        advice = "All Star, no floor. Sequence backward: what is the smallest Dot that proves the vision and earns the next round?"
    else:
        advice = "Healthy spread. Ship the Dots for activation, build the Dash for retention, and narrate one Star for the vision."

    return UseCasePortfolio(dot=dot, dash=dash, star=star, advice=advice)


def classify_use_cases_as_dict(text: str) -> dict[str, Any]:
    return asdict(classify_use_cases(text))


# Growth office-hours script: the questions an activation-and-retention advisor
# asks, keyed to the stage each one pressure-tests. Deterministic, so a founder
# gets the same interrogation every run and can take it home as homework.
GROWTH_ADVISOR_QUESTIONS: dict[str, list[str]] = {
    "relationship": [
        "Who already trusts you, and what community or partner gives you the next 25 buyers without paid spend?",
        "What is the referral loop: what makes a happy user recruit the next one?",
    ],
    "activation": [
        "What is the aha moment, and how many minutes from sign-up to feeling it?",
        "Which activation metric did you pick because it correlates with retention, not because it looks big?",
    ],
    "retention": [
        "What brings a user back the second time, unprompted, on their own data?",
        "Is your net dollar retention above 100%, and is engagement retention (the leading indicator) climbing before paid retention?",
        "For an AI product: what is your eval set, the thing that wins the renewal after the demo wins the trial?",
    ],
}

GROWTH_CLOSERS = [
    "Draw your growth as a loop, not a funnel: what does a retained user feed back into acquisition?",
    "If you could fix only one stage this quarter, relationship, activation, or retention, which compounds fastest for you?",
]


def growth_advisor_questions(score: GrowthReadinessScore) -> list[dict[str, Any]]:
    weak = {
        "relationship": score.relationship <= 5,
        "activation": score.activation <= 5,
        "retention": score.retention <= 5,
    }
    agenda = [
        {"stage": stage, "questions": GROWTH_ADVISOR_QUESTIONS[stage]}
        for stage, is_weak in weak.items()
        if is_weak
    ]
    # Always interrogate the weakest stage, even when nothing scored at or below 5.
    if not agenda:
        agenda.append({"stage": score.weakest_stage, "questions": GROWTH_ADVISOR_QUESTIONS[score.weakest_stage]})
    agenda.append({"stage": "closers", "questions": GROWTH_CLOSERS})
    return agenda


def growth_office_hours(text: str) -> dict[str, Any]:
    """Score the R-A-R spine, classify the use-case portfolio, and return the
    office-hours agenda for the weakest stage."""
    score = score_growth_readiness(text)
    portfolio = classify_use_cases(text)
    return {
        "overall": score.overall,
        "relationship": score.relationship,
        "activation": score.activation,
        "retention": score.retention,
        "weakest_stage": score.weakest_stage,
        "stage_focus": score.stage_focus,
        "use_case_portfolio": asdict(portfolio),
        "agenda": growth_advisor_questions(score),
    }
