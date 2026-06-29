#!/usr/bin/env python3
"""Gate that keeps the repo honest about value claims."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PHRASE = "adversarially-confirmed to add value"

REQUIRED = [
    "README.md",
    "CLAUDE.md",
    "GETTING_STARTED.md",
    "TRUST.md",
    "VALUE_BAR.md",
    "VALIDATION.md",
    "companions/README.md",
    "pilot_check/README.md",
    "pilot_check/CLAUDE.md",
    "first_hour/README.md",
    "first_hour/CLAUDE.md",
    "idea/README.md",
    "idea/CLAUDE.md",
    "idea/raise/README.md",
    "idea/raise/CLAUDE.md",
    "idea/validate/README.md",
    "idea/validate/CLAUDE.md",
    "mvp/README.md",
    "mvp/CLAUDE.md",
    "mvp/build/README.md",
    "mvp/build/CLAUDE.md",
    "mvp/harden/README.md",
    "mvp/harden/CLAUDE.md",
    "tool_tuning/README.md",
    "tool_tuning/CLAUDE.md",
    "launch/README.md",
    "launch/CLAUDE.md",
    "launch/FOUNDER_ACTIVATION_FIELD_GUIDE.md",
    "scale/README.md",
    "scale/CLAUDE.md",
    "quality/README.md",
    "quality/CLAUDE.md",
    "cost/README.md",
    "cost/CLAUDE.md",
]

SCAN_SUFFIXES = {".md", ".txt", ".py", ".yaml", ".yml", ".json"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "dist", "site-packages"}
CLAIM_PATTERNS = [
    (re.compile(r"\bfounder playbook for Claude builders\b", re.I),
     "use founder workflow kit language"),
    (re.compile(r"\bStartup Activation Playbook\b", re.I),
     "use Founder Activation Field Guide language"),
    (re.compile(r"\bAnthropic playbook\b|\bofficial Anthropic\b|\bofficial playbook\b", re.I),
     "do not imply official Anthropic ownership"),
    (re.compile(r"\bevery tier is proven\b|\bproof every tier\b", re.I),
     "record a gate instead of claiming proof"),
    (re.compile(r"\bguaranteed to resolve\b", re.I),
     "scope the claim to a verified run"),
    (re.compile(r"\bprove and scale\b", re.I),
     "measure before using prove/proof framing"),
    (re.compile(r"\boperator playbook v1\b", re.I),
     "use guide or field guide wording"),
]


def skill_docs() -> list[str]:
    roots = [
        ".claude/skills",
        "idea/raise/skills",
        "idea/validate/skills",
        "mvp/build/skills",
        "mvp/harden/skills",
        "launch/skills",
        "scale/skills",
        "quality/skills",
    ]
    paths: list[str] = []
    for root in roots:
        base = ROOT / root
        if base.exists():
            paths.extend(str(path.relative_to(ROOT)) for path in base.glob("*/SKILL.md"))
    return sorted(paths)


def scanned_files() -> list[Path]:
    files: list[Path] = []
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    for rel_text in result.stdout.splitlines():
        path = ROOT / rel_text
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if rel_text == "scripts/check_value_bar.py":
            continue
        rel_parts = set(Path(rel_text).parts)
        if rel_parts & SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


def value_claim_findings() -> list[str]:
    findings: list[str] = []
    for path in scanned_files():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for pattern, fix in CLAIM_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{rel}:{line}: {match.group(0)!r} - {fix}")
    return findings


def main() -> int:
    missing: list[str] = []
    for rel in REQUIRED + skill_docs():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{rel}: missing file")
            continue
        if PHRASE not in path.read_text():
            missing.append(f"{rel}: missing {PHRASE!r}")

    findings = missing + value_claim_findings()
    if findings:
        print("value bar gate: FAIL")
        print("\n".join(findings))
        return 1

    print("value bar gate: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
