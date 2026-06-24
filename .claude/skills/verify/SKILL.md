---
name: verify
description: Use this skill to verify the demos whenever you add a lever, change a request shape, or touch the runner. Run it aggressively any time you touch relevant code.
---

Verify the repo with these tools, in order. Do not stop until they pass.

Value bar: verification proves the demos are mechanically vetted, not that they are adversarially-confirmed to add value. If no skeptical workflow receipt exists, report that gap.

1. Run the levers: `ANTHROPIC_API_KEY=... python run.py`. Every lever needs a key, calls the real
   API, and must finish and refresh the receipt at data/last_run.md. Without a key the run must
   fail fast with a clear key-required message and a non-zero exit.
2. Run the deslop gate on the docs: `python scripts/deslop_check.py`. It must be clean. Offline.
3. Run the compile check: `python -m compileall cost_control run.py scripts`. It must succeed. Offline.
4. Read the README lever table against the code in `cost_control/demos.py`. If a row and the code
   disagree, fix the row. The repo lists only the levers it actually runs.
5. The numbers are receipts: every figure a lever prints (cache reads, token counts, the
   context_receipt table) comes from the real usage object, never from memory. Rerun and quote
   your own, the measured table in the README included.

If no key is available, run the offline gates (steps 2 and 3) and confirm step 1 fails fast with
the key-required message under `env -u ANTHROPIC_API_KEY PYTHON_DOTENV_DISABLED=1 python run.py`.
Do not fake a run.

If you hit a blocker, find a solution and update this skill for the future, so the next change
verifies itself. This skill is meant to improve, not stay frozen.
