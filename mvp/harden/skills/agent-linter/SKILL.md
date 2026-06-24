---
name: agent-linter
description: >-
  Harden an agent's tools and protocol with Claude. Lint MCP tool definitions
  into contract-grade interfaces, scored against 16 rules including an
  OWASP/STRIDE security lens (secrets, destructive ops, injection) and a
  tool-discovery check (a raw-query escape hatch that makes the agent bypass the
  surface). The rule score is a deterministic gate, and with a key Claude
  rewrites the worst tool and the same rules re-score it. Also check an
  agent protocol for the always-do / ask-first / never-do boundaries, and grade
  the harness architecture (subagent decomposition, structured return contracts,
  async siblings, context compaction, memory, skills, gating) against the
  DeepAgents, LangGraph, and Claude Code patterns. Use when someone wants to lint
  MCP tools, harden an agent, review tool descriptions, gate tool quality in CI,
  write an agent operating protocol, or review an agent architecture or harness.
  Triggers on "lint my MCP tools", "harden my agent", "tool descriptions", "is my
  agent safe", "agent protocol", "review my agent architecture", "harness review",
  "subagents", "context compaction", "agent memory", or
  "always ask-first never".
---

# agent-linter

Value bar: this skill is a candidate until it is adversarially-confirmed to add value against a baseline tool-contract or agent-security review. If that receipt is missing, call the output mechanically vetted only.

A founder runs this at the MVP stage of a founder workflow kit for Claude builders, the
security review before any user touches the agent. It turns vague MCP tools into
contract-grade interfaces and grades the agent protocol and harness, with an
OWASP and STRIDE security lens. The rule score is a deterministic gate
that runs offline and reproduces in CI. Built on the Claude Developer Platform:
with a key, claude-opus-4-8 rewrites the worst tool and the same rules re-score
it. Claude does the judgment, the gate proves it.

Most agent bugs are vague tool semantics, not model failures. A tool
description is an API contract: the model is the caller and cannot read your
source. This skill scores the contract with deterministic rules and gates it.
With a key, Claude rewrites the worst offender, the rewrite the rules can name
but cannot write, and the same rules re-lint it.

## Workflow

### 1. Get the tools on the wire
Dump the MCP server's `tools/list` response to JSON, or point the linter at a
FastMCP server file. The linter reads the wire format, so it grades what the
model actually receives, in any language.

### 2. Lint and read the findings
`python -m contract_doctor your_tools.json`. Each tool starts at 100. The rules
catch thin descriptions, generic names, undocumented params and returns,
missing failure modes, undeclared mutations, overlap, and the security slice: a
raw secret as a model-visible argument, a destructive op with no safety
contract, and free-form input into a code, shell, SQL, or URL sink.

### 3. Fix, then gate
Fix every error, justify every surviving warning. Gate it in CI:
`python -m contract_doctor your_tools.json --min-score 80 || exit 1`.

### 4. The judge loop
With a key set, Claude rewrites the worst tool from its findings on every lint,
and the same rules re-score the rewrite. With no key the rewrite is skipped and
the score is identical, so the gate reproduces offline. Claude writes the
contract the rules could name but not write, and the rules keep the score
honest, never moving because Claude ran. Pass `--no-judge` for a
deterministic-only run.

### 5. Write the agent protocol
For the agent itself, declare boundaries the way the AGENTS.md convention does:
group instructions into always-do, ask-first, and never-do, and add a failure
plan and a success metric. An agent with no stated boundaries acts on a guess.

### 6. Grade the harness
Describe the architecture as a manifest (subagents and their return contracts,
async siblings, context compaction, memory, skills, gating) and grade it:
`python -m contract_doctor.harness manifest.json`. The rules encode the patterns
the well-architected open harnesses converged on (DeepAgents, LangGraph, Claude
Code): decompose into subagents with isolated context, give each a structured
return so it talks to its parent and siblings, run independent siblings async,
compact selectively under the model's own judgment (a 1M window still fills on a
long loop), keep episodic and procedural memory, make skills progressive, and
gate every outward action.

## What NOT to do
- Never lint the source docstring instead of the published schema. Only the
  wire contract reaches the model.
- Never pass a secret through the model to satisfy a tool signature.
- Never ship a destructive tool without a stated reversibility or confirm path.
