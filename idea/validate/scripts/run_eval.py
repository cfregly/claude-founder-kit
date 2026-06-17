from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python scripts/run_eval.py` from the repo root without an install step.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from startup_signal_lab.evals import run_evals  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Startup Linter eval suite. Grades Claude's intervention "
        "on each case and needs ANTHROPIC_API_KEY set."
    )
    parser.parse_args()
    print(json.dumps(run_evals(), indent=2))
