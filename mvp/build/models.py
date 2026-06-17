"""The consequence ladder: the one place model ids live.

Route by consequence. The cost of being wrong rises with the rung, so the more
capable, more expensive model earns the higher-stakes work. Every act and the
forkable starter pick a rung by name, so a model id changes here once, not in
five files.

The rungs are the eval tiers in 03_evals.py and the routing in
04_cost_engineering.py:

    JUNIOR         lookups, where it is cheap to be wrong
    SENIOR         the workhorse for real synthesis
    PRINCIPAL      high-consequence, irreversible work
    DISTINGUISHED  the adversarial edge (access-gated)

Model ids move fast. Pin a dated snapshot in production, and list what a key can
reach with:

    python -c "import anthropic; print([m.id for m in anthropic.Anthropic().models.list().data])"
"""

JUNIOR = "claude-haiku-4-5"
SENIOR = "claude-sonnet-4-6"
PRINCIPAL = "claude-opus-4-8"
DISTINGUISHED = "claude-fable-5"
