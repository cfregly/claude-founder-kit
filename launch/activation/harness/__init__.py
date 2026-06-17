"""Step 10, orchestrate: the two harnesses and the MCP surface.

The same pipeline runs two ways. `agent_sdk` is the local Claude Agent SDK
orchestrator: it runs offline-deterministically and, with the SDK and a key, as a
real agent with subagents per account, hooks that gate the outward tools, and the
queries as in-process MCP tools. `managed_agent` is the cloud path: a Managed
Agents scheduled deployment that fires the weekly run on a cron, with the gate as
a permission policy. `mcp_server` exposes the eleven queries plus measure and
operate as MCP tools a founder can point their own agent at.
"""
