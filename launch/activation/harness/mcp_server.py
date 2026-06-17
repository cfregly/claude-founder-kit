"""The capture and query surface as an MCP server: the eleven queries, measure, operate.

Step 1 and step 9 in one place: the same logical retrievals the pipeline runs
become MCP tools, so a founder can point their own Claude agent (local or managed)
at their event log and get the funnel, the readout, and the gated plan without
cloning the repo. Guarded: if the `mcp` package is absent the module still
imports, and `serve()` explains the one-line install.
"""

# No `from __future__ import annotations` here: FastMCP introspects the real
# annotation classes on the tool signatures, and stringized annotations break it.

import json
from typing import Optional

from ..capture import queries
from ..measure import metrics
from ..operate import plan as planning

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # optional dependency: the MCP server is one surface, not the core
    FastMCP = None  # type: ignore


def build_server():
    if FastMCP is None:
        raise RuntimeError("the MCP server needs the mcp package: pip install mcp")
    server = FastMCP("activation")

    @server.tool()
    def run_queries(event_log: str) -> list:
        """Run the eleven adoption queries over a JSONL event log, each with its value."""
        return queries.run_all(queries.load(event_log))

    @server.tool()
    def time_to_first_value(event_log: str) -> Optional[float]:
        """Median days from signup to first call (the aha) over a JSONL event log."""
        return queries.time_to_first_value_days(queries.load(event_log))

    @server.tool()
    def measure(cohort_json: str) -> dict:
        """Score a cohort JSON file into the activation readout (funnel, rates, PQAs)."""
        with open(cohort_json) as f:
            return metrics.summarize(json.load(f))

    @server.tool()
    def operate(readout_json: str) -> dict:
        """Turn a readout JSON file into the gated plan: did, proposed, will_not."""
        with open(readout_json) as f:
            return planning.plan(json.load(f))

    return server


def serve():
    """Run the MCP server over stdio for a local agent to connect to."""
    build_server().run()
