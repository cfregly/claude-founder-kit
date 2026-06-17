# Platform coverage

The claim is that producing one weekly report touches the whole Claude Developer
Platform and the Agent SDK. This is the prose form of that claim. `make coverage`
prints the authoritative map from `activation/platform/coverage.py`, and this file
mirrors it.

A surface is load-bearing when the report genuinely needs it, and coverage when it
is there to complete the set. The coverage-only items are the honest minority, 14
of 43, and they are named, not hidden. The deterministic stages (capture, measure,
the gate, the audit, the report template) run with no key, so the demo runs
offline. The generative stages (enrich, decide, draft) run Claude on every run and
raise with no key, so a misconfiguration is loud.

## Messages API and generation

| Surface | Where | Status |
| --- | --- | --- |
| Messages API (messages.create) | platform/client.py, decide, draft, enrich | load-bearing |
| Model selection (opus-4-8, sonnet advisor) | platform/client.py | load-bearing |
| Adaptive thinking and effort | decide/motion.py | load-bearing |
| Structured outputs (format, strict tool) | decide, draft, enrich | load-bearing |
| Prompt caching (the cohort prefix) | enrich/research.py, decide/motion.py | load-bearing |
| Token counting | platform/client.py | load-bearing |
| Batch API | enrich/research.py | load-bearing |
| Files API | draft/render.py | load-bearing |
| Citations | enrich/research.py | load-bearing |
| Streaming | harness/agent_sdk.py | coverage |
| Vision and PDF input | enrich/research.py | coverage |
| Compaction | harness/agent_sdk.py | coverage |
| Context editing | harness/agent_sdk.py | coverage |
| Mid-conversation system messages | harness/agent_sdk.py | coverage |
| Refusal handling and fallbacks | platform/client.py | coverage |

## Tools

| Surface | Where | Status |
| --- | --- | --- |
| User-defined tools and the tool runner | decide, draft | load-bearing |
| Code execution (server) | draft/render.py | load-bearing |
| Web search and web fetch | enrich/research.py | load-bearing |
| Memory tool | operate/memory.py, harness | load-bearing |
| MCP (the eleven queries) | harness/mcp_server.py | load-bearing |
| Strict tool use | decide, draft | load-bearing |
| Advisor tool (the second opinion) | decide/motion.py | coverage |
| Bash and text editor | harness/agent_sdk.py | coverage |
| Programmatic tool calling | enrich/research.py | coverage |
| Tool search | harness/agent_sdk.py | coverage |
| Computer use (read the dashboard) | harness/agent_sdk.py | coverage |

## Skills

| Surface | Where | Status |
| --- | --- | --- |
| Agent Skills (SKILL.md) | skills/activation/SKILL.md | load-bearing |
| Skills API | harness/managed_agent.py | coverage |

## Managed Agents (the cloud harness)

| Surface | Where | Status |
| --- | --- | --- |
| Agents, Sessions, Environments | harness/managed_agent.py, agents/*.yaml | load-bearing |
| Events and streaming | harness/managed_agent.py | load-bearing |
| Deployments (the cron weekly run) | harness/managed_agent.py, agents/*.yaml | load-bearing |
| Permission policies (the always_ask gate) | harness/managed_agent.py | load-bearing |
| Outcomes (the rubric grades the report) | harness/managed_agent.py | load-bearing |
| Memory stores (week-over-week) | harness/managed_agent.py | load-bearing |
| Vaults (the data credentials) | harness/managed_agent.py | load-bearing |
| Multiagent (a thread per PQA) | harness/managed_agent.py | coverage |
| Webhooks | harness/managed_agent.py | coverage |

## Agent SDK (the local harness)

| Surface | Where | Status |
| --- | --- | --- |
| Subagents (per account) | harness/agent_sdk.py | load-bearing |
| Hooks (the gate) | harness/agent_sdk.py | load-bearing |
| Permissions (the gate) | harness/agent_sdk.py | load-bearing |
| Sessions | harness/agent_sdk.py | load-bearing |
| MCP (in-process) | harness/agent_sdk.py | load-bearing |
| Skills | harness/agent_sdk.py | load-bearing |

## The honest part

The report does not need computer use, webhooks, or compaction to be correct. They
are coverage: real, working code paths that round out the platform surface, marked
as such so the load-bearing majority is not inflated by them. The test that
matters is the offline one. With no key, the deterministic spine produces the whole
report and the gate audit passes. The generative stages run against a real key and
raise without one, so the platform claim is exercised honestly: the spine proves
the receipt offline, and the model does the judgment when the key is present.
