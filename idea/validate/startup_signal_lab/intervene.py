"""python -m startup_signal_lab.intervene <pitch.md> - the live founder intervention.

Runs Claude every time. Needs ANTHROPIC_API_KEY. The deterministic signal score is in
score.py and is the gate; this is the online judgment layer that writes the intervention.
"""
from __future__ import annotations

import pathlib
import sys

from startup_signal_lab.anthropic_client import analyze_pitch_with_claude


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: python -m startup_signal_lab.intervene <pitch.md>", file=sys.stderr)
        return 0 if argv else 2
    pitch = pathlib.Path(argv[0]).read_text(encoding="utf-8")
    result = analyze_pitch_with_claude(pitch)
    print(result["response"])
    usage = result.get("usage", {})
    print(f"\n[live: {result['route']['model']}, "
          f"{usage.get('input_tokens', '?')} in / {usage.get('output_tokens', '?')} out]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
