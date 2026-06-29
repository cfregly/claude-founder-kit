# MCP And Agent Pointer

The pilot-check stage stays keyless. Use these existing live paths when you are ready to connect the trust
controls to real Claude calls.

| Job | Existing path |
| --- | --- |
| First tool round trip | `first_hour/tour/step3_tool.py` |
| Manual agent loop | `first_hour/tour/step4_agent_loop.py` |
| MVP tool use | `mvp/build/02_agent_with_tools.py` |
| Eval gate | `mvp/build/03_evals.py` |
| MCP server | `mvp/build/mcp_server/startup_metrics_server.py` |
| Agent SDK harness | `launch/activation/harness/agent_sdk.py` |
| Managed Agents shape | `launch/activation/harness/managed_agent.py` |

Before moving a live path beyond demo traffic, attach the pilot-check evals, permissions, logs,
monitoring, rollback, and stopping conditions to the workflow.
