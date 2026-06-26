#!/usr/bin/env python3
"""Doc and pin gate for the tool tuning recipe."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
PIN = ROOT / "receipt_pin.json"
DOCS = [ROOT / "README.md", ROOT / "CLAUDE.md"]
PHRASE = "adversarially-confirmed to add value"
REQUIRED_TOKENS = [
    "claude-agent-harness-optimization",
    "efdc801b6e8e4d9cf1e1c32899c8d95325f79304",
    "docs/confirmed-improvements.md",
    "optimize-tools",
    "model-matrix",
    "grind-harness",
]


def line_no(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def strip_code(text: str) -> str:
    return re.sub(r"```[\s\S]*?```|`[^`\n]*`|\]\([^)]*\)|https?://[^\s)]+",
                  lambda match: "\n" * match.group(0).count("\n"), text)


def check_links(path: Path, text: str, failures: list[str]) -> None:
    without_code = re.sub(r"```[\s\S]*?```", lambda m: "\n" * m.group(0).count("\n"), text)
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", without_code):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        rel = target.split("#", 1)[0]
        if rel and not (path.parent / rel).exists():
            failures.append(f"{path.name}:{line_no(without_code, match.start())}: broken link {target}")


def main() -> int:
    failures: list[str] = []
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    commit = pin.get("pinned_commit", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        failures.append("receipt_pin.json: pinned_commit must be a 40 character lowercase SHA")
    if commit not in pin.get("receipt_url", ""):
        failures.append("receipt_pin.json: receipt_url must include pinned_commit")
    if pin.get("receipt_path", "") not in pin.get("receipt_url", ""):
        failures.append("receipt_pin.json: receipt_url must include receipt_path")
    if not (REPO_ROOT / pin.get("founder_kit_receipt", "")).is_file():
        failures.append("receipt_pin.json: founder_kit_receipt must resolve")
    joined_commands = "\n".join(pin.get("commands", []))
    for token in ("optimize-tools", "model-matrix", "grind-harness"):
        if token not in joined_commands:
            failures.append(f"receipt_pin.json: missing command token {token}")

    for directory in ("claude_agent_harness_optimization", "evals", "recipes"):
        if (ROOT / directory).exists():
            failures.append(f"{directory}: companion implementation must not be vendored")

    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        if PHRASE not in text:
            failures.append(f"{doc.name}: missing value-bar phrase")
        for token in REQUIRED_TOKENS:
            if token not in text:
                failures.append(f"{doc.name}: missing {token}")
        check_links(doc, text, failures)
        prose = strip_code(text)
        for match in re.finditer("[\u2013\u2014]", prose):
            failures.append(f"{doc.name}:{line_no(prose, match.start())}: em or en dash")
        for match in re.finditer(";", prose):
            failures.append(f"{doc.name}:{line_no(prose, match.start())}: prose semicolon")

    if failures:
        print("tool_tuning check_docs FAILED:")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print("tool_tuning check_docs passed: pin, docs, links, and prose clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
