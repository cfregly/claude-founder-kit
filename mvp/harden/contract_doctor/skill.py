"""Lint a SKILL.md: is the skill discoverable and progressively disclosed?

    python -m contract_doctor.skill path/to/SKILL.md [--min-score 80]

Skills are a first-class surface, the way DeepAgents and Claude Code treat them.
A skill is three layers: a `description` that is ALWAYS in context and decides
when to load the skill, a body loaded on demand when it triggers, and references
for the deep detail pulled in only when needed. That is progressive disclosure.
A skill fails when the description does not trigger it, or when the whole thing is
one giant always-loaded prompt. This grades a SKILL.md on those terms.

Rules:
  SK001 (error) no description in frontmatter. The model has nothing to trigger on.
  SK002 (warn)  description too long (always-loaded context) or too short (vague).
  SK003 (warn)  description gives no trigger guidance ("use when", "triggers on").
  SK004 (warn)  a large body with no references: it all loads on trigger instead
                of pointing the deep detail to files (progressive disclosure).
  SK005 (info)  no guardrails ("what not to do"): skills drift without explicit don'ts.
  SK006 (info)  name missing or not kebab-case.
  SK007 (warn)  the body has no workflow structure. A skill is a procedure, not an essay.

Severities: error (-15), warn (-8), info (-3). Starts at 100, floor 0. Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEDUCTION = {"error": 15, "warn": 8, "info": 3}


def _f(rule, severity, message, fix):
    return {"rule": rule, "severity": severity, "message": message, "fix": fix}


def _parse(text: str) -> tuple[dict, str]:
    """Pull name/description from YAML frontmatter (folded blocks included) and
    return (frontmatter, body). No YAML dependency: parse the few keys we grade."""
    fm: dict = {}
    body = text
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            raw_fm, body = parts[1], parts[2]
            lines = raw_fm.splitlines()
            i = 0
            while i < len(lines):
                m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", lines[i])
                if not m:
                    i += 1
                    continue
                key, val = m.group(1), m.group(2).strip()
                if val in (">", ">-", "|", "|-", ""):
                    block, i = [], i + 1
                    while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                        if lines[i].strip():
                            block.append(lines[i].strip())
                        i += 1
                    fm[key] = " ".join(block)
                    continue
                fm[key] = val
                i += 1
    return fm, body


def lint_skill(text: str) -> dict:
    fm, body = _parse(text)
    findings: list[dict] = []
    add = findings.append
    name = fm.get("name", "")
    desc = fm.get("description", "")
    body_lines = body.strip().splitlines()

    # SK001 / SK002 / SK003 -- the description is the trigger.
    if not desc:
        add(_f("SK001", "error",
               "no description in frontmatter: the model has nothing to decide when "
               "to load this skill",
               "Add a description. It is always in context, so it is what triggers "
               "the skill. Name the job and the situations it fires in."))
    else:
        if len(desc) > 1200:
            add(_f("SK002", "warn",
                   f"description is {len(desc)} chars: it is always-loaded context, so "
                   "an essay here costs every turn",
                   "Tighten the description to the job plus its triggers. Push the "
                   "how-to into the body, which loads only when the skill fires."))
        elif len(desc) < 40:
            add(_f("SK002", "warn",
                   f"description is {len(desc)} chars: too thin to trigger reliably",
                   "Say what the skill does and when to use it. A vague description "
                   "either never fires or fires on the wrong turn."))
        if not re.search(r"use when|use this|triggers? on|when the user|when someone|when a\b",
                         desc, re.I):
            add(_f("SK003", "warn",
                   "the description gives no trigger guidance",
                   "State when to use it: 'Use when ...', 'Triggers on ...'. Triggering "
                   "left to chance is a skill the model never reaches for."))

    # SK006 name convention.
    if not name:
        add(_f("SK006", "info", "no name in frontmatter",
               "Add a kebab-case name. It is the handle the skill is invoked by."))
    elif not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        add(_f("SK006", "info", f"name '{name}' is not kebab-case",
               "Use lowercase-with-hyphens, e.g. 'pitch-deck'. It is a handle, not a title."))

    # SK004 progressive disclosure: a large body that all loads on trigger.
    has_refs = bool(re.search(
        r"\]\([^)\s]+\.(?:md|py|json|txt|js|mjs|ya?ml)\)|\bsee\b[^.]{0,40}\b(?:file|reference|doc|template)|\breferences?\b\s*:",
        body, re.I))
    if len(body_lines) > 250 and not has_refs:
        add(_f("SK004", "warn",
               f"the body is {len(body_lines)} lines with no references: it all loads "
               "when the skill triggers",
               "Keep the body to the workflow and point the deep detail at referenced "
               "files. Progressive disclosure: description always, body on trigger, "
               "files on demand."))

    # SK007 structure: a skill is a procedure.
    has_structure = ("##" in body) or bool(re.search(r"^\s*(?:\d+\.|[-*]\s)", body, re.M))
    if body_lines and not has_structure:
        add(_f("SK007", "warn",
               "the body has no workflow structure (no sections or steps)",
               "Shape it as a procedure: numbered steps or sections the model follows. "
               "A wall of prose is read once and applied unevenly."))

    # SK005 guardrails.
    if not re.search(r"what not to do|\bnever\b|\bdo not\b|\bdon'?t\b|\bavoid\b", body, re.I):
        add(_f("SK005", "info",
               "no guardrails: nothing says what the skill must not do",
               "Add a 'What NOT to do' section. The don'ts are where a skill drifts."))

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
    ap = argparse.ArgumentParser(prog="contract_doctor.skill", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill", help="path to a SKILL.md")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--min-score", type=int, default=80)
    args = ap.parse_args(argv)

    r = lint_skill(Path(args.skill).read_text())
    if args.as_json:
        import json
        print(json.dumps(r, indent=2))
    else:
        print(f"skill - {args.skill}: {r['score']}/100 (grade {r['grade']})\n")
        for x in r["findings"]:
            print(f"[{x['rule']} {SEV[x['severity']]} {x['severity']}] {x['message']}")
            print(f"    fix: {x['fix']}")
        if not r["findings"]:
            print("clean - a skill the model can find and disclose progressively")
    if r["score"] < args.min_score:
        print(f"\nFAIL: {r['score']} < --min-score {args.min_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
