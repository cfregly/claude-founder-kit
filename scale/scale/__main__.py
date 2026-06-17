"""The CLI: score a Scale-stage cohort into the moat readout.

    python -m scale examples/cohort.json          the human readout (runs Claude)
    python -m scale examples/cohort.json --json    the raw deterministic readout, offline
    python -m scale examples/cohort.json --min-moat 40   a CI gate on the median moat

The deterministic moat core runs offline and carries the receipt. The human
readout adds the GTM motion and the moat narrative from Claude on every run, so it
needs ANTHROPIC_API_KEY and the anthropic SDK and raises a clear error without
them. The --json output is the raw readout and never calls Claude.
"""

from __future__ import annotations

import argparse
import json
import sys

from .measure import metrics


def _print_readout(readout: dict, generated: dict) -> None:
    """The human readout: the deterministic moat core, then the Claude GTM motion
    and moat narrative. Both halves print every run."""
    print(f"cohort: {readout['cohort']} ({readout['accounts']} accounts)\n")
    print("moat (switching-cost proxy, 0..100)")
    for s in sorted(readout["scores"], key=lambda x: x["moat"], reverse=True):
        marks = []
        if s["gtm_ready"]:
            marks.append("GTM-ready")
        if s["compounding_data"]:
            marks.append("compounding data")
        tail = ("  [" + ", ".join(marks) + "]") if marks else ""
        print(f"  {(s['name'] + ' ').ljust(20, '.')} {s['moat']:>3}  "
              f"({s['band']}: integration {s['integration_depth']}, "
              f"workflow {s['workflow_lockin']}, usage {s['usage_depth']}){tail}")
    dist = readout["moat_distribution"]
    print()
    print(f"  distribution ........... deep {dist['deep']}, "
          f"forming {dist['forming']}, shallow {dist['shallow']}")
    print(f"  median moat ............ {readout['median_moat']}")
    ready = readout["gtm_ready_accounts"]
    print(f"  expansion-ready ........ {', '.join(ready) if ready else 'none'}  "
          f"(the one number: {readout['the_number']['value']})")
    comp = readout["compounding_data_accounts"]
    print(f"  compounding data ....... {', '.join(comp) if comp else 'none'}")
    print("\nflags")
    for f in readout["flags"]:
        print(f"  - {f}")

    print("\nGTM motion")
    motion = generated.get("gtm_motion", {})
    targets = motion.get("target_accounts", [])
    print(f"  target ................. {', '.join(targets) if targets else 'none'}")
    print(f"  play ................... {motion.get('play', '')}")
    print(f"  why .................... {motion.get('rationale', '')}")
    print("\nmoat narrative")
    print(f"  {generated.get('moat_narrative', '')}")


def cmd_score(args) -> int:
    with open(args.cohort) as f:
        coh = json.load(f)
    readout = metrics.summarize(coh)

    if args.min_moat is not None and readout["median_moat"] < args.min_moat:
        # The CI gate runs on the deterministic readout, before any Claude call, so
        # it fails offline with no key. Print whichever view was asked for first.
        if args.json:
            print(json.dumps(readout, indent=2))
        print(f"\nFAIL: median moat {readout['median_moat']} below the "
              f"{args.min_moat} bar.", file=sys.stderr)
        return 1

    if args.json:
        # The raw deterministic readout. Never calls Claude, so it runs offline.
        print(json.dumps(readout, indent=2))
        return 0

    # The human readout runs Claude every run for the GTM motion and the narrative.
    from .generate import gtm
    generated = gtm.gtm_and_moat(readout)
    _print_readout(readout, generated)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scale",
        description="Score a Scale-stage cohort into a moat readout and the GTM motion.")
    p.add_argument("cohort", help="the cohort JSON of accounts with Scale-stage signals")
    p.add_argument("--json", action="store_true",
                   help="the raw deterministic readout, offline, no Claude")
    p.add_argument("--min-moat", type=float, default=None,
                   help="fail below this median moat (a CI gate, runs offline)")
    p.set_defaults(func=cmd_score)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as e:
        # The generative stage runs Claude and raises without a key or SDK. Surface
        # the reason cleanly, not as a traceback.
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
