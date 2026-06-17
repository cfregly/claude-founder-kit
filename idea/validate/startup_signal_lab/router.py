from __future__ import annotations

import os
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ModelRoute:
    model: str
    reason: str
    cache_static_context: bool
    human_review: bool
    expected_latency_class: str


def route_claude_model(task: str, risk: str = "medium", context_tokens: int = 8000) -> ModelRoute:
    """Opinionated startup-friendly Claude model router.

    This is not meant to be universal. It is a demo of how to encode model routing
    as product architecture: business value, risk, tool complexity, and data scope.
    """
    task_l = task.lower()
    risk_l = risk.lower()

    fast_model = os.getenv("CLAUDE_FAST_MODEL", "claude-haiku-4-5")
    default_model = os.getenv("CLAUDE_DEFAULT_MODEL", "claude-sonnet-4-6")
    deep_model = os.getenv("CLAUDE_DEEP_MODEL", "claude-opus-4-8")

    simple_patterns = ["classify", "extract", "tag", "summarize", "route", "dedupe"]
    deep_patterns = ["strategy", "ambiguous", "multi-step", "agent", "codebase", "architecture", "legal", "safety"]

    if any(p in task_l for p in simple_patterns) and risk_l in {"low", "medium"}:
        return ModelRoute(
            model=fast_model,
            reason="Low-risk structured transformation; optimize for cost and latency.",
            cache_static_context=context_tokens > 4000,
            human_review=False,
            expected_latency_class="fast",
        )

    if risk_l == "high" or any(p in task_l for p in deep_patterns):
        return ModelRoute(
            model=deep_model,
            reason="High ambiguity or high consequence; prioritize reasoning quality and tool discipline.",
            cache_static_context=context_tokens > 4000,
            human_review=True,
            expected_latency_class="moderate",
        )

    return ModelRoute(
        model=default_model,
        reason="Default startup production path: strong quality, fast iteration, reasonable unit economics.",
        cache_static_context=context_tokens > 4000,
        human_review=risk_l != "low",
        expected_latency_class="fast",
    )


def route_as_dict(task: str, risk: str = "medium", context_tokens: int = 8000) -> dict:
    return asdict(route_claude_model(task, risk, context_tokens))
