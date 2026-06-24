# Value Receipt: Internal Founder Simulation

Status: internal simulation, not external proof.

Date: 2026-06-24.

Reviewer role: skeptical internal founder-operator.

Workflow: seed-stage founder building LedgerOps AI, a Claude support copilot for finance teams.

Baseline: a rough pitch, a two-case happy-path eval set, and a first-draft MCP tool surface with search, ticket update, billing query, and refund tools.

Artifacts tested:

- [scenario.md](scenario.md)
- [pitch.md](pitch.md)
- [eval_baseline_weak.jsonl](eval_baseline_weak.jsonl)
- [eval_candidate_improved.jsonl](eval_candidate_improved.jsonl)
- [tools_baseline.json](tools_baseline.json)

## Commands Run

```bash
cd idea/validate
python -m startup_signal_lab.score ../../receipts/internal-founder-simulation-2026-06-24/pitch.md

cd ../../mvp/build
python eval_lint.py ../../receipts/internal-founder-simulation-2026-06-24/eval_baseline_weak.jsonl
python eval_lint.py ../../receipts/internal-founder-simulation-2026-06-24/eval_candidate_improved.jsonl

cd ../harden
python -m contract_doctor ../../receipts/internal-founder-simulation-2026-06-24/tools_baseline.json

cd ../../launch
python -m activation operate examples/readout.json --weekly --prev examples/prev_week_state.json

cd ../scale
python -m scale examples/cohort.json --json
```

`ANTHROPIC_API_KEY` was not set, so live Claude calls were not run. This receipt covers deterministic founder workflow gates only.

## Observed Results

| Area | Baseline | Kit result | Founder value indicated |
| --- | --- | --- | --- |
| Startup signal | Rough pitch only | `startup-signal - pitch: 7/10` | The pitch is viable enough to continue, but still needs review before a stronger claim |
| Evals | 2 happy-path cases | `69/100`, grade C, 0 honesty cases, 0 adversarial cases | The kit caught that the eval set would not catch hallucination or instruction override |
| Evals after repair | 8 cases with refusal and adversarial coverage | `97/100`, grade A, 2 honesty cases, 1 adversarial case | The kit gave a concrete bar for turning a demo eval set into a safer CI candidate |
| Tool contracts | First-draft MCP tools | `28/100`, grade F, 5 tools below bar | The kit caught raw secret exposure, destructive refund without safety contract, raw SQL passthrough, duplicate search tools, missing failure modes |
| Launch motion | Sample cohort readout | Biggest leak: `first_build -> second_build`, 38% lost. Motion: 72-hour second-build nudge to 3 accounts. 2 PQAs ready for handoff | The kit turned activation data into a specific operator action and kept outward actions gated |
| Scale motion | Sample cohort readout | 3 expansion-ready accounts, 5 deep moats, median moat 60 | The kit separated expansion-ready accounts from deep-moat accounts that should be retained before expansion |
| Cost evidence | Existing cost receipt | Context trimming and context editing both show 68% lower cost than naive on the saved receipt | Useful mechanical evidence, but not rerun here because no API key was present |

## Objections Tried

- The baseline eval set might look acceptable because both cases are gradeable. The eval gate rejected that by requiring honesty, adversarial coverage, and enough cases.
- The tool surface might look acceptable to a human because it has named tools. The contract gate rejected that because the model sees missing parameter docs, no failure modes, a raw secret, a destructive refund, and raw SQL.
- The launch and scale outputs might become generic advice. The deterministic reports named specific accounts, leaks, and gated actions.

## Decision

This run supports a narrow internal claim:

The kit found founder-relevant defects before live build work: weak eval coverage, unsafe tool contracts, and unclear launch or expansion motions.

This run does not support an external value claim:

No independent founder used the kit on their own workflow, no external reviewer had room to reject it, and no live Claude path was run in this shell.

## Follow-up

- Run the same receipt flow with a real founder artifact.
- Add the founder's baseline artifact and objection notes.
- Run the live paths with `ANTHROPIC_API_KEY` set.
- Keep this receipt labeled as internal until an outside user supplies the external receipt.
