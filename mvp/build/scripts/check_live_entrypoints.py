#!/usr/bin/env python3
"""Exercise live script entrypoints without spending tokens.

The live scripts should fail cleanly without a key. This catches missing imports,
top-level crashes, and accidental sample fallbacks before a founder copies a
quickstart command.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRYPOINTS = [
    "01_first_call.py",
    "02_agent_with_tools.py",
    "03_evals.py",
    "04_cost_engineering.py",
    "06_structured_output.py",
]


def main() -> int:
    failures: list[str] = []
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["PYTHON_DOTENV_DISABLED"] = "1"

    for rel in ENTRYPOINTS:
        proc = subprocess.run(
            [sys.executable, rel],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
        output = proc.stdout + proc.stderr
        if proc.returncode == 0:
            failures.append(f"{rel}: exited 0 without a key")
        if "Traceback" in output:
            failures.append(f"{rel}: traceback instead of clean key-required failure")
        if "ANTHROPIC_API_KEY" not in output:
            failures.append(f"{rel}: missing explicit ANTHROPIC_API_KEY error")

    if failures:
        print("live entrypoint gate: FAIL")
        print("\n".join(failures))
        return 1
    print(f"live entrypoint gate: clean ({len(ENTRYPOINTS)} scripts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
