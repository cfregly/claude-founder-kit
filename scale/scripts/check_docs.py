#!/usr/bin/env python3
"""Doc-correctness gate: the docs must match the code.

Checks, in order: the marquee moat numbers reproduce from the sample cohort and
appear in the README, every CLI flag is documented, every environment variable the
code reads is documented, the relative links resolve, and the prose carries no
em-dashes, no en-dashes, no prose semicolons, and no draft markers. Exit non-zero
on any failure so CI fails the build.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json                                          # noqa: E402

from scale.measure import metrics                    # noqa: E402
from scale.__main__ import build_parser              # noqa: E402

FAILS: list[str] = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


# 1. The marquee numbers reproduce from the sample cohort.
cohort = json.loads((ROOT / "examples" / "cohort.json").read_text())
readout = metrics.summarize(cohort)
top = next(s for s in readout["scores"] if s["name"] == "acct_01")
dist = readout["moat_distribution"]
reproduced = {
    "acct_01 moat 100": top["moat"] == 100,
    "median moat 60": readout["median_moat"] == 60.0,
    "distribution 5/3/2": (dist["deep"], dist["forming"], dist["shallow"]) == (5, 3, 2),
    "3 expansion-ready": readout["the_number"]["value"] == 3,
    "5 compounding-data": len(readout["compounding_data_accounts"]) == 5,
}
for label, ok in reproduced.items():
    check(ok, f"marquee number changed: {label}")

readme = (ROOT / "README.md").read_text()
for token in ["100", "60", "5 / 3 / 2", "expansion-ready"]:
    check(token in readme, f"README is missing a reproducible number: {token!r}")

# 2. Every CLI flag is documented in the README, CLAUDE.md, or the Makefile.
parser = build_parser()
flags = [s for a in parser._actions for s in a.option_strings
         if s.startswith("--") and s != "--help"]
docs = "\n".join((ROOT / f).read_text() for f in ("README.md", "CLAUDE.md", "Makefile"))
for flag in flags:
    check(flag in docs, f"CLI flag not documented: {flag}")

# 3. Every environment variable the code reads is documented.
env_keys = set()
for py in (ROOT / "scale").rglob("*.py"):
    text = py.read_text()
    env_keys |= set(re.findall(r'os\.(?:environ\.get|getenv)\(\s*["\']([A-Z_]+)["\']', text))
    env_keys |= set(re.findall(r'os\.environ\[\s*["\']([A-Z_]+)["\']', text))
for key in sorted(env_keys):
    check(key in docs, f"env var read by code but not documented: {key}")

# 4. Relative links in the docs resolve.
for md_name in ("README.md", "CLAUDE.md"):
    md = (ROOT / md_name).read_text()
    for target in re.findall(r"\]\(([^)]+)\)", md):
        if target.startswith(("http", "#")):
            continue
        path = target.split("#")[0]
        check((ROOT / path).exists(), f"{md_name}: broken relative link {target!r}")

# 5. No em-dashes, en-dashes, prose semicolons, or draft markers in markdown prose.
for md in ROOT.rglob("*.md"):
    if any(p in md.parts for p in (".git", ".venv")):
        continue
    in_fence = False
    for line in md.read_text().splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = re.sub(r"`[^`]*`", "", line)
        check("—" not in prose, f"{md.name}: em-dash in prose: {line.strip()[:50]!r}")
        check("–" not in prose, f"{md.name}: en-dash in prose: {line.strip()[:50]!r}")
        check(";" not in prose, f"{md.name}: semicolon in prose: {line.strip()[:50]!r}")
        check(not re.search(r"\b(TODO|FIXME|TBD|XXX|PLACEHOLDER)\b", prose),
              f"{md.name}: draft marker in {line.strip()[:50]!r}")

if FAILS:
    print("check_docs FAILED:")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)
print(f"check_docs passed: {len(reproduced)} numbers reproduced, "
      f"{len(flags)} CLI flags documented, {len(env_keys)} env vars covered, "
      "links and prose clean.")
