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
    def test_pin_is_valid(self) -> None:
        pin = tune_tools.load_pin()
        self.assertEqual(40, len(pin["pinned_commit"]))
        self.assertIn(pin["pinned_commit"], pin["receipt_url"])
        self.assertIn(pin["receipt_path"], pin["receipt_url"])

    def test_render_points_to_companion_workflow(self) -> None:
        pin = tune_tools.load_pin()
        rendered = tune_tools.render(pin)
        self.assertIn("claude-agent-harness-optimization", rendered)
        self.assertIn("optimize-tools", rendered)
        self.assertIn("model-matrix", rendered)
        self.assertIn("grind-harness", rendered)
        self.assertIn(pin["pinned_commit"], rendered)

    def test_no_companion_implementation_is_vendored(self) -> None:
        for directory in ("claude_agent_harness_optimization", "evals", "recipes"):
            self.assertFalse((ROOT / directory).exists(), directory)


if __name__ == "__main__":
    unittest.main()
