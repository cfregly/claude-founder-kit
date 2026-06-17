# NOTE: no `from __future__ import annotations` here on purpose. FastMCP reads
# real type annotations off each @mcp.tool() function to build the schema; with
# stringized annotations it calls issubclass() on a str and crashes at import.
import json
from pathlib import Path

from .anthropic_client import analyze_pitch_with_claude
from .growth import classify_use_cases_as_dict, growth_office_hours, score_growth_as_dict
from .router import route_as_dict
from .scoring_tools import office_hours, score_as_dict

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - optional dependency
    FastMCP = None  # type: ignore


def _load_pricing() -> dict:
    pricing_path = Path(__file__).resolve().parent.parent / "pricing.json"
    return json.loads(pricing_path.read_text())


def _estimate_unit_economics(
    input_tokens: int,
    output_tokens: int,
    requests_per_month: int,
    model: str = "claude-sonnet-4-6",
) -> dict:
    pricing = _load_pricing()
    model_pricing = pricing["models"].get(model)
    if model_pricing is None:
        return {"error": f"unknown model '{model}'", "valid_models": sorted(pricing["models"])}
    input_cost_per_mtok = model_pricing["input_per_mtok"]
    output_cost_per_mtok = model_pricing["output_per_mtok"]
    input_cost = (input_tokens * requests_per_month / 1_000_000) * input_cost_per_mtok
    output_cost = (output_tokens * requests_per_month / 1_000_000) * output_cost_per_mtok
    total = input_cost + output_cost
    return {
        "model": model,
        "monthly_input_cost_usd": round(input_cost, 2),
        "monthly_output_cost_usd": round(output_cost, 2),
        "monthly_total_cost_usd": round(total, 2),
        "cost_per_request_usd": round(total / max(1, requests_per_month), 6),
        "pricing_note": pricing.get("_verify", "Verify pricing before quoting."),
    }


if FastMCP is not None:
    mcp = FastMCP("claude-startup-linter")

    @mcp.tool()
    def score_startup_signal(pitch: str) -> str:
        """Score value prop, urgency, differentiation, platform risk, distribution, and data boundary."""
        return json.dumps(score_as_dict(pitch), indent=2)

    @mcp.tool()
    def route_claude_model(task: str, risk: str = "medium", context_tokens: int = 8000) -> str:
        """Choose a Claude model based on task complexity, risk, and context size."""
        return json.dumps(route_as_dict(task, risk, context_tokens), indent=2)

    @mcp.tool()
    def estimate_unit_economics(input_tokens: int, output_tokens: int, requests_per_month: int, model: str = "claude-sonnet-4-6") -> str:
        """Estimate monthly cost and per-request cost for a Claude workload using pricing.json."""
        return json.dumps(_estimate_unit_economics(input_tokens, output_tokens, requests_per_month, model), indent=2)

    @mcp.tool()
    def draft_founder_intervention(pitch: str) -> str:
        """Draft a founder intervention: value prop, wedge, architecture, platform risk, and metrics.

        Runs Claude and needs ANTHROPIC_API_KEY set."""
        result = analyze_pitch_with_claude(pitch)
        return result["response"]

    @mcp.tool()
    def founder_office_hours(pitch: str) -> str:
        """Run the AI-startup advisor office-hours script: score the pitch, then
        return the forcing questions for its weak dimensions (why now, why not the
        frontier labs or the cloud, what compounds, data boundary, unit economics)."""
        return json.dumps(office_hours(pitch), indent=2)

    @mcp.tool()
    def score_growth_readiness(pitch: str) -> str:
        """Score the founder's growth spine: Relationship, then Activation, then
        Retention. Returns the weakest stage to fix first and why."""
        return json.dumps(score_growth_as_dict(pitch), indent=2)

    @mcp.tool()
    def classify_ai_use_cases(pitch: str) -> str:
        """Sort the pitch's AI use cases by return horizon and risk into Dot (ship
        now, drives activation), Dash (build next, the retention layer), and Star
        (the high-ceiling vision bet)."""
        return json.dumps(classify_use_cases_as_dict(pitch), indent=2)

    @mcp.tool()
    def founder_growth_office_hours(pitch: str) -> str:
        """Run the growth office-hours script: score Relationship -> Activation ->
        Retention, classify the use-case portfolio, and return forcing questions
        for the weakest stage (the cheapest acquisition is the retention you keep)."""
        return json.dumps(growth_office_hours(pitch), indent=2)
else:
    mcp = None


def main() -> None:
    if mcp is None:
        raise RuntimeError("mcp package not installed. Run: pip install mcp")
    mcp.run()


if __name__ == "__main__":
    main()
