"""Prose gate: README.md and CLAUDE.md must avoid em dashes, en dashes, and semicolons."""
import sys

FILES = ["README.md", "CLAUDE.md"]
bad = []
for f in FILES:
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if "—" in line or "–" in line or ";" in line:
            bad.append("%s:%d: %s" % (f, i, line.rstrip()))

if bad:
    print("\n".join(bad))
    print("FAIL: %d flagged line(s)" % len(bad))
    sys.exit(1)
print("prose clean: README.md and CLAUDE.md free of em dashes, en dashes, and semicolons")
