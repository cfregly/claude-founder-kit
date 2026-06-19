"""The local harness: the Claude Agent SDK orchestrator for the weekly report.

The same pipeline, run as an agent. The eleven queries plus measure and operate
become in-process MCP tools, a PreToolUse hook enforces the gate (the outward
tools ask for approval, the never-set is denied), and an account-researcher
subagent briefs each PQA. The live agent requires `claude-agent-sdk` and
`ANTHROPIC_API_KEY`; the deterministic dry run is explicit.
"""

from __future__ import annotations

import json

from .. import pipeline
from ..measure import metrics
from ..operate import plan as planning
from ..platform import client as _client

try:
    from claude_agent_sdk import (
        AgentDefinition, ClaudeAgentOptions, HookMatcher,
        create_sdk_mcp_server, query, tool,
    )
    _SDK = True
except Exception:  # optional dependency: one harness, not the core
    _SDK = False

# The outward tools wait for approval; anything that spends, grants, or posts is
# denied outright. The gate ledger, enforced as a permission decision.
ASK_TOOLS = {"mcp__activation__send_founder_nudge", "mcp__activation__gtm_handoff"}
NEVER_PATTERNS = ("spend", "credit", "post_public", "publish", "tweet")

SYSTEM = (
    "You are a growth operator. Produce the weekly startup-signal report for the "
    "cohort. Call wr_measure on the cohort file, then wr_operate on the readout. "
    "For each product-qualified account, delegate a brief to the account-researcher "
    "subagent. Propose the outward motions but send nothing: the outward tools wait "
    "for the operator's approval."
)


def available() -> bool:
    return _SDK and _client.available()


def _missing_live_reason() -> str:
    reasons = []
    if not _SDK:
        reasons.append("claude-agent-sdk is not installed")
    if not _client.available():
        reasons.append("ANTHROPIC_API_KEY is not set or the anthropic SDK is unavailable")
    return "; ".join(reasons) or "live Agent SDK prerequisites are missing"


def _build_server():
    """The in-process MCP server: the deterministic functions as agent tools."""

    @tool("wr_run_queries", "Run the eleven adoption queries over a JSONL event log.",
          {"event_log": str})
    async def wr_run_queries(args):
        from ..capture import queries
        rows = queries.load(args["event_log"])
        return {"content": [{"type": "text", "text": json.dumps(queries.run_all(rows))}]}

    @tool("wr_measure", "Score a cohort JSON file into the activation readout.",
          {"cohort_json": str})
    async def wr_measure(args):
        with open(args["cohort_json"]) as f:
            out = metrics.summarize(json.load(f))
        return {"content": [{"type": "text", "text": json.dumps(out)}]}

    @tool("wr_operate", "Turn a readout JSON file into the gated plan.",
          {"readout_json": str})
    async def wr_operate(args):
        with open(args["readout_json"]) as f:
            out = planning.plan(json.load(f))
        return {"content": [{"type": "text", "text": json.dumps(out)}]}

    @tool("send_founder_nudge", "Send a drafted nudge to a founder (waits for approval).",
          {"account": str, "subject": str, "body": str})
    async def send_founder_nudge(args):
        return {"content": [{"type": "text", "text": f"queued nudge to {args['account']}"}]}

    @tool("gtm_handoff", "Hand a PQA to a named GTM owner (waits for approval).",
          {"account": str, "owner": str})
    async def gtm_handoff(args):
        return {"content": [{"type": "text", "text": f"queued handoff of {args['account']}"}]}

    return create_sdk_mcp_server(
        name="activation", version="0.1.0",
        tools=[wr_run_queries, wr_measure, wr_operate, send_founder_nudge, gtm_handoff],
    )


async def _gate_hook(input_data, tool_use_id, context):
    """PreToolUse gate: deny the never-set, ask for the outward tools, allow the rest."""
    name = input_data.get("tool_name", "")
    event = input_data.get("hook_event_name", "PreToolUse")
    if any(p in name.lower() for p in NEVER_PATTERNS):
        return {"hook_specific_output": {
            "hook_event_name": event, "permission_decision": "deny",
            "permission_decision_reason": "Spend, credits, and public posts are never done unattended."}}
    if name in ASK_TOOLS:
        return {"hook_specific_output": {
            "hook_event_name": event, "permission_decision": "ask",
            "permission_decision_reason": "Outward action: waits for the operator's approval."}}
    return {}


def _options():
    return ClaudeAgentOptions(
        system_prompt=SYSTEM,
        model=_client.MODEL,
        mcp_servers={"activation": _build_server()},
        allowed_tools=[
            "mcp__activation__wr_run_queries",
            "mcp__activation__wr_measure",
            "mcp__activation__wr_operate",
            "mcp__activation__send_founder_nudge",
            "mcp__activation__gtm_handoff",
        ],
        hooks={"PreToolUse": [HookMatcher(hooks=[_gate_hook])]},
        agents={
            "account-researcher": AgentDefinition(
                description="Brief one product-qualified account with web research.",
                prompt=("Brief one account in two sentences: what they build and the "
                        "one reason to reach out now, each claim cited. If nothing is "
                        "public, say 'no public signal found.'"),
                tools=["WebSearch", "WebFetch"],
                model="opus-4-8",
            ),
        },
        permission_mode="default",
        max_turns=24,
    )


async def _run_async(cohort: str, week_of: str) -> dict:
    from claude_agent_sdk import ResultMessage
    prompt = (f"Produce the weekly startup-signal report for {cohort} (week of {week_of}). "
              "Measure, operate, brief each PQA via the subagent, and propose the outward "
              "motions for approval. Send nothing.")
    text = ""
    async for message in query(prompt=prompt, options=_options()):
        if isinstance(message, ResultMessage) and getattr(message, "subtype", "") == "success":
            text = message.result
    return {"live": True, "report": text}


def run_local(*, cohort: str = "examples/cohort.json",
              week_of: str = pipeline.DEFAULT_WEEK_OF,
              dry_run: bool = False) -> dict:
    """Run the live Agent SDK orchestration, or an explicit deterministic dry run."""
    if not available():
        if not dry_run:
            raise RuntimeError(
                "the local Agent SDK orchestrator is not live: "
                f"{_missing_live_reason()}. Use --dry-run for the deterministic pipeline."
            )
        result = pipeline.run(week_of=week_of)
        return {"live": False, "report": result["report"]}
    import asyncio
    return asyncio.run(_run_async(cohort, week_of))
