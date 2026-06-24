#!/usr/bin/env python3
"""Gate that keeps the repo honest about value claims."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHRASE = "adversarially-confirmed to add value"

REQUIRED = [
    "README.md",
    "CLAUDE.md",
    "VALUE_BAR.md",
    "VALIDATION.md",
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
    "launch/README.md",
    "launch/CLAUDE.md",
    "scale/README.md",
    "scale/CLAUDE.md",
    "quality/README.md",
    "quality/CLAUDE.md",
    "cost/README.md",
    "cost/CLAUDE.md",
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


def main() -> int:
    missing: list[str] = []
    for rel in REQUIRED + skill_docs():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{rel}: missing file")
            continue
        if PHRASE not in path.read_text():
            missing.append(f"{rel}: missing {PHRASE!r}")

    if missing:
        print("value bar gate: FAIL")
        print("\n".join(missing))
        return 1

    print("value bar gate: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
