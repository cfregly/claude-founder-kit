#!/usr/bin/env python3
"""Validate companion registry pins, URLs, and optional clone checks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "companions" / "registry.json"
REQUIRED = {
    "id",
    "name",
    "stage",
    "status",
    "repo",
    "commit",
    "tag",
    "ledger",
    "ledger_url",
    "receipt",
    "checked_on",
    "commands",
    "pin_bump_requires",
}
PIN_BUMP_REQUIRED = {
    "old pin",
    "new pin",
    "what changed",
    "commands run",
    "why founder-kit should move",
}
STATUSES = {"candidate", "mechanically vetted", "adversarially confirmed", "rejected"}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def url_ok(url: str, timeout: int = 10) -> tuple[bool, str]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "claude-founder-kit"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 400, str(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            try:
                with urllib.request.urlopen(url, timeout=timeout) as response:
                    return 200 <= response.status < 400, str(response.status)
            except Exception as inner:  # noqa: BLE001
                return False, str(inner)
        return False, str(exc)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def tag_url(repo: str, tag: str) -> str:
    return f"{repo.rstrip('/')}/tree/{tag}"


def check_clone(entry: dict, failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix=f"founder-kit-{entry['id']}-") as tmp:
        cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            entry["tag"],
            entry["repo"],
            tmp,
        ]
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            fail(f"{entry['id']}: clone failed for tag {entry['tag']}: {result.stderr.strip()}", failures)
            return
        head = subprocess.check_output(["git", "-C", tmp, "rev-parse", "HEAD"], text=True).strip()
        if head != entry["commit"]:
            fail(f"{entry['id']}: tag resolves to {head}, expected {entry['commit']}", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate founder-kit companion registry.")
    parser.add_argument("--verify-urls", action="store_true", help="check repo, ledger, and tag URLs")
    parser.add_argument("--clone", action="store_true", help="clone pinned tags and verify commits")
    args = parser.parse_args()

    failures: list[str] = []
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("schema_version") != 1:
        fail("registry schema_version must be 1", failures)
    companions = registry.get("companions", [])
    if not isinstance(companions, list) or not companions:
        fail("registry must include at least one companion", failures)
        companions = []

    seen_ids: set[str] = set()
    for entry in companions:
        entry_id = entry.get("id", "<missing id>")
        missing = sorted(REQUIRED - set(entry))
        if missing:
            fail(f"{entry_id}: missing fields: {', '.join(missing)}", failures)
            continue
        if entry_id in seen_ids:
            fail(f"{entry_id}: duplicate id", failures)
        seen_ids.add(entry_id)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", entry_id):
            fail(f"{entry_id}: id must be lowercase kebab-case", failures)
        if entry["status"] not in STATUSES:
            fail(f"{entry_id}: unknown status {entry['status']!r}", failures)
        if not re.fullmatch(r"[0-9a-f]{40}", entry["commit"]):
            fail(f"{entry_id}: commit must be a 40 character lowercase SHA", failures)
        if entry["commit"] not in entry["ledger_url"]:
            fail(f"{entry_id}: ledger_url must include commit", failures)
        if entry["ledger"] not in entry["ledger_url"]:
            fail(f"{entry_id}: ledger_url must include ledger path", failures)
        if not (ROOT / entry["receipt"]).is_file():
            fail(f"{entry_id}: receipt does not exist: {entry['receipt']}", failures)
        commands = entry["commands"]
        if not isinstance(commands, list) or not commands:
            fail(f"{entry_id}: commands must be a non-empty list", failures)
        joined_commands = "\n".join(commands)
        if entry["tag"] not in joined_commands:
            fail(f"{entry_id}: commands must checkout the registered tag", failures)
        if set(entry["pin_bump_requires"]) != PIN_BUMP_REQUIRED:
            fail(f"{entry_id}: pin_bump_requires must match the founder-kit bump rule", failures)

        if args.verify_urls:
            for label, url in (
                ("repo", entry["repo"]),
                ("ledger", entry["ledger_url"]),
                ("tag", tag_url(entry["repo"], entry["tag"])),
            ):
                ok, detail = url_ok(url)
                if not ok:
                    fail(f"{entry_id}: {label} URL failed: {url} ({detail})", failures)
        if args.clone:
            check_clone(entry, failures)

    if failures:
        print("check_companions FAILED:")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    mode = "with URLs" if args.verify_urls else "offline"
    if args.clone:
        mode += " and clones"
    print(f"check_companions passed: {len(companions)} companions, {mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
