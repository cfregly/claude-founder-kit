#!/usr/bin/env python3
"""Deterministic day-0 doc and template gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TERMS = ["evals", "permissions", "monitoring", "rollback", "stopping conditions"]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    checklist = (ROOT / "trust_checklist.md").read_text(encoding="utf-8")
    joined = "\n".join([readme, claude, checklist]).lower()

    if "adversarially-confirmed to add value" not in joined:
        failures.append("missing value-bar phrase")
    for term in REQUIRED_TERMS:
        if term not in joined:
            failures.append(f"missing control term: {term}")

    controls = load_json(ROOT / "templates" / "trust_controls.json")
    gate = load_json(ROOT / "templates" / "rollout_gate.json")
    tool = load_json(ROOT / "templates" / "tool_contract_template.json")
    cases = [
        json.loads(line)
        for line in (ROOT / "evals" / "template.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for bucket in ("always", "ask", "never"):
        if not controls["permissions"].get(bucket):
            failures.append(f"permissions.{bucket} is empty")
    for signal in ("eval_pass_rate", "latency_p95_ms", "fallback_rate", "policy_denial_rate"):
        if signal not in controls["monitoring"]["signals"]:
            failures.append(f"monitoring signal missing: {signal}")
    if gate["stages"] != ["offline", "shadow", "canary", "default"]:
        failures.append("rollout stages must be offline, shadow, canary, default")
    if not gate["stopping_conditions"]:
        failures.append("stopping conditions are empty")
    if tool["name"] != "fetch_activation_events":
        failures.append("unexpected tool template name")
    if len(cases) < 5:
        failures.append("eval template needs at least five cases")
    for expected_id in ("win_case", "honesty_case", "permission_ask_case", "rollback_case", "stop_case"):
        if expected_id not in {case["id"] for case in cases}:
            failures.append(f"missing eval case: {expected_id}")

    if failures:
        print("day0 check_docs: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print("day0 check_docs: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
