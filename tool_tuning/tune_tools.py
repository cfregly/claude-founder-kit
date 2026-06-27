#!/usr/bin/env python3
"""Render the pinned tool-tuning companion workflow without vendoring it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
REGISTRY_PATH = REPO_ROOT / "companions" / "registry.json"
COMPANION_ID = "tool-tuning"
REQUIRED = {
    "id",
    "name",
    "repo",
    "commit",
    "tag",
    "ledger",
    "ledger_url",
    "receipt",
    "checked_on",
    "commands",
}


def load_entry(path: Path = REGISTRY_PATH) -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"))
    for entry in registry.get("companions", []):
        if entry.get("id") == COMPANION_ID:
            validate_entry(entry)
            return entry
    raise ValueError(f"companion registry is missing {COMPANION_ID}")


def validate_entry(entry: dict) -> None:
    missing = sorted(REQUIRED - set(entry))
    if missing:
        raise ValueError(f"companion entry is missing fields: {', '.join(missing)}")
    commit = entry["commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("commit must be a 40 character lowercase git SHA")
    if commit not in entry["ledger_url"]:
        raise ValueError("ledger_url must include commit")
    if entry["ledger"] not in entry["ledger_url"]:
        raise ValueError("ledger_url must include ledger")
    receipt = REPO_ROOT / entry["receipt"]
    if not receipt.is_file():
        raise ValueError(f"receipt does not exist: {receipt}")
    commands = entry["commands"]
    if not isinstance(commands, list) or not commands:
        raise ValueError("commands must be a non-empty list")
    required_commands = ("optimize-tools", "model-matrix", "grind-harness")
    joined = "\n".join(commands)
    for token in required_commands:
        if token not in joined:
            raise ValueError(f"commands must include {token}")


def render(entry: dict) -> str:
    lines = [
        f"# {entry['name']}",
        "",
        "Tune one tool means pick one callable and tighten its name, use_when, avoid_when,",
        "input_schema, output contract, context controls, error guidance, examples, negative",
        "guidance, and held-out cases.",
        "",
        "This founder-kit recipe does not copy harness code.",
        "It points to the pinned companion workbench for tool contract tuning.",
        "",
        f"Repo: {entry['repo']}",
        f"Commit: {entry['commit']}",
        f"Tag: {entry['tag']}",
        f"Ledger: {entry['ledger_url']}",
        f"Founder-kit receipt: {entry['receipt']}",
        "",
        "Run the pinned companion workflow:",
        "",
    ]
    lines.extend(f"  {command}" for command in entry["commands"])
    lines.extend(
        [
            "",
            "First watch the weak bundle fail. Then run the passing bundle.",
            "Use optimize-tools for the first contract pass.",
            "Use model-matrix when tool choice depends on model or harness.",
            "Use grind-harness only after you have live eval cases and held-out checks.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the pinned tool tuning recipe.")
    parser.add_argument("--json", action="store_true", help="print the registry entry as JSON")
    args = parser.parse_args()
    entry = load_entry()
    if args.json:
        print(json.dumps(entry, indent=2, sort_keys=True))
    else:
        print(render(entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
