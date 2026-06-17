"""CLI: lint a pitch-deck spec.

    python -m pitch_lint <deck.json> [--json] [--min-score N] [--no-judge]

The pitch_lint score is the deterministic gate. Exit 1 if the deck scores below
--min-score (default 80). Wire it into CI: a deck that stops fighting for its
words stops shipping. The score is stdlib-only and runs the same with or without
a key, so CI stays reproducible.

claude-opus-4-8 reviews every interactive run: it reads the arc the rules cannot
score and prints below the score. The gate (check_docs, CI, --min-score) stays
deterministic and never calls the API: when stdout is piped to a subprocess the
read does not fire by default. The read is advisory and never changes the score
or the exit code. --judge forces it on regardless of the TTY, --no-judge turns it
off even when a key is present.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .rules import lint_deck

SEV_MARK = {"error": "✗", "warn": "!", "info": "·"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pitch_lint", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="deck spec JSON")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--min-score", type=int, default=80)
    ap.add_argument("--no-judge", action="store_true",
                    help="skip the Claude narrative read even when a key is set. "
                         "The read reviews every interactive run with "
                         "ANTHROPIC_API_KEY and `pip install anthropic`, advisory only")
    ap.add_argument("--judge", action="store_true",
                    help=argparse.SUPPRESS)  # force on regardless of the TTY; reviews every interactive run by default
    args = ap.parse_args(argv)

    deck = json.loads(Path(args.spec).read_text())
    report = lint_deck(deck)

    # The Claude narrative read reviews every interactive run (a key is set and
    # stdout is a TTY). It is advisory: it never changes the score or the exit
    # code below, so the deterministic gate stays reproducible. When stdout is
    # piped to a subprocess (check_docs, CI, `make check`), it does not fire by
    # default, so the gate never calls the API. --judge forces it on regardless
    # of the TTY, --no-judge turns it off even when a key is present.
    from .judge import available, judge_deck
    narrative = None
    run_judge = (not args.no_judge) and (args.judge or (available() and sys.stdout.isatty()))
    if run_judge:
        narrative = judge_deck(deck)

    if args.as_json:
        if narrative is not None:
            report["narrative"] = narrative
        print(json.dumps(report, indent=2))
    else:
        name = deck.get("company", args.spec)
        print(f"pitch_lint - {name}: {report['score']}/100 (grade {report['grade']})\n")
        # Lead with how it reads to an investor: the four dimensions a founder is
        # judged on, not the format nitpicks. Strategic gaps come first.
        dim_mark = {"solid": "✓", "soft": "!", "gap": "✗"}
        print("How it reads to an investor:")
        for dim, d in report["dimensions"].items():
            tail = "" if d["status"] == "solid" else f"  ({d['errors']} gap, {d['warns']} soft)"
            print(f"  [{dim_mark[d['status']]}] {d['label']:42s} {d['status']}{tail}")
        from .rules import DIMENSION, DIMENSION_LABEL
        if report["findings"]:
            print("\nWhat to fix, grouped:")
            for dim in ("questions", "story", "diligence", "ask"):
                fs = [f for f in report["findings"] if DIMENSION.get(f["rule"]) == dim]
                if not fs:
                    continue
                print(f"\n  {DIMENSION_LABEL[dim]}")
                for f in fs:
                    print(f"    [{f['rule']} {SEV_MARK[f['severity']]}] {f['slide']}: {f['message']}")
                    print(f"        fix: {f['fix']}")
        else:
            print("\nclean - every word fought and won")

        if narrative is not None:
            from .judge import render
            print(render(narrative))

    if report["score"] < args.min_score:
        print(f"\nFAIL: {report['score']} < --min-score {args.min_score}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
