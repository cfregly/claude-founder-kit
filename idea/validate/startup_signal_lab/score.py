"""Headless scorer: `python -m startup_signal_lab.score <pitch.md> ...`

Prints the overall startup-signal score (1-10) for each pitch file. The README
documents its marquee score with this command, and the score-drift gate
(scripts/check_docs.py) re-runs it and fails if the printed number ever diverges
from the one the README advertises, so the headline score cannot go stale.
"""
from __future__ import annotations

import pathlib
import sys

from startup_signal_lab.scoring_tools import score_startup_signal


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: python -m startup_signal_lab.score <pitch.md> [<pitch.md> ...]",
              file=sys.stderr)
        return 0 if argv else 2
    for arg in argv:
        path = pathlib.Path(arg)
        score = score_startup_signal(path.read_text(encoding="utf-8"))
        print(f"startup-signal - {path.stem}: {score.overall}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
