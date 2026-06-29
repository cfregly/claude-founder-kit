from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import demo


class PilotCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = demo.load_json(demo.DEFAULT_RECEIPT)

    def test_suite_passes_saved_programmatic_tool_calling_receipt(self) -> None:
        result = demo.run_suite()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["pilot_check"], "pass")
        self.assertEqual(result["basis"], "ptc_cost_receipt")
        self.assertEqual(result["access_level"], "pilot_candidate")
        self.assertEqual(result["evals"]["passed"], result["evals"]["total"])

    def test_receipt_can_describe_a_founders_own_workflow(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["workload"] = "founder_product_workflow"
        receipt["workflow"]["name"] = "founder_product_workflow"
        receipt["workflow"]["tool_name"] = "query_founder_product_events"
        receipt["workflow"]["answer_kind"] = "ordered_customer_ids"
        receipt["expected_answer"] = ["cust_1", "cust_2"]
        receipt["answers"]["mode_a"] = ["cust_1", "cust_2"]
        receipt["answers"]["mode_b"] = ["cust_1", "cust_2"]
        receipt["accounts"]["expected"] = ["cust_1", "cust_2"]
        receipt["accounts"]["mode_a"] = ["cust_1", "cust_2"]
        receipt["accounts"]["mode_b"] = ["cust_1", "cust_2"]
        self.assertEqual(demo.receipt_problems(receipt), [])

    def test_controls_are_visible_in_receipt(self) -> None:
        result = demo.run_suite()
        self.assertEqual(
            result["controls"],
            ["proof_case", "receipt", "approval_queue", "fallback", "kill_switch"],
        )

    def test_every_result_has_a_log_entry(self) -> None:
        result = demo.run_suite()
        for item in result["results"]:
            self.assertEqual(item["logs"]["run_id"], item["run_id"])
            self.assertEqual(item["logs"]["case_id"], item["case_id"])
            self.assertIn("pilot_check", item["logs"])
            self.assertIn("access_level", item["logs"])
            self.assertIn("log_hash", item["logs"])

    def test_destructive_action_fails_closed(self) -> None:
        result = demo.run_suite()
        item = next(row for row in result["results"] if row["case_id"] == "destructive_action_case")
        self.assertEqual(item["permission"], "deny")
        self.assertTrue(item["kill_switch"])

    def test_pilot_regression_rolls_back_to_direct_path(self) -> None:
        result = demo.run_suite()
        item = next(row for row in result["results"] if row["case_id"] == "fallback_case")
        self.assertTrue(item["rollback"])
        self.assertEqual(item["fallback"], "direct_path")
        self.assertIn("eval_pass_rate", item["rollout"]["failures"])

    def test_bad_receipts_fail_the_pilot_check(self) -> None:
        variants = [
            "wrong_answer",
            "trace_drift",
            "missing_receipt",
            "cost_regression",
            "fallback_reason",
            "missing_container",
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                mutated = demo.mutate_receipt(self.receipt, variant)
                self.assertTrue(demo.receipt_problems(mutated))

    def test_missing_live_receipt_keeps_access_offline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            result = demo.run_suite(missing)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["pilot_check"], "fail")
        self.assertEqual(result["access_level"], "offline_only")
        self.assertTrue(result["receipt_problems"])

    def test_custom_receipt_path_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "programmatic_tool_calling_receipt.json"
            path.write_text(json.dumps(self.receipt), encoding="utf-8")
            result = demo.run_suite(path)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(Path(result["receipt_path"]), path)

    def test_summary_explains_the_gate(self) -> None:
        summary = demo.format_summary(demo.run_suite())
        self.assertIn("keyless, deterministic gate", summary)
        self.assertIn("What did not run: no Claude API call", summary)
        self.assertIn("Decision: PASS -> access_level=pilot_candidate", summary)
        self.assertIn("What this command tests", summary)
        self.assertIn("Receipt is real enough", summary)
        self.assertIn("direct_path is the baseline non-programmatic path", summary)
        self.assertIn("Stop cases covered", summary)


if __name__ == "__main__":
    unittest.main()
