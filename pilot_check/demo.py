#!/usr/bin/env python3
"""Deterministic programmatic tool calling pilot check.

The harness is intentionally keyless. It checks whether the customer-evidence
programmatic tool calling receipt is safe enough to promote to a pilot candidate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_RECEIPT = ROOT / "templates" / "programmatic_tool_calling_receipt.json"
BASIS = "ptc_cost_receipt"


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
        return "allow", "read-only proof or analysis"
    if intent in policy["ask"]:
        return "ask", "outward action requires approval"
    if intent in policy["never"]:
        return "deny", "action is outside the pilot boundary"
    return "deny", "unknown intent fails closed"


def receipt_problems(receipt: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not receipt:
        return ["missing_receipt"]

    if receipt.get("schema_version") != "ptc-cost-receipt-v1":
        problems.append("schema_version")
    if not receipt.get("workload"):
        problems.append("workload")
    if receipt.get("basis") != BASIS:
        problems.append("basis")
    workflow = receipt.get("workflow") or {}
    if not workflow.get("tool_name"):
        problems.append("tool_name")

    claim = receipt.get("claim") or {}
    mode_a = claim.get("mode_a_billed_input_tokens")
    mode_b = claim.get("mode_b_billed_input_tokens")
    if not isinstance(mode_a, int) or not isinstance(mode_b, int):
        problems.append("billed_input_tokens")
    elif mode_b >= mode_a:
        problems.append("cost_regression")
    if claim.get("same_answer") is not True:
        problems.append("same_answer")

    expected = receipt.get("expected_answer")
    answers = receipt.get("answers") or {}
    mode_a_answer = answers.get("mode_a")
    mode_b_answer = answers.get("mode_b")
    if expected is None:
        expected = (receipt.get("accounts") or {}).get("expected")
        mode_a_answer = mode_a_answer or (receipt.get("accounts") or {}).get("mode_a")
        mode_b_answer = mode_b_answer or (receipt.get("accounts") or {}).get("mode_b")
    if expected is None:
        problems.append("expected_answer")
    if mode_a_answer != expected:
        problems.append("mode_a_answer")
    if mode_b_answer != expected:
        problems.append("mode_b_answer")

    trace = receipt.get("trace_gate") or {}
    if trace.get("passed") is not True:
        problems.append("trace_gate")
    if trace.get("caller_path") != "code_execution_20260120":
        problems.append("caller_path")
    if trace.get("server_tool_blocks", 0) < 1:
        problems.append("server_tool_blocks")
    if trace.get("container_count", 0) < 1:
        problems.append("container")
    if trace.get("caller_path_drift") is True:
        problems.append("caller_path_drift")
    if trace.get("fallback_reason") is not None:
        problems.append("fallback_reason")
    if trace.get("correctness") is not True:
        problems.append("correctness")
    if trace.get("raw_tool_bytes", 0) <= trace.get("final_bytes", 0):
        problems.append("reducer_size")

    return problems


def mutate_receipt(receipt: dict[str, Any], variant: str | None) -> dict[str, Any]:
    if not variant:
        return copy.deepcopy(receipt)
    out = copy.deepcopy(receipt)
    if variant == "wrong_answer":
        expected = list(out.get("expected_answer") or (out.get("accounts") or {}).get("expected") or ["wrong"])
        replacement = list(expected)
        replacement[-1] = "wrong_answer" if replacement else "wrong_answer"
        out.setdefault("answers", {})["mode_b"] = replacement
        out.setdefault("accounts", {})["mode_b"] = replacement
        out.setdefault("claim", {})["same_answer"] = False
        out.setdefault("trace_gate", {})["correctness"] = False
    elif variant == "trace_drift":
        out.setdefault("trace_gate", {})["caller_path_drift"] = True
        out.setdefault("trace_gate", {})["passed"] = False
        out.setdefault("trace_gate", {})["problems"] = ["caller_path_drift"]
    elif variant == "missing_receipt":
        out = {}
    elif variant == "cost_regression":
        claim = out.setdefault("claim", {})
        claim["mode_b_billed_input_tokens"] = claim.get("mode_a_billed_input_tokens", 0) + 1
        claim["input_reduction_pct"] = -0.1
    elif variant == "fallback_reason":
        out.setdefault("trace_gate", {})["fallback_reason"] = "caller_path_drift"
        out.setdefault("trace_gate", {})["passed"] = False
        out.setdefault("trace_gate", {})["problems"] = ["fallback_reason"]
    elif variant == "missing_container":
        out.setdefault("trace_gate", {})["container_count"] = 0
        out.setdefault("trace_gate", {})["passed"] = False
        out.setdefault("trace_gate", {})["problems"] = ["container"]
    return out


def monitor_snapshot(case: dict[str, Any], controls: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("metrics", {})
    defaults = controls["monitoring"]["defaults"]
    claim = receipt.get("claim") or {}
    return {
        "eval_pass_rate": metrics.get("eval_pass_rate", defaults["eval_pass_rate"]),
        "latency_p95_ms": metrics.get("latency_p95_ms", defaults["latency_p95_ms"]),
        "fallback_rate": metrics.get("fallback_rate", defaults["fallback_rate"]),
        "policy_denial_rate": metrics.get("policy_denial_rate", defaults["policy_denial_rate"]),
        "cost_per_successful_task_usd": metrics.get(
            "cost_per_successful_task_usd",
            defaults["cost_per_successful_task_usd"],
        ),
        "mode_a_billed_input_tokens": claim.get("mode_a_billed_input_tokens"),
        "mode_b_billed_input_tokens": claim.get("mode_b_billed_input_tokens"),
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
    if stage in {"pilot", "default"}:
        return {"stage": stage, "decision": "rollback", "failures": failures, "rollback_to": gate["rollback_to"]}
    return {"stage": stage, "decision": "stop", "failures": failures, "rollback_to": None}


def log_entry(
    case: dict[str, Any],
    run_id: str,
    permission: str,
    rollout: dict[str, Any],
    observed: dict[str, Any],
    receipt: dict[str, Any],
    problems: list[str],
) -> dict[str, Any]:
    entry = {
        "log_event_id": "log_" + stable_run_id("log", {"run_id": run_id, "case_id": case["id"]}),
        "run_id": run_id,
        "case_id": case["id"],
        "actor": "pilot_check_harness",
        "intent": case["input"]["intent"],
        "permission": permission,
        "pilot_check": "fail" if problems else "pass",
        "access_level": "pilot_candidate" if not problems else "offline_only",
        "rollout_decision": rollout["decision"],
        "fallback": "direct_path" if rollout["decision"] == "rollback" else None,
        "receipt_source": receipt.get("receipt_source"),
        "monitoring": observed,
        "trace_present": not problems or "missing_receipt" not in problems,
    }
    entry["log_hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return entry


def answer_for_case(case: dict[str, Any], controls: dict[str, Any], gate: dict[str, Any], base_receipt: dict[str, Any]) -> dict[str, Any]:
    case_receipt = mutate_receipt(base_receipt, case.get("receipt_variant"))
    problems = receipt_problems(case_receipt)
    intent = case["input"]["intent"]
    permission, reason = permission_decision(intent, controls)
    observed = monitor_snapshot(case, controls, case_receipt)
    rollout = rollout_decision(case, gate, observed)
    kill_switch = bool(problems) or rollout["decision"] in {"rollback", "stop"} or permission == "deny"
    fallback = "direct_path" if rollout["decision"] == "rollback" else None
    run_id = stable_run_id(case["id"], case["input"])

    evidence = {
        "answer": (case_receipt.get("answers") or {}).get("mode_b")
        or (case_receipt.get("accounts") or {}).get("mode_b"),
        "source_ids": ["ticket_8831", "log_52991", "usage_771"],
        "caveats": problems,
    }
    if permission != "allow":
        evidence["caveats"] = [reason]

    result = {
        "run_id": run_id,
        "case_id": case["id"],
        "claim": case["claim"],
        "permission": permission,
        "permission_reason": reason,
        "receipt_problems": problems,
        "monitoring": observed,
        "rollout": rollout,
        "rollback": rollout["decision"] == "rollback",
        "fallback": fallback,
        "kill_switch": kill_switch,
        "stopping_condition": kill_switch,
        "evidence": evidence,
    }
    result["logs"] = log_entry(case, run_id, permission, rollout, observed, case_receipt, problems)
    result["passed"] = case_passed(result, case["expected"])
    return result


def case_passed(result: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, want in expected.items():
        if result.get(key) != want:
            return False
    return True


def run_suite(receipt_path: Path | str = DEFAULT_RECEIPT) -> dict[str, Any]:
    receipt_path = Path(receipt_path)
    controls = load_json(ROOT / "templates" / "pilot_check_controls.json")
    gate = load_json(ROOT / "templates" / "access_levels.json")
    cases = load_jsonl(ROOT / "evals" / "template.jsonl")

    try:
        receipt = load_json(receipt_path)
        load_error = None
    except FileNotFoundError:
        receipt = {}
        load_error = f"receipt not found: {receipt_path}"
    except json.JSONDecodeError as exc:
        receipt = {}
        load_error = f"receipt json error: {exc}"

    baseline_problems = receipt_problems(receipt)
    if load_error:
        baseline_problems = [load_error]

    results = [answer_for_case(case, controls, gate, receipt) for case in cases]
    passed = sum(1 for result in results if result["passed"])
    evals_pass = passed == len(results)
    pilot_pass = not baseline_problems
    status = "pass" if evals_pass and pilot_pass else "fail"

    return {
        "workload": receipt.get("workload"),
        "workflow": receipt.get("workflow"),
        "basis": BASIS,
        "stage": "pilot_check",
        "status": status,
        "pilot_check": "pass" if pilot_pass else "fail",
        "access_level": "pilot_candidate" if pilot_pass else "offline_only",
        "fallback": "direct_path",
        "receipt_path": str(receipt_path),
        "receipt_source": receipt.get("receipt_source"),
        "receipt_problems": baseline_problems,
        "controls": ["proof_case", "receipt", "approval_queue", "fallback", "kill_switch"],
        "evals": {"passed": passed, "total": len(results)},
        "results": results,
        "next_live_steps": [
            "make programmatic_tool_calling RECEIPT_OUT=/tmp/programmatic_tool_calling_receipt.json",
            "make pilot-check RECEIPT=/tmp/programmatic_tool_calling_receipt.json",
            "shadow the direct path before pilot traffic",
        ],
    }


def percent_reduction(mode_a: int | None, mode_b: int | None) -> str:
    if not isinstance(mode_a, int) or not isinstance(mode_b, int) or mode_a <= 0:
        return "unknown"
    return f"{((mode_a - mode_b) / mode_a) * 100:.1f}% fewer"


def case_lookup(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["case_id"]: row for row in receipt["results"]}


def format_summary(receipt: dict[str, Any]) -> str:
    cases = case_lookup(receipt)
    proof = cases.get("proof_case", {})
    proof_monitoring = proof.get("monitoring") or {}
    mode_a = proof_monitoring.get("mode_a_billed_input_tokens")
    mode_b = proof_monitoring.get("mode_b_billed_input_tokens")
    workflow = receipt.get("workflow") or {}
    destructive = cases.get("destructive_action_case", {})
    fallback = cases.get("fallback_case", {})
    approval = cases.get("approval_queue_case", {})
    baseline_pass = not receipt.get("receipt_problems")

    lines = [
        "Pilot check report",
        "==================",
        "What ran: keyless, deterministic gate over an existing programmatic tool calling receipt.",
        "What did not run: no Claude API call, no live tools, no customer traffic.",
        "",
        f"Receipt: {receipt.get('receipt_path')}",
        f"Workflow: {receipt.get('workload') or workflow.get('name')}",
        f"Tool: {workflow.get('tool_name')}",
        f"Decision: {receipt.get('status', '').upper()} -> access_level={receipt.get('access_level')}",
        f"Gate behaviors: {receipt['evals']['passed']}/{receipt['evals']['total']} behaved as expected",
        "Meaning: the live receipt is good enough for pilot-candidate status, and the bad scenarios are stopped.",
        "This does not mean production-ready or default-on.",
        "",
        "What this command tests",
        "1. Receipt is real enough: same answer, lower billed input, clean trace.",
        "2. Workflow is bounded: one workflow, one tool, no broad launch.",
        "3. Approval works: outward customer action asks first.",
        "4. Dangerous actions fail closed: destructive action is denied and trips the kill switch.",
        "5. Bad receipts stop launch: wrong answer, trace drift, missing receipt, cost regression, "
        "fallback reason, and missing container.",
        "6. Pilot health regression rolls back to direct tool use: direct_path is the baseline non-programmatic path.",
        "",
        "1) Live receipt check",
        f"- Same answer: {'PASS' if baseline_pass else 'FAIL'}",
        f"- Token gate: {mode_a} -> {mode_b} billed input tokens ({percent_reduction(mode_a, mode_b)})",
        f"- Trace gate: {'PASS' if baseline_pass else 'FAIL'}",
        f"- Baseline problems: {', '.join(receipt.get('receipt_problems') or ['none'])}",
        "",
        "2) Launch-safety drills",
        f"- Good proof case: {proof.get('rollout', {}).get('decision')} with permission={proof.get('permission')}",
        f"- Outward action drill: permission={approval.get('permission')} until approved",
        f"- Destructive action drill: permission={destructive.get('permission')}, kill_switch={destructive.get('kill_switch')}",
        f"- Simulated pilot regression drill: failures={fallback.get('rollout', {}).get('failures')} "
        f"-> rollout={fallback.get('rollout', {}).get('decision')}, fallback={fallback.get('fallback')}",
        "- Stop cases covered: wrong answer, trace drift, missing receipt, cost regression, "
        "fallback reason, missing container",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a programmatic tool calling cost receipt before pilot access.")
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT), help="programmatic tool calling receipt JSON to check")
    parser.add_argument("--json", action="store_true", help="print the full machine-readable result")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = run_suite(args.receipt)
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(format_summary(receipt))
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
