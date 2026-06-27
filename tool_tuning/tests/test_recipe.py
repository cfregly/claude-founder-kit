#!/usr/bin/env python3
"""Tests for the tool tuning recipe."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tune_tools  # noqa: E402


class ToolTuningRecipeTest(unittest.TestCase):
    def test_registry_entry_is_valid(self) -> None:
        entry = tune_tools.load_entry()
        self.assertEqual("tool-tuning", entry["id"])
        self.assertEqual(40, len(entry["commit"]))
        self.assertIn(entry["commit"], entry["ledger_url"])
        self.assertIn(entry["ledger"], entry["ledger_url"])

    def test_render_points_to_companion_workflow(self) -> None:
        entry = tune_tools.load_entry()
        rendered = tune_tools.render(entry)
        self.assertIn("claude-agent-harness-optimization", rendered)
        self.assertIn("optimize-tools", rendered)
        self.assertIn("model-matrix", rendered)
        self.assertIn("grind-harness", rendered)
        self.assertIn("tool_tuning_before_bundle.json", rendered)
        self.assertIn("agent_audit_bundle.json", rendered)
        self.assertIn("name, use_when, avoid_when", rendered)
        self.assertIn(entry["commit"], rendered)
        self.assertIn(entry["tag"], rendered)

    def test_no_companion_implementation_is_vendored(self) -> None:
        for directory in ("claude_agent_harness_optimization", "evals", "recipes"):
            self.assertFalse((ROOT / directory).exists(), directory)
        self.assertFalse((ROOT / "receipt_pin.json").exists())


if __name__ == "__main__":
    unittest.main()
