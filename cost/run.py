#!/usr/bin/env python3
"""One-command entry for the cost-lever demos. Online only.

    ANTHROPIC_API_KEY=... python run.py                  # every lever, real call
    ANTHROPIC_API_KEY=... python run.py prompt_caching   # one lever, real call

Requires ANTHROPIC_API_KEY. Every run calls the real Anthropic API. Without a key it fails fast
with a clear error and a non-zero exit. After a run it writes a receipt to data/last_run.md.
"""

import sys
from pathlib import Path

from cost_control.client import get_client, require_key
from cost_control.demos import REGISTRY

RECEIPT = Path(__file__).resolve().parent / "data" / "last_run.md"


def _names(argv):
    return [a for a in argv if not a.startswith("-")]


def _write_receipt(selected):
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# last run", "", f"levers: {len(selected)}", ""] + [f"- {n}" for n in selected]
    RECEIPT.write_text("\n".join(lines) + "\n")


def main(argv):
    try:
        require_key()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    names = _names(argv)
    unknown = [n for n in names if n not in REGISTRY]
    if unknown:
        print("unknown lever(s): " + ", ".join(unknown))
        print("available: " + ", ".join(REGISTRY))
        return 2
    selected = names or list(REGISTRY)

    client = get_client()
    for name in selected:
        summary, fn = REGISTRY[name]
        print(f"\n=== {name}  ({summary}) ===")
        print(fn(client))

    _write_receipt(selected)
    print(f"\nran {len(selected)} lever(s) live. receipt: data/last_run.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
