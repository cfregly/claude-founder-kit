"""claude-startup-launch: produce the founder-to-builder weekly report.

One repo, one deliverable. The weekly startup-signal report is the artifact the
growth role ships every Monday, and producing it end to end runs a single
pipeline (capture -> measure -> enrich -> decide -> draft -> gate -> remember ->
render) that exercises the Claude Developer Platform and the Agent SDK at the
step where each is genuinely the right tool.

The core is stdlib only and deterministic, so `make demo` produces the report
offline with no key. Every Claude and cloud layer is optional and degrades to the
deterministic path when a key is absent.
"""

__version__ = "0.1.0"
