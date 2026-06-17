"""Grade an agent harness, not just its tools.

    python -m contract_doctor.harness manifest.json [--min-score 70]

The agent linter scores tool CONTRACTS. This scores the HARNESS: the architecture
a startup wires Claude into. Most agents that fail in production do not fail on a
bad prompt, they fail on harness design, the way a four-tool MCP surface makes the
agent bypass it. The dimensions here are the ones the well-architected open
harnesses converged on (LangChain DeepAgents, LangGraph, Claude Code, Cursor):
decomposition into subagents, a structured return contract so a subagent talks to
its parent and its parallel siblings, async sibling execution, context isolation
and offload, conversation compaction (model-controlled and selective, because even
a 1M window runs out on a long agentic loop), memory (episodic, procedural,
semantic), skills as first-class with progressive disclosure, and a gate on
outward actions.

Input is a harness manifest (JSON), the architecture described as data:

    {
      "name": "research-agent",
      "task": "long-running",                 # one-shot | multi-step | long-running
      "subagents": [
        {"name": "searcher", "returns": "structured", "parallel": true,
         "context": "isolated"}
      ],
      "context": {
        "compaction": "model-controlled",      # none | threshold | model-controlled
        "compaction_scope": "selective",       # all | selective (control WHAT is kept)
        "offload": "filesystem",               # none | filesystem
        "caching": true,                       # cache the stable prefix
        "durable": true,                       # checkpoint so a long run resumes
        "window": "1M"
      },
      "memory": ["episodic", "procedural"],    # episodic | procedural | semantic
      "skills": [{"name": "deslop", "disclosure": "progressive"}],
      "governance": {"gates_outward_actions": true}
    }

Severities: error (-15), warn (-8), info (-3). The harness starts at 100, floor 0.
Deterministic, so the same manifest grades the same every run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEDUCTION = {"error": 15, "warn": 8, "info": 3}
MEMORY_KINDS = {"episodic", "procedural", "semantic"}


def _f(rule, severity, message, fix):
    return {"rule": rule, "severity": severity, "message": message, "fix": fix}


def lint_harness(m: dict) -> dict:
    findings: list[dict] = []
    add = findings.append

    task = (m.get("task") or "multi-step").lower()
    subs = m.get("subagents") or []
    ctx = m.get("context") or {}
    mem = set(m.get("memory") or [])
    skills = m.get("skills") or []
    gov = m.get("governance") or {}
    complex_task = task in ("multi-step", "long-running")

    # HA001 decomposition: a complex agent that is one monolithic loop carries
    # every step's context in one window. Decompose into subagents with isolated
    # context (the DeepAgents pillar; the "isolate" strategy of context eng).
    if complex_task and not subs:
        add(_f("HA001", "error",
               f"a {task} agent with no subagents: one monolithic loop holds every "
               "step's context in a single window",
               "Decompose into subagents with isolated context. A researcher, a "
               "writer, a verifier each carry only their slice, so the main thread "
               "stays small and each subtask is independently testable."))

    # HA002 return contract: a subagent that returns free-form text cannot be
    # reliably consumed by its parent or a parallel sibling. The return IS the
    # interface between agents.
    text_returns = [s.get("name", "<sub>") for s in subs
                    if (s.get("returns") or "text").lower() == "text"]
    if text_returns:
        shown = ", ".join(text_returns[:3]) + (" ..." if len(text_returns) > 3 else "")
        add(_f("HA002", "error",
               f"subagent(s) return free-form text ({shown}): the parent and "
               "parallel siblings cannot reliably consume the result",
               "Give each subagent a structured return (a schema). The return is "
               "the contract between agents, the same discipline a tool description "
               "is. Free-form text forces the caller to re-parse and guess."))

    # HA003 parallelism: independent subagents run one after another waste wall
    # clock. Run independent siblings concurrently (async).
    if len(subs) >= 2 and not any((s.get("parallel") is True) for s in subs):
        add(_f("HA003", "warn",
               f"{len(subs)} subagents, none marked parallel: independent work runs "
               "sequentially and wastes wall-clock",
               "Run independent siblings concurrently. Fan out the searchers, await "
               "all, then synthesize. Wall-clock becomes the slowest single subagent, "
               "not the sum."))

    # HA004 context isolation: subagents on a shared context defeat the point of
    # spawning them; large results kept inline bloat the window.
    shared = [s.get("name", "<sub>") for s in subs
              if (s.get("context") or "isolated").lower() == "shared"]
    if shared:
        add(_f("HA004", "warn",
               f"subagent(s) share the main context ({', '.join(shared[:3])}): "
               "spawning them no longer isolates context",
               "Give each subagent its own context window. Isolation is why a "
               "subagent helps: the main thread never sees the subtask's noise, "
               "only its structured result."))
    if subs and (ctx.get("offload") or "none").lower() == "none":
        add(_f("HA004", "info",
               "no filesystem offload: large tool results stay in the window",
               "Offload large results (a file dump, a long page) to a filesystem or "
               "scratchpad and pass a handle. The window holds the reference, not "
               "the payload."))

    # HA005 compaction: a long-running agent with no compaction exhausts even a 1M
    # window on a long loop. Threshold-only compaction is blunt; the model should
    # be able to compact on its own judgment and control WHAT is kept.
    compaction = (ctx.get("compaction") or "none").lower()
    window = str(ctx.get("window") or "")
    if task == "long-running" and compaction == "none":
        add(_f("HA005", "error",
               "a long-running agent with no compaction: even a 1M window fills on a "
               "long agentic loop, then the agent degrades or stalls",
               "Add compaction: summarize the conversation, preserve the decisions, "
               "open questions, and key facts, discard the redundant turns. A bigger "
               "window buys time, it does not remove the need."))
    elif complex_task and compaction == "threshold":
        add(_f("HA005", "warn",
               "compaction fires only at a fixed threshold: the model cannot compact "
               "when IT judges the context has gone stale",
               "Expose a compaction tool the model can call on its own judgment, not "
               "only at a byte threshold, and let it choose what to keep. The model "
               "knows which turns stopped mattering before the threshold does."))
    if compaction in ("threshold", "model-controlled") and \
            (ctx.get("compaction_scope") or "all").lower() == "all":
        add(_f("HA005", "info",
               "compaction summarizes everything uniformly: it cannot keep the "
               "architectural decisions verbatim while compressing the chatter",
               "Make compaction selective: keep decisions, constraints, and open "
               "questions in full, compress the rest. A hot / warm / cold tier "
               "(recent verbatim, mid rolling summary, old broad summary) is the "
               "common shape."))

    # HA006 memory: no persistent memory means nothing survives the context
    # window. Episodic (what happened) and procedural (the rules/playbooks) are
    # the load-bearing pair; semantic (facts) is the third. A one-shot agent is
    # stateless by design and has nothing to carry between runs, so the absence
    # of memory is only a finding for a complex (multi-step or long-running)
    # agent, where continuity across windows is what makes memory load-bearing.
    # Penalizing a one-shot for "no memory" pushes a founder to over-engineer.
    if not mem:
        if complex_task:
            add(_f("HA006", "warn",
                   "no persistent memory: nothing survives the run, so the agent relearns "
                   "the project every session",
                   "Add memory. Episodic (structured summaries of past runs, decisions, "
                   "outcomes) gives continuity across windows; procedural (rules, "
                   "playbooks, business logic) steers behavior; semantic (facts) grounds "
                   "it. Retrieve the relevant slice, do not reload all of it."))
    else:
        missing = MEMORY_KINDS - mem
        if "episodic" in missing or "procedural" in missing:
            add(_f("HA006", "info",
                   f"memory has {sorted(mem)} but not {sorted(missing & {'episodic', 'procedural'})}",
                   "Episodic and procedural are the load-bearing pair: what happened, "
                   "and the rules that should repeat. Add the missing one."))
        bad = mem - MEMORY_KINDS
        if bad:
            add(_f("HA006", "info", f"unknown memory kind(s): {sorted(bad)}",
                   "Use episodic, procedural, or semantic. Naming the kind makes the "
                   "retrieval and write policy explicit."))

    # HA007 skills as first-class with progressive disclosure: an inlined skill is
    # always-loaded context and triggers poorly. A skill should be a short
    # description that triggers it, a body loaded on demand, and references for the
    # deep detail (the Claude / DeepAgents skill shape).
    inlined = [s.get("name", "<skill>") for s in skills
               if (s.get("disclosure") or "").lower() == "inlined"]
    if inlined:
        add(_f("HA007", "warn",
               f"skill(s) inlined into the system prompt ({', '.join(inlined[:3])}): "
               "always-loaded context that also triggers poorly",
               "Make skills progressive: a short description that decides when to "
               "load it, a body pulled in on demand, references for the deep detail. "
               "The model loads the skill only when the task calls for it."))

    # HA008 governance: outward or irreversible actions that are not gated turn a
    # harness into expensive noise sent in the founder's name.
    gated = gov.get("gates_outward_actions")
    if gated is False:
        add(_f("HA008", "error",
               "outward actions are explicitly not gated: the harness can email, "
               "spend, or post on its own",
               "Gate every outward or irreversible action behind a human approval "
               "(or refuse it by design). Measure and draft unattended; act only on "
               "approval. Autonomy without a gate is the failure mode that loses "
               "trust the first time it ships noise."))
    elif gated is None and complex_task:
        add(_f("HA008", "info",
               "no stated gate on outward actions: the policy is undecided",
               "Declare whether outward or irreversible actions are gated. Unstated "
               "means nobody chose, which is how a loop ends up acting unattended."))

    # HA009 prompt caching: a stable, large prefix (system prompt, skills, memory)
    # re-sent uncached on every call pays full input price each turn. Caching the
    # stable prefix is the cheapest context-engineering win and the one DeepAgents
    # bakes into its middleware.
    if complex_task and ctx.get("caching") is not True:
        add(_f("HA009", "warn",
               "no prompt caching on the stable prefix: the system prompt, skills, "
               "and memory re-send at full input price every turn",
               "Cache the stable prefix. It changes what evals and support can "
               "afford, not just the bill. Stable context never resends at full "
               "price, and the cache read is a fraction of the write."))

    # HA010 durability: a long-running agent with no checkpoint loses everything on
    # a crash, a deploy, or a timeout. LangGraph makes checkpointing the default
    # for exactly this reason.
    if task == "long-running" and ctx.get("durable") is not True:
        add(_f("HA010", "warn",
               "a long-running agent with no checkpointing: a crash, deploy, or "
               "timeout loses the whole run",
               "Persist state at each step so the run resumes where it stopped. A "
               "long agent that cannot resume is a long agent you rerun from zero."))

    score = max(0, 100 - sum(DEDUCTION[x["severity"]] for x in findings))
    return {"score": score, "grade": grade(score), "findings": findings}


def grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


SEV = {"error": "✗", "warn": "!", "info": "·"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="contract_doctor.harness", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", help="harness manifest JSON")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--min-score", type=int, default=70)
    args = ap.parse_args(argv)

    m = json.loads(Path(args.manifest).read_text())
    r = lint_harness(m)
    if args.as_json:
        print(json.dumps(r, indent=2))
    else:
        name = m.get("name", args.manifest)
        print(f"harness - {name}: {r['score']}/100 (grade {r['grade']})\n")
        for x in r["findings"]:
            print(f"[{x['rule']} {SEV[x['severity']]} {x['severity']}] {x['message']}")
            print(f"    fix: {x['fix']}")
        if not r["findings"]:
            print("clean - a harness Claude can run, not just a prompt")
    if r["score"] < args.min_score:
        print(f"\nFAIL: {r['score']} < --min-score {args.min_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
