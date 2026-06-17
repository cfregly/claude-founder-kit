"""CLI: lint an MCP server's tool contracts.

    python -m contract_doctor <tools.json | fastmcp_server.py> [options]

The deterministic rule score is the gate: it runs offline, with no key, and is
what CI checks. Claude (claude-opus-4-8) reviews every interactive run and
rewrites the worst-scoring tool, then the same rules re-score the rewrite. The
gate (check_docs, CI, --min-score) stays deterministic and never calls the API:
when stdout is piped to a subprocess the rewrite does not fire by default.

Options:
    --json           emit the full report as JSON instead of the table
    --min-score N    exit 1 if any tool scores below N (default 70), the CI gate
    --judge          force the Claude rewrite of the worst tool on regardless of
                     the TTY, and report a skip when no key is set
    --no-judge       skip the Claude rewrite even when a key is set, for a purely
                     deterministic run
"""

from __future__ import annotations

import argparse
import json
import sys

from .loaders import load_tools
from .report import render
from .rules import grade, lint_server, lint_tool, score_tool


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="contract_doctor", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source", nargs="?", help="tools JSON file or FastMCP server .py")
    parser.add_argument("--protocol", help="lint an agent protocol doc (AGENTS.md / "
                        "SKILL.md style) for always / ask-first / never boundaries and "
                        "a failure plan, instead of tools")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--min-score", type=int, default=70)
    parser.add_argument("--judge", action="store_true",
                        help="force the Claude rewrite on regardless of the TTY and report a "
                        "skip with no key (it reviews every interactive run by default)")
    parser.add_argument("--no-judge", action="store_true",
                        help="skip the Claude rewrite even with a key set")
    args = parser.parse_args(argv)

    if args.protocol:
        from pathlib import Path
        from .protocol import lint_agent_protocol
        rep = lint_agent_protocol(Path(args.protocol).read_text())
        if args.as_json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"agent-protocol {args.protocol}: {rep['score']}/100 (grade {rep['grade']})")
            for fnd in rep["findings"]:
                print(f"  [{fnd['rule']} {fnd['severity']}] {fnd['message']}\n      fix: {fnd['fix']}")
        return 0 if rep["score"] >= args.min_score else 1

    if not args.source:
        parser.error("provide a tools source, or --protocol PATH")
    tools = load_tools(args.source)
    report = lint_server(tools)

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report, args.source))

    # The rewrite runs by default only on a direct interactive run, detected by
    # stdout.isatty(). When stdout is piped to a subprocess (check_docs, CI,
    # `make check`), it does not fire, so the gate never calls the API and the
    # score output stays byte-for-byte stable. --judge forces it on regardless of
    # the TTY, --no-judge forces the deterministic-only path. The skip line prints
    # only when --judge asked for the rewrite but no key is set.
    from .judge import available, rewrite_tool
    run_judge = (not args.no_judge) and (args.judge or (available() and sys.stdout.isatty()))
    if run_judge:
        if not available():
            print("\n--- judge: skipped. Set ANTHROPIC_API_KEY and "
                  "`pip install anthropic` to have Claude rewrite the worst tool "
                  "and re-lint it. ---")
        else:
            worst_name = min(report["tools"], key=lambda n: report["tools"][n]["score"])
            worst = next(t for t in tools if t.get("name") == worst_name)
            worst_report = report["tools"][worst_name]
            print(f"\n--- judge: rewriting '{worst_name}' "
                  f"(score {worst_report['score']}) with Claude ---")
            fixed = rewrite_tool(worst, worst_report["findings"])
            fixed_findings = lint_tool(fixed)
            fixed_score = score_tool(fixed_findings)
            print(json.dumps(fixed, indent=2))
            print(f"\nre-lint: {worst_report['score']} ({worst_report['grade']}) "
                  f"-> {fixed_score} ({grade(fixed_score)})")
            if fixed_findings:
                for f in fixed_findings:
                    print(f"  remaining [{f['rule']} {f['severity']}]: {f['message']}")

    failing = [
        name for name, t in report["tools"].items() if t["score"] < args.min_score
    ]
    if failing:
        print(
            f"\nFAIL: {len(failing)} tool(s) below --min-score {args.min_score}: "
            + ", ".join(sorted(failing)),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
