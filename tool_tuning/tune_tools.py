#!/usr/bin/env python3
"""Render the pinned companion harness workflow without vendoring it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
PIN_PATH = ROOT / "receipt_pin.json"
REQUIRED = {
    "companion_repo",
    "pinned_commit",
    "receipt_path",
    "receipt_url",
    "founder_kit_receipt",
    "checked_on",
    "commands",
}


def load_pin(path: Path = PIN_PATH) -> dict:
    pin = json.loads(path.read_text(encoding="utf-8"))
    validate_pin(pin)
    return pin


def validate_pin(pin: dict) -> None:
    missing = sorted(REQUIRED - set(pin))
    if missing:
        raise ValueError(f"receipt pin is missing fields: {', '.join(missing)}")
    commit = pin["pinned_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("pinned_commit must be a 40 character lowercase git SHA")
    if commit not in pin["receipt_url"]:
        raise ValueError("receipt_url must include pinned_commit")
    if pin["receipt_path"] not in pin["receipt_url"]:
        raise ValueError("receipt_url must include receipt_path")
    receipt = REPO_ROOT / pin["founder_kit_receipt"]
    if not receipt.is_file():
        raise ValueError(f"founder_kit_receipt does not exist: {receipt}")
    commands = pin["commands"]
    if not isinstance(commands, list) or not commands:
        raise ValueError("commands must be a non-empty list")
    required_commands = ("optimize-tools", "model-matrix", "grind-harness")
    joined = "\n".join(commands)
    for token in required_commands:
        if token not in joined:
            raise ValueError(f"commands must include {token}")


def render(pin: dict) -> str:
    lines = [
        "# Tune your tools",
        "",
        "This founder-kit recipe does not copy harness code.",
        "It points to the pinned companion workbench for tool contract tuning.",
        "",
        f"Repo: {pin['companion_repo']}",
        f"Commit: {pin['pinned_commit']}",
        f"Confirmed-improvements ledger: {pin['receipt_url']}",
        f"Founder-kit receipt: {pin['founder_kit_receipt']}",
        "",
        "Run the pinned companion workflow:",
        "",
    ]
    lines.extend(f"  {command}" for command in pin["commands"])
    lines.extend(
        [
            "",
            "Use optimize-tools for a first contract pass.",
            "Use model-matrix when tool choice depends on model or harness.",
            "Use grind-harness only after you have live eval cases and held-out checks.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the pinned tool tuning recipe.")
    parser.add_argument("--json", action="store_true", help="print the pin as JSON")
    args = parser.parse_args()
    pin = load_pin()
    if args.json:
        print(json.dumps(pin, indent=2, sort_keys=True))
    else:
        print(render(pin))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
