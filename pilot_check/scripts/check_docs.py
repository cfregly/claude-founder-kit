#!/usr/bin/env python3
"""Deterministic pilot-check doc and template gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TERMS = [
    "proof case",
    "receipt",
    "approval queue",
    "fallback",
    "kill switch",
    "pilot check",
    "permissions",
    "logs",
    "monitoring",
    "rollback",
    "stopping conditions",
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    checklist = (ROOT / "pilot_checklist.md").read_text(encoding="utf-8")
    joined = "\n".join([readme, claude, checklist]).lower()

    if "adversarially-confirmed to add value" not in joined:
        failures.append("missing value-bar phrase")
    for term in REQUIRED_TERMS:
        if term not in joined:
            failures.append(f"missing control term: {term}")

    controls = load_json(ROOT / "templates" / "pilot_check_controls.json")
    gate = load_json(ROOT / "templates" / "access_levels.json")
    tool = load_json(ROOT / "templates" / "tool_contract_template.json")
    receipt = load_json(ROOT / "templates" / "programmatic_tool_calling_receipt.json")
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
    for field in ("log_event_id", "run_id", "case_id", "intent", "permission", "pilot_check", "access_level", "rollout_decision", "log_hash"):
        if field not in controls["logs"]["required_fields"]:
            failures.append(f"log field missing: {field}")
    if gate["stages"] != ["offline", "shadow", "pilot", "default"]:
        failures.append("rollout stages must be offline, shadow, pilot, default")
    if not gate["stopping_conditions"]:
        failures.append("stopping conditions are empty")
    if tool["name"] != "your_narrow_product_tool":
        failures.append("unexpected tool template name")
    if "log_event_id" not in tool["trace_fields"]:
        failures.append("tool template trace fields must include log_event_id")
    if receipt.get("schema_version") != "ptc-cost-receipt-v1":
        failures.append("saved programmatic tool calling receipt has unexpected schema")
    if receipt.get("basis") != "ptc_cost_receipt":
        failures.append("saved programmatic tool calling receipt has unexpected basis")
    if not receipt.get("workflow", {}).get("tool_name"):
        failures.append("saved programmatic tool calling receipt needs workflow.tool_name")
    if receipt.get("claim", {}).get("mode_b_billed_input_tokens", 0) >= receipt.get("claim", {}).get("mode_a_billed_input_tokens", 0):
        failures.append("saved programmatic tool calling receipt must show Mode B below Mode A billed input")
    if receipt.get("answers", {}).get("mode_a") != receipt.get("expected_answer"):
        failures.append("saved programmatic tool calling receipt mode_a answer must match expected_answer")
    if receipt.get("answers", {}).get("mode_b") != receipt.get("expected_answer"):
        failures.append("saved programmatic tool calling receipt mode_b answer must match expected_answer")
    if receipt.get("trace_gate", {}).get("passed") is not True:
        failures.append("saved programmatic tool calling receipt trace gate must pass")
    if len(cases) < 5:
        failures.append("eval template needs at least five cases")
    for expected_id in (
        "proof_case",
        "approval_queue_case",
        "destructive_action_case",
        "fallback_case",
        "wrong_answer_case",
        "trace_drift_case",
        "missing_receipt_case",
        "cost_regression_case",
        "fallback_reason_case",
        "missing_container_case",
    ):
        if expected_id not in {case["id"] for case in cases}:
            failures.append(f"missing eval case: {expected_id}")

    if failures:
        print("pilot_check check_docs: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print("pilot_check check_docs: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
