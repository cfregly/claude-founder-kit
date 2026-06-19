"""Claude judge: rewrite the worst tool contract, then re-lint it.

Deterministic rules find the violations and own the score. Claude writes the fix
the rules can name but not write. The loop closes when the same rules re-score
the rewrite, the eval-before-vibes discipline you would apply to any agent
change. The rules never move because Claude ran.

The rewrite is on by default and runs whenever a key is set. With no key it is a
no-op the caller skips, so the deterministic score is identical and CI stays
green offline.

Best practice: this is a single structured rewrite of one tool, so it uses the
Messages API, not the Agent SDK. The rewrite comes back through a forced tool
call (tool_choice), so the result is a reliable tool object on every SDK
version, not JSON parsed out of free text.

Requires ANTHROPIC_API_KEY and `pip install anthropic`.
"""

from __future__ import annotations

import json
import os

try:
    from anthropic import Anthropic
except Exception:  # optional dependency: the linter is stdlib-only without it
    Anthropic = None  # type: ignore

try:  # honor the .env setup path without making dotenv a hard dependency
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

MODEL = "claude-opus-4-8"

SYSTEM = """You rewrite MCP tool definitions into contract-grade interfaces.
You receive one tool's JSON definition and the linter findings against it. Call
the rewritten_tool tool with the rewrite. Keep the tool's purpose identical. Fix
every finding: a precise 2-4 sentence description with exact semantics,
documented failure modes, declared side effects and idempotency for mutations, a
description for every parameter, enums or formats or patterns for shaped strings,
and a 'required' array. Rename the tool only if the linter flagged the name as
generic. Write the contract plain: no marketing adjectives ('powerful',
'seamless', 'robust'), no filler, no em-dashes. Every sentence states semantics
the caller can act on. An adjective that carries no behavior gets cut.

Each finding carries a 'fix_kind'. Apply 'auto' findings mechanically: delete the
flagged words and reclaim the tokens for behavior. Treat 'ask' findings as the
work: write the real semantics, rename, or declare the shape they call for.

Example. Given {"name": "search", "description": "Search stuff.", "inputSchema":
{"type": "object", "properties": {"q": {"type": "string"}}}} with findings that
the name is generic, the description is one line, and the parameter is
undocumented, return {"name": "search_invoices", "description": "Search invoices
by text and return up to 20 matches, newest first. Returns an empty list when
nothing matches, never an error. Read-only.", "inputSchema": {"type": "object",
"properties": {"query": {"type": "string", "description": "the text to match in
invoice fields"}, "limit": {"type": "integer", "description": "maximum results, 1
to 100, default 20"}}, "required": ["query"], "additionalProperties": false}}."""

# Forced tool_choice returns the rewrite as a reliable tool object, not JSON
# parsed out of prose. inputSchema is the tool's own JSON Schema, so it stays a
# free-form object.
_TOOL = {
    "name": "rewritten_tool",
    "description": "Return the rewritten, contract-grade tool definition.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string",
                     "description": "the tool name, renamed only if flagged as generic"},
            "description": {"type": "string",
                            "description": "the contract-grade description with semantics and failure modes"},
            "inputSchema": {"type": "object",
                            "description": "the tool's JSON Schema: described properties, a required array, enums and formats"},
        },
        "required": ["name", "description", "inputSchema"],
        "additionalProperties": False,
    },
}


def available() -> bool:
    """True when a live rewrite is possible: the SDK imports and a key is set."""
    return Anthropic is not None and bool(os.getenv("ANTHROPIC_API_KEY"))


def rewrite_tool(tool: dict, findings: list[dict]) -> dict:
    """Rewrite one tool into a contract-grade definition with Claude.

    Returns the rewritten {name, description, inputSchema} so the caller re-lints
    it. No temperature is set: it is removed on claude-opus-4-8 and sending it
    returns a 400. The caller checks available() first, so this runs only with a
    key and an installed SDK.
    """
    client = Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM,
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "rewritten_tool"},
        messages=[{
            "role": "user",
            "content": (
                "Tool definition:\n```json\n"
                + json.dumps(tool, indent=2)
                + "\n```\n\nLinter findings:\n```json\n"
                + json.dumps(findings, indent=2)
                + "\n```"
            ),
        }],
    )
    block = next(b for b in msg.content if getattr(b, "type", None) == "tool_use")
    return dict(block.input)
