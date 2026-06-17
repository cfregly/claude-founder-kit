"""The platform coverage map: which surface each step exercises, and where.

The repo's claim is that producing one weekly report touches the whole Claude
Developer Platform and the Agent SDK. This is the verifiable form of that claim:
every surface, the file that exercises it, and an honest label of whether the
report genuinely needs it (load-bearing) or it is there to complete the set
(coverage). `make coverage` prints it; PLATFORM_COVERAGE.md mirrors it in prose.
"""

from __future__ import annotations

LOAD = "load-bearing"
COVER = "coverage"

# (surface, where it lives, the pipeline step, status)
COVERAGE = {
    "Messages API & generation": [
        ("Messages API (messages.create)", "platform/client.py + decide/draft/enrich", "all model calls", LOAD),
        ("Model selection (opus-4-8 / sonnet advisor)", "platform/client.py", "decide", LOAD),
        ("Adaptive thinking + effort", "decide/motion.py", "decide", LOAD),
        ("Structured outputs (output_config.format / strict tool)", "decide, draft, enrich", "decide / draft", LOAD),
        ("Prompt caching (cohort prefix)", "enrich/research.py, decide/motion.py", "enrich / decide", LOAD),
        ("Token counting (count_tokens)", "platform/client.py", "cost receipt", LOAD),
        ("Batch API (messages.batches)", "enrich/research.py", "enrich (many PQAs at 50%)", LOAD),
        ("Files API (upload / download)", "draft/render.py", "render", LOAD),
        ("Citations", "enrich/research.py", "enrich", LOAD),
        ("Streaming", "harness/agent_sdk.py", "orchestrate", COVER),
        ("Vision / PDF input", "enrich/research.py", "ingest a founder deck", COVER),
        ("Compaction", "harness/agent_sdk.py", "long weekly run", COVER),
        ("Context editing", "harness/agent_sdk.py", "long weekly run", COVER),
        ("Mid-conversation system messages", "harness/agent_sdk.py", "auto-approve toggle", COVER),
        ("Refusal handling / fallbacks", "platform/client.py", "Fable path", COVER),
    ],
    "Tools": [
        ("User-defined tools / tool runner", "decide, draft", "decide / draft", LOAD),
        ("Code execution (server)", "draft/render.py", "render the PDF", LOAD),
        ("Web search + web fetch", "enrich/research.py", "enrich", LOAD),
        ("Memory tool", "operate/memory.py + harness", "remember", LOAD),
        ("MCP (the 11 queries)", "harness/mcp_server.py", "capture / package", LOAD),
        ("Strict tool use", "decide, draft", "decide / draft", LOAD),
        ("Advisor tool (second opinion)", "decide/motion.py", "decide", COVER),
        ("Bash / text editor", "harness/agent_sdk.py", "orchestrate", COVER),
        ("Programmatic tool calling", "enrich/research.py", "compose the queries", COVER),
        ("Tool search", "harness/agent_sdk.py", "orchestrate", COVER),
        ("Computer use", "harness/agent_sdk.py", "read the live dashboard", COVER),
    ],
    "Skills": [
        ("Agent Skills (SKILL.md)", "skills/activation/SKILL.md", "package", LOAD),
        ("Skills API", "harness/managed_agent.py", "publish the skill", COVER),
    ],
    "Managed Agents (cloud harness)": [
        ("Agents / Sessions / Environments", "harness/managed_agent.py + agents/*.yaml", "schedule", LOAD),
        ("Events / streaming (SSE)", "harness/managed_agent.py", "schedule", LOAD),
        ("Deployments (cron, the weekly run)", "harness/managed_agent.py + agents/*.yaml", "schedule", LOAD),
        ("Permission policies (always_ask gate)", "harness/managed_agent.py", "gate", LOAD),
        ("Outcomes (rubric grades the report)", "harness/managed_agent.py", "decide / grade", LOAD),
        ("Memory stores (week-over-week)", "harness/managed_agent.py", "remember", LOAD),
        ("Vaults (PostHog / Stripe creds)", "harness/managed_agent.py", "capture", LOAD),
        ("Multiagent (a thread per PQA)", "harness/managed_agent.py", "enrich", COVER),
        ("Webhooks (PQA crossed threshold)", "harness/managed_agent.py", "schedule", COVER),
    ],
    "Agent SDK (local harness)": [
        ("Subagents (per PQA, per section)", "harness/agent_sdk.py", "orchestrate", LOAD),
        ("Hooks (the gate)", "harness/agent_sdk.py", "gate", LOAD),
        ("Permissions (the gate)", "harness/agent_sdk.py", "gate", LOAD),
        ("Sessions", "harness/agent_sdk.py", "orchestrate", LOAD),
        ("MCP (in-process)", "harness/agent_sdk.py", "capture", LOAD),
        ("Skills", "harness/agent_sdk.py", "package", LOAD),
    ],
}


def counts():
    load = cover = 0
    for entries in COVERAGE.values():
        for *_, status in entries:
            if status == LOAD:
                load += 1
            else:
                cover += 1
    return load, cover


def render() -> str:
    L = ["Platform coverage: where one weekly report touches the platform", ""]
    for group, entries in COVERAGE.items():
        L.append(group)
        for surface, where, step, status in entries:
            tag = "*" if status == LOAD else " "
            L.append(f"  {tag} {(surface + ' ').ljust(46, '.')} {where}")
        L.append("")
    load, cover = counts()
    L.append(f"{load} load-bearing (*), {cover} coverage, {load + cover} surfaces total.")
    L.append("Load-bearing means the report genuinely needs it. Coverage means it is")
    L.append("there to complete the set, the honest minority. The deterministic stages")
    L.append("run with no key, so make demo runs offline. The generative stages run")
    L.append("Claude every run and raise with no key, so a misconfiguration is loud.")
    return "\n".join(L) + "\n"
