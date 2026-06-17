"""De-slop: deterministic linter for AI-slop in prose and rendered output.

Public API:
    lint_text(text)  -> list[finding]   prose tells
    lint_html(html)  -> list[finding]   visual AI-slop blacklist
    lint(text)       -> report dict      auto-detects HTML, scores both
    grade(score)     -> "A".."F"
    RULES                                the canonical ruleset (slop_rules.json)
"""
from .rules import RULES, lint, lint_html, lint_text, grade, load_config

__all__ = ["RULES", "lint", "lint_html", "lint_text", "grade", "load_config"]
