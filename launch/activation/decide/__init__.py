"""Step 4, decide: choose the one motion against the biggest leak.

This step runs Claude every run: a single judgment call that uses adaptive
thinking at high effort and asks the advisor tool for a second opinion, returning
the decision as structured output. The gate ledger already carries a deterministic
pick, so this is pure judgment. With no key or no SDK it raises a clear error. It
never touches the gate: the model recommends, the human approves.
"""
