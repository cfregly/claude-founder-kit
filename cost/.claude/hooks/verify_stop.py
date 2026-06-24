#!/usr/bin/env python3
"""Stop hook: optionally require live verification before Claude stops.

Default behavior is quiet: do not block, because `python run.py` makes paid API calls.
Set CLAUDE_FOUNDER_KIT_REQUIRE_LIVE_VERIFY=1 when you explicitly want the hook to
enforce a fresh live receipt.
"""

import json
import os
import sys
import time
from pathlib import Path

RECEIPT = Path(__file__).resolve().parents[2] / "data" / "last_run.md"
FRESH_SECONDS = 30 * 60


def main():
    try:
        json.load(sys.stdin)  # the Stop hook payload; the decision here does not need its fields
    except Exception:
        pass

    if os.environ.get("CLAUDE_FOUNDER_KIT_REQUIRE_LIVE_VERIFY") != "1":
        sys.exit(0)

    fresh = RECEIPT.exists() and (time.time() - RECEIPT.stat().st_mtime) < FRESH_SECONDS
    if fresh:
        sys.exit(0)  # verification ran recently, let the agent stop

    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    "Live verification is required for this session. Run the verify skill before stopping: "
                    "`python run.py`, then `python scripts/deslop_check.py`. The receipt at "
                    "data/last_run.md is stale or missing."
                ),
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
