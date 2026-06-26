#!/usr/bin/env python3
"""Render the founder-kit companion registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "companions" / "registry.json"


def load_registry(path: Path = REGISTRY) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entries(registry: dict) -> list[dict]:
    return list(registry.get("companions", []))


def find_entry(registry: dict, entry_id: str) -> dict:
    for entry in entries(registry):
        if entry["id"] == entry_id:
            return entry
    raise SystemExit(f"unknown companion id: {entry_id}")


def render_entry(entry: dict) -> str:
    lines = [
        f"# {entry['name']}",
        "",
        f"ID: {entry['id']}",
        f"Stage: {entry['stage']}",
        f"Status: {entry['status']}",
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
    return "\n".join(lines)


def render_list(registry: dict) -> str:
    lines = [
        "# Founder-kit companions",
        "",
        "Founder-kit is the front door. Companion repos keep the deep implementation work.",
        "",
    ]
    for entry in entries(registry):
        lines.append(
            f"- {entry['id']}: {entry['name']} [{entry['status']}] "
            f"stage={entry['stage']} tag={entry['tag']}"
        )
    lines.extend(
        [
            "",
            "Use `make companion ID=<id>` to print one pinned workflow.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render founder-kit companion registry entries.")
    parser.add_argument("--id", help="render one companion by id")
    parser.add_argument("--json", action="store_true", help="print raw registry JSON")
    args = parser.parse_args()

    registry = load_registry()
    if args.json:
        print(json.dumps(registry, indent=2, sort_keys=True))
    elif args.id:
        print(render_entry(find_entry(registry, args.id)))
    else:
        print(render_list(registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
