"""Claude Agent SDK example: repo reviewer for founder demos.

Run this after installing the Claude Agent SDK and setting ANTHROPIC_API_KEY.
It asks Claude to inspect the current repository and produce a founder-ready launch plan.
"""

from __future__ import annotations

import asyncio

try:
    from claude_agent_sdk import ClaudeAgentOptions, query
except Exception as exc:  # pragma: no cover
    raise SystemExit("Install claude-agent-sdk first: pip install claude-agent-sdk") from exc


PROMPT = """
You are reviewing this repository the way a founder-facing engineer would, to get
it ready to demo to technical founders. Inspect the files before you claim
anything about the repo, and do not edit a file unless the change is low-risk and
clearly correct. Prefer a concise written report.

Return, with each finding as problem, then why it matters, then the fix:
1. The 15-minute demo flow.
2. The strongest Claude-specific proof points.
3. Three improvements to make it more production credible.
4. A README patch, only if a clear one is warranted.

Write plain prose: no em-dashes, no buzzwords.
""".strip()


async def main() -> None:
    options = ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob", "Edit", "Bash"])
    async for message in query(prompt=PROMPT, options=options):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
