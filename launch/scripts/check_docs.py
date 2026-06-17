#!/usr/bin/env python3
"""Doc-correctness gate: the docs must match the code.

Checks, in order: the marquee numbers reproduce from the demo and appear in the
README, every CLI subcommand is documented, every environment variable the code
reads is in .env.example, the relative links resolve, the prose carries no
em-dashes or en-dashes, and nothing ships with a draft marker. Exit non-zero on
any failure so CI fails the build.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from activation import contracts, pipeline           # noqa: E402
from activation.__main__ import build_parser         # noqa: E402
from activation.capture import queries               # noqa: E402

FAILS: list[str] = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


# 1. The marquee numbers reproduce from the seed-7 demo.
rows = pipeline.capture_rows()
q = {x["id"]: x["value"] for x in queries.run_all(rows)}
funnel = "/".join(str(q["Q11"][s]) for s in contracts.STAGES)
result = pipeline.run()
readout = result["readout"]
reproduced = {
    "165 events": len(rows) == 165,
    "funnel 12/12/10/8/5/4/3/1": funnel == "12/12/10/8/5/4/3/1",
    "Q9 = 5": q["Q9"] == 5,
    "activation 67%": readout["activation_rate"] == 0.67,
    "retention 62%": readout["retention_rate"] == 0.62,
    "time-to-second-build 8": readout["time_to_second_build_days"] == 8,
    "2 PQAs": len(readout["pqas_ready_for_handoff"]) == 2,
    "time-to-first-value 2.0": result["signals"]["time_to_first_value_days"] == 2.0,
}
for label, ok in reproduced.items():
    check(ok, f"marquee number changed: {label}")

readme = (ROOT / "README.md").read_text()
for token in ["165 events", "12 / 12 / 10 / 8 / 5 / 4 / 3 / 1",
              "67%", "62%", "8-day", "2.0 days", "Q9"]:
    check(token in readme, f"README is missing a reproducible number: {token!r}")

# 2. Every CLI subcommand is documented in the README, CLAUDE.md, or the Makefile.
parser = build_parser()
subs = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
docs = "\n".join((ROOT / f).read_text() for f in ("README.md", "CLAUDE.md", "Makefile"))
for name in subs.choices:
    check(name in docs, f"CLI subcommand not documented: {name}")

# 3. Every environment variable the code reads is in .env.example.
env_keys = set()
for py in (ROOT / "activation").rglob("*.py"):
    text = py.read_text()
    env_keys |= set(re.findall(r'os\.(?:environ\.get|getenv)\(\s*["\']([A-Z_]+)["\']', text))
    env_keys |= set(re.findall(r'os\.environ\[\s*["\']([A-Z_]+)["\']', text))
env_example = (ROOT / ".env.example").read_text()
for key in sorted(env_keys):
    check(key in env_example, f"env var read by code but missing from .env.example: {key}")

# 4. Relative links in the docs resolve.
for md_name in ("README.md", "CLAUDE.md", "PLATFORM_COVERAGE.md"):
    md = (ROOT / md_name).read_text()
    for target in re.findall(r"\]\(([^)]+)\)", md):
        if target.startswith(("http", "#")):
            continue
        path = target.split("#")[0]
        check((ROOT / path).exists(), f"{md_name}: broken relative link {target!r}")

# 5. No em-dashes or en-dashes in markdown prose (deslop owns the full check).
# 6. No draft markers anywhere shipped.
for md in ROOT.rglob("*.md"):
    if ".git" in md.parts:
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
        check(not re.search(r"\b(TODO|FIXME|TBD|XXX|PLACEHOLDER)\b", prose),
              f"{md.name}: draft marker in {line.strip()[:50]!r}")

if FAILS:
    print("check_docs FAILED:")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)
print(f"check_docs passed: {len(reproduced)} numbers reproduced, "
      f"{len(list(subs.choices))} subcommands documented, "
      f"{len(env_keys)} env vars covered, links and prose clean.")
