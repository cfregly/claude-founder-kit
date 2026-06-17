from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Iterable

from .anthropic_client import analyze_pitch_with_claude


def _cost_usd(model: str, usage: dict) -> float | None:
    """Price a Claude call from pricing.json. Returns None for an unknown model."""
    pricing = json.loads((Path(__file__).resolve().parent.parent / "pricing.json").read_text())
    model_pricing = pricing["models"].get(model)
    if model_pricing is None or not isinstance(usage, dict):
        return None
    input_tokens = usage.get("input_tokens") or 0
    output_tokens = usage.get("output_tokens") or 0
    return round(
        (input_tokens * model_pricing["input_per_mtok"] + output_tokens * model_pricing["output_per_mtok"])
        / 1_000_000,
        6,
    )


@dataclass(frozen=True)
class EvalCase:
    name: str
    pitch: str
    must_include: tuple[str, ...]


DEFAULT_EVALS = [
    EvalCase(
        name="platform-risk-heavy",
        pitch="We are an AI agent platform built on OpenAI and Anthropic for enterprise workflows. We help teams automate tasks with agents and dashboards.",
        must_include=("platform", "moat", "workflow"),
    ),
    EvalCase(
        name="clear-ops-pain",
        pitch="We reduce debugging time for AI support agents by 42% by analyzing production traces, PII-safe summaries, and failed tool calls inside the customer support workflow.",
        must_include=("debug", "production", "metric"),
    ),
]


def run_evals(cases: Iterable[EvalCase] = DEFAULT_EVALS) -> list[dict]:
    """Grade Claude's intervention on each case. Runs Claude every time and needs
    ANTHROPIC_API_KEY set: analyze_pitch_with_claude raises if it is missing."""
    results: list[dict] = []
    for case in cases:
        start = perf_counter()
        output = analyze_pitch_with_claude(case.pitch)
        elapsed_ms = round((perf_counter() - start) * 1000, 1)
        response = output["response"].lower()
        hits = [term for term in case.must_include if term.lower() in response]
        usage = output.get("usage") if isinstance(output.get("usage"), dict) else None
        results.append(
            {
                "name": case.name,
                "elapsed_ms": elapsed_ms,
                "quality_hit_rate": round(len(hits) / len(case.must_include), 2),
                "hits": hits,
                "overall_signal_score": output["score"]["overall"],
                "model": output["route"]["model"],
                "input_tokens": usage.get("input_tokens") if usage else None,
                "output_tokens": usage.get("output_tokens") if usage else None,
                "cost_usd": _cost_usd(output["route"]["model"], usage) if usage else None,
            }
        )
    return results
