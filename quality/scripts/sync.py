"""Sync the canonical de-slop ruleset into the sibling repos.

The canonical file is deslop/slop_rules.json in THIS repo. Each sibling repo
under the same parent directory vendors a copy and loads from it, so the word
lists are defined once and cannot drift by hand.

    python scripts/sync.py            copy canonical -> every target
    python scripts/sync.py --check    fail if any target drifts (pre-push / CI)

Targets that have no JSON consumer (claude-gpu-perf-tune docs, claude-prompt-to-
production prompts) cite the canon in prose and are not synced here.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANON = ROOT / "deslop" / "slop_rules.json"
SIBS = ROOT.parent

TARGETS = [
    SIBS / "slop_rules.json",  # resume + deck builder (deslop_rules.js reads this)
    SIBS / "claude-startup-idea" / "validate" / "startup_signal_lab" / "slop_rules.json",
    SIBS / "claude-startup-idea" / "raise" / "pitch_lint" / "slop_rules.json",
    SIBS / "claude-startup-mvp" / "harden" / "contract_doctor" / "slop_rules.json",
]


def main(argv: list[str]) -> int:
    check = "--check" in argv
    canon = CANON.read_text(encoding="utf-8")
    drift, missing, ok = [], [], []
    for t in TARGETS:
        if not t.parent.exists():
            missing.append(t)
            continue
        if check:
            (drift if (not t.exists() or t.read_text(encoding="utf-8") != canon) else ok).append(t)
        else:
            t.write_text(canon, encoding="utf-8")
            ok.append(t)

    for t in missing:
        print(f"skip (no dir): {t.parent}")
    if check:
        for t in drift:
            print(f"DRIFT: {t.relative_to(SIBS)}")
        if drift:
            print(f"\n{len(drift)} target(s) out of sync. Run: python scripts/sync.py")
            return 1
        print(f"in sync: {len(ok)} target(s)")
        return 0
    for t in ok:
        print(f"synced: {t.relative_to(SIBS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
