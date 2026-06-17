"""Deterministic variant assignment: the CASH copy-and-UI-tweak analog.

CASH (Claude Accelerates Sustainable Hypergrowth) is the public name for the
pattern where Claude ships a growth experiment, mostly copy and UI tweaks, and
measures the win, with a human gate on what ships (Lenny's Podcast, "Anthropic
$1B to $19B growth run", 2026-04-05). The public fact is the pattern, not the
vendor: propose an experiment, ship a variant, measure the win, iterate.

This assigns a stable arm per org with a hash, so the same org always sees the
same arm and the funnel splits cleanly. No network and no platform in the core.
"""

import hashlib


def variant(org_id, experiment, arms=("control", "treatment")):
    """A stable arm for this org and experiment. Same inputs, same arm, always."""
    h = hashlib.sha256(f"{experiment}:{org_id}".encode()).hexdigest()
    return arms[int(h, 16) % len(arms)]
