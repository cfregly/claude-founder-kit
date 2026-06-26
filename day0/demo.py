#!/usr/bin/env python3
"""Deterministic day-0 trust receipt.

The harness is intentionally small and keyless. It lets a founder inspect the
control shape before a live Claude workflow touches data or takes action.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stable_run_id(case_id: str, payload: dict[str, Any]) -> str:
    body = json.dumps({"case_id": case_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def permission_decision(intent: str, controls: dict[str, Any]) -> tuple[str, str]:
    policy = controls["permissions"]
    if intent in policy["always"]:
        return "allow", "internal read or analysis"
    if intent in policy["ask"]:
        return "ask", "outward action requires approval"
    if intent in policy["never"]:
        return "deny", "action is outside the day-0 boundary"
    return "deny", "unknown intent fails closed"


def monitor_snapshot(case: dict[str, Any], controls: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("metrics", {})
    defaults = controls["monitoring"]["defaults"]
    return {
        "eval_pass_rate": metrics.get("eval_pass_rate", defaults["eval_pass_rate"]),
        "latency_p95_ms": metrics.get("latency_p95_ms", defaults["latency_p95_ms"]),
        "fallback_rate": metrics.get("fallback_rate", defaults["fallback_rate"]),
        "policy_denial_rate": metrics.get("policy_denial_rate", defaults["policy_denial_rate"]),
        "cost_per_successful_task_usd": metrics.get(
            "cost_per_successful_task_usd",
            defaults["cost_per_successful_task_usd"],
        ),
    }


def rollout_decision(case: dict[str, Any], gate: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    stage = case.get("rollout_stage", "offline")
    thresholds = gate["thresholds"]
    failures: list[str] = []
    if observed["eval_pass_rate"] < thresholds["min_eval_pass_rate"]:
        failures.append("eval_pass_rate")
    if observed["latency_p95_ms"] > thresholds["max_latency_p95_ms"]:
        failures.append("latency_p95_ms")
    if observed["fallback_rate"] > thresholds["max_fallback_rate"]:
        failures.append("fallback_rate")
    if observed["policy_denial_rate"] > thresholds["max_policy_denial_rate"]:
        failures.append("policy_denial_rate")
    if observed["cost_per_successful_task_usd"] > thresholds["max_cost_per_successful_task_usd"]:
        failures.append("cost_per_successful_task_usd")

    if not failures:
        return {"stage": stage, "decision": "continue", "failures": [], "rollback_to": None}
    if stage in {"canary", "default"}:
        return {"stage": stage, "decision": "rollback", "failures": failures, "rollback_to": gate["rollback_to"]}
    return {"stage": stage, "decision": "stop", "failures": failures, "rollback_to": None}


def log_entry(
    case: dict[str, Any],
    run_id: str,
    permission: str,
    rollout: dict[str, Any],
    observed: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    entry = {
        "log_event_id": "log_" + stable_run_id("log", {"run_id": run_id, "case_id": case["id"]}),
        "run_id": run_id,
        "case_id": case["id"],
        "actor": "day0_harness",
        "intent": case["input"]["intent"],
        "permission": permission,
        "rollout_decision": rollout["decision"],
        "fallback": "direct_path" if rollout["decision"] == "rollback" else None,
        "source_ids": evidence["source_ids"],
        "monitoring": observed,
        "trace_present": True,
    }
    entry["log_hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return entry


def answer_for_case(case: dict[str, Any], controls: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    intent = case["input"]["intent"]
    permission, reason = permission_decision(intent, controls)
    observed = monitor_snapshot(case, controls)
    rollout = rollout_decision(case, gate, observed)
    stop_condition = rollout["decision"] in {"rollback", "stop"} or permission == "deny"
    run_id = stable_run_id(case["id"], case["input"])

    evidence = {
        "source_ids": ["evt_001", "evt_002", "evt_003"],
        "row_count": 3,
        "caveats": [],
    }
    if intent == "summarize_missing_metric":
        evidence["caveats"] = ["billing metric unavailable"]
    if permission != "allow":
        evidence["caveats"] = [reason]

    return {
        "run_id": run_id,
        "case_id": case["id"],
        "claim": case["claim"],
        "permission": permission,
        "permission_reason": reason,
        "monitoring": observed,
        "rollout": rollout,
        "rollback": rollout["decision"] == "rollback",
        "stopping_condition": stop_condition,
        "fallback": "direct_path" if rollout["decision"] == "rollback" else None,
        "evidence": evidence,
        "logs": log_entry(case, run_id, permission, rollout, observed, evidence),
    }


def case_passed(result: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, want in expected.items():
        if result.get(key) != want:
            return False
    return True


def run_suite() -> dict[str, Any]:
    controls = load_json(ROOT / "templates" / "trust_controls.json")
    gate = load_json(ROOT / "templates" / "rollout_gate.json")
    cases = load_jsonl(ROOT / "evals" / "template.jsonl")
    results = []
    for case in cases:
        result = answer_for_case(case, controls, gate)
        result["passed"] = case_passed(result, case["expected"])
        results.append(result)

    passed = sum(1 for result in results if result["passed"])
    return {
        "stage": "day0",
        "status": "pass" if passed == len(results) else "fail",
        "controls": ["evals", "permissions", "logs", "monitoring", "rollback", "stopping_conditions"],
        "evals": {"passed": passed, "total": len(results)},
        "results": results,
        "next_live_steps": [
            "make demo-first_hour",
            "cd mvp/build && python 03_evals.py",
            "cd mvp/harden && make demo",
            "make companion ID=feature-hits",
            "make tune-tools",
        ],
    }


def main() -> int:
    receipt = run_suite()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
