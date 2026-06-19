"""The unified CLI: one entry point for every step of the weekly report.

    python -m activation demo                 the whole pipeline, live -> the report
    python -m activation capture              emit the sample cohort to a backend
    python -m activation measure cohort.json  the activation readout
    python -m activation operate readout.json the gated plan and report
    python -m activation gen-examples         regenerate the committed samples

The platform and harness layers add more subcommands (enrich, decide, draft,
deploy, coverage); they live in later modules and need a key for the live path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:  # honor launch/.env before CLI fail-fast checks
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:  # pragma: no cover - dotenv is a setup helper
    pass

from . import pipeline
from .capture import queries, simulate
from .measure import metrics
from .operate import memory, plan as planning, report as reporting

PREV_STATE = "examples/prev_week_state.json"


def _print_readout(readout: dict) -> None:
    print(f"cohort: {readout['cohort']} ({readout['accounts']} accounts)\n")
    print("funnel")
    for s in readout["funnel"]:
        print(f"  {(s['label'] + ' ').ljust(28, '.')} {s['count']:>3}  "
              f"({s['pct_of_top'] * 100:.0f}% of top, conv {s['conv_from_prev']:.2f})")
    print()
    print(f"  activation rate ......... {readout['activation_rate'] * 100:.0f}%")
    print(f"  retention (2nd build) ... {readout['retention_rate'] * 100:.0f}%")
    print(f"  engagement retention .... {readout['engagement_retention'] * 100:.0f}%")
    ttsb = readout["time_to_second_build_days"]
    print(f"  time-to-second-build .... {ttsb if ttsb is not None else 'n/a'} days")
    ready = readout["pqas_ready_for_handoff"]
    print(f"  PQAs ready .............. {', '.join(ready) if ready else 'none'}")
    print("\nflags")
    for f in readout["flags"]:
        print(f"  - {f}")


def cmd_demo(args) -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. The launch demo runs the live pipeline "
              "(enrich, decide, draft, render) and has no offline mode.", file=sys.stderr)
        return 1
    prev = memory.load_prev_state(PREV_STATE)
    result = pipeline.run(seed=args.seed, prev_state=prev, week_of=args.week_of, live=True)
    sys.stdout.write(result["report"])
    r = result.get("rendered")
    where = f"{r['format']}: {r['path']}" if r else "skipped"
    print(f"\n[live: ran Claude for enrich, decide, draft; render {where}]", file=sys.stderr)
    return 0


def cmd_coverage(args) -> int:
    from .platform import coverage
    sys.stdout.write(coverage.render())
    return 0


def cmd_enrich(args) -> int:
    from .enrich import research
    with open(args.readout) as f:
        readout = json.load(f)
    out = research.enrich_pqas(readout.get("pqas_ready_for_handoff", []),
                               cohort_name=readout.get("cohort", ""), use_batch=args.batch)
    print(json.dumps(out, indent=2))
    return 0


def cmd_decide(args) -> int:
    from .decide import motion as deciding
    with open(args.readout) as f:
        readout = json.load(f)
    print(json.dumps(deciding.decide_motion(readout, planning.plan(readout)), indent=2))
    return 0


def cmd_draft(args) -> int:
    from .draft import nudges
    with open(args.readout) as f:
        readout = json.load(f)
    p = planning.plan(readout)
    print(json.dumps(nudges.draft_nudges(p), indent=2))
    return 0


def cmd_capture(args) -> int:
    if args.no_telemetry:
        os.environ["ACTIVATION_TELEMETRY"] = "off"
    if args.backend:
        os.environ["ACTIVATION_BACKEND"] = args.backend
    os.environ["ACTIVATION_EVENT_LOG"] = args.log
    open(args.log, "w").close()
    simulate.run(args.seed)
    if args.no_telemetry:
        print("telemetry off: nothing captured.")
        return 0
    rows = queries.load(args.log)
    orgs = {r["org_id"] for r in rows}
    print(f"captured {len(rows)} events from {len(orgs)} orgs to {args.log} "
          f"(backend {os.environ.get('ACTIVATION_BACKEND', 'local')})")
    return 0


def cmd_measure(args) -> int:
    with open(args.cohort) as f:
        coh = json.load(f)
    readout = metrics.summarize(coh)
    if args.json:
        print(json.dumps(readout, indent=2))
    else:
        _print_readout(readout)
    if args.min_activation is not None and readout["activation_rate"] < args.min_activation:
        print(f"\nFAIL: activation {readout['activation_rate'] * 100:.0f}% below "
              f"the {args.min_activation * 100:.0f}% bar.", file=sys.stderr)
        return 1
    return 0


def cmd_operate(args) -> int:
    with open(args.readout) as f:
        readout = json.load(f)
    p = planning.plan(readout)
    if args.audit_gates:
        violations = audit_or_print(p)
        return 1 if violations else 0
    if args.json:
        print(json.dumps(p, indent=2))
        return 0
    if args.weekly:
        prev = memory.load_prev_state(args.prev) if args.prev else None
        sys.stdout.write(reporting.weekly_report(readout, p, prev_state=prev, week_of=args.week_of))
    else:
        sys.stdout.write(planning.morning_report(p))
    return 0


def audit_or_print(p: dict) -> list[str]:
    violations = planning.audit(p)
    if violations:
        print("GATE AUDIT FAILED:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
    else:
        print("gate audit passed: nothing outward-facing ran unattended.")
    return violations


def cmd_gen_examples(args) -> int:
    paths = pipeline.generate_examples(args.dir)
    print("wrote " + ", ".join(paths.values()))
    return 0


def cmd_deploy(args) -> int:
    from .harness import managed_agent
    if args.apply:
        print(json.dumps(managed_agent.apply(), indent=2))
    else:
        sys.stdout.write(managed_agent.render_plan())
    return 0


def cmd_agent(args) -> int:
    from .harness import agent_sdk
    result = agent_sdk.run_local(cohort=args.cohort, week_of=args.week_of)
    sys.stdout.write(result["report"])
    if not result["live"]:
        print("\n[agent sdk not active: ran the deterministic pipeline. Install "
              "claude-agent-sdk and set ANTHROPIC_API_KEY for the live agent.]", file=sys.stderr)
    return 0


def cmd_mcp(args) -> int:
    from .harness import mcp_server
    try:
        mcp_server.serve()
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="activation", description="Produce the founder-to-builder weekly report.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="the whole pipeline, offline, then the weekly report")
    d.add_argument("--seed", type=int, default=7)
    d.add_argument("--week-of", default=pipeline.DEFAULT_WEEK_OF)
    d.add_argument("--live", action="store_true",
                   help="layer enrich/decide/draft/render when a key is present")
    d.set_defaults(func=cmd_demo)

    r = sub.add_parser("report", help="alias for demo")
    r.add_argument("--seed", type=int, default=7)
    r.add_argument("--week-of", default=pipeline.DEFAULT_WEEK_OF)
    r.add_argument("--live", action="store_true")
    r.set_defaults(func=cmd_demo)

    c = sub.add_parser("capture", help="emit the sample cohort to a backend")
    c.add_argument("--seed", type=int, default=7)
    c.add_argument("--backend", choices=["local", "posthog", "statsig", "amplitude"])
    c.add_argument("--log", default="events.jsonl")
    c.add_argument("--no-telemetry", action="store_true")
    c.set_defaults(func=cmd_capture)

    m = sub.add_parser("measure", help="score a cohort into the activation readout")
    m.add_argument("cohort")
    m.add_argument("--json", action="store_true")
    m.add_argument("--min-activation", type=float, default=None,
                   help="fail below this activation rate (a CI gate)")
    m.set_defaults(func=cmd_measure)

    o = sub.add_parser("operate", help="turn a readout into the gated plan and report")
    o.add_argument("readout")
    o.add_argument("--json", action="store_true")
    o.add_argument("--weekly", action="store_true", help="the weekly report (default is the morning report)")
    o.add_argument("--prev", default=None, help="last week's state file, for deltas")
    o.add_argument("--week-of", default=pipeline.DEFAULT_WEEK_OF)
    o.add_argument("--audit-gates", action="store_true", help="fail if anything outward-facing ran unattended")
    o.set_defaults(func=cmd_operate)

    g = sub.add_parser("gen-examples", help="regenerate the committed sample inputs")
    g.add_argument("--dir", default="examples")
    g.set_defaults(func=cmd_gen_examples)

    cov = sub.add_parser("coverage", help="print the platform-surface coverage map")
    cov.set_defaults(func=cmd_coverage)

    en = sub.add_parser("enrich", help="research the PQAs (web search + fetch, cited)")
    en.add_argument("readout")
    en.add_argument("--batch", action="store_true", help="fan out through the Batch API")
    en.set_defaults(func=cmd_enrich)

    de = sub.add_parser("decide", help="decide the one motion (thinking + effort + advisor)")
    de.add_argument("readout")
    de.set_defaults(func=cmd_decide)

    dr = sub.add_parser("draft", help="draft the founder message per proposed action")
    dr.add_argument("readout")
    dr.set_defaults(func=cmd_draft)

    dep = sub.add_parser("deploy", help="the Managed Agents weekly deployment (dry run by default)")
    dep.add_argument("--apply", action="store_true", help="create the agent, environment, and deployment")
    dep.add_argument("--dry-run", action="store_true", help="print the plan without creating (default)")
    dep.set_defaults(func=cmd_deploy)

    ag = sub.add_parser("agent", help="run the local Agent SDK orchestrator (falls back to the pipeline)")
    ag.add_argument("--cohort", default="examples/cohort.json")
    ag.add_argument("--week-of", default=pipeline.DEFAULT_WEEK_OF)
    ag.set_defaults(func=cmd_agent)

    mc = sub.add_parser("mcp", help="serve the eleven queries + measure + operate as an MCP server")
    mc.set_defaults(func=cmd_mcp)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as e:
        # The generative steps (enrich, decide, draft) and the live demo run Claude
        # and raise without a key or SDK. Surface the reason cleanly, not as a trace.
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
