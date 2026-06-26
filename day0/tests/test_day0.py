from __future__ import annotations

import unittest

import demo


class Day0TrustTests(unittest.TestCase):
    def test_suite_passes_all_fixture_evals(self) -> None:
        receipt = demo.run_suite()
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["evals"]["passed"], receipt["evals"]["total"])

    def test_controls_are_visible_in_receipt(self) -> None:
        receipt = demo.run_suite()
        self.assertEqual(
            receipt["controls"],
            ["evals", "permissions", "logs", "monitoring", "rollback", "stopping_conditions"],
        )

    def test_every_result_has_a_log_entry(self) -> None:
        receipt = demo.run_suite()
        for result in receipt["results"]:
            self.assertEqual(result["logs"]["run_id"], result["run_id"])
            self.assertEqual(result["logs"]["case_id"], result["case_id"])
            self.assertTrue(result["logs"]["trace_present"])
            self.assertIn("log_hash", result["logs"])

    def test_destructive_action_fails_closed(self) -> None:
        receipt = demo.run_suite()
        result = next(item for item in receipt["results"] if item["case_id"] == "permission_deny_case")
        self.assertEqual(result["permission"], "deny")
        self.assertTrue(result["stopping_condition"])

    def test_canary_regression_rolls_back(self) -> None:
        receipt = demo.run_suite()
        result = next(item for item in receipt["results"] if item["case_id"] == "rollback_case")
        self.assertTrue(result["rollback"])
        self.assertEqual(result["fallback"], "direct_path")
        self.assertIn("eval_pass_rate", result["rollout"]["failures"])

    def test_offline_regression_stops_before_rollout(self) -> None:
        receipt = demo.run_suite()
        result = next(item for item in receipt["results"] if item["case_id"] == "stop_case")
        self.assertEqual(result["rollout"]["decision"], "stop")
        self.assertTrue(result["stopping_condition"])


if __name__ == "__main__":
    unittest.main()
