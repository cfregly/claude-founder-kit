"""Produce the founder-to-builder weekly report.

One repo, one deliverable. The weekly startup-signal report is the artifact the
growth role ships every Monday, and producing it end to end runs a single
pipeline (capture -> measure -> enrich -> decide -> draft -> gate -> remember ->
render) that exercises the Claude Developer Platform and the Agent SDK at the
step where each is genuinely the right tool.

The deterministic core (capture, measure, the gate, the report template) is stdlib only and
carries the receipt, so the gates run offline. The generative stages (enrich, decide, draft) run
Claude on every run and raise a clear error without a key, so `make demo` needs ANTHROPIC_API_KEY
and fails fast rather than degrading.
"""

__version__ = "0.1.0"
