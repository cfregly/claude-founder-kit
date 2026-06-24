# Value Receipt: Internal Founder Simulation

Status: internal simulation with live Claude calls, not external proof.

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
python -m startup_signal_lab.intervene ../../receipts/internal-founder-simulation-2026-06-24/pitch.md

cd ../../mvp/build
python eval_lint.py ../../receipts/internal-founder-simulation-2026-06-24/eval_baseline_weak.jsonl
python eval_lint.py ../../receipts/internal-founder-simulation-2026-06-24/eval_candidate_improved.jsonl
python 03_evals.py
python 04_cost_engineering.py

cd ../harden
python -m contract_doctor ../../receipts/internal-founder-simulation-2026-06-24/tools_baseline.json

cd ../../launch
python -m activation operate examples/readout.json --weekly --prev examples/prev_week_state.json
make demo

cd ../scale
python -m scale examples/cohort.json --json
python -m scale examples/cohort.json
```

`ANTHROPIC_API_KEY` was loaded from the local `.env` copied into this repo for execution. The file is git-ignored and was not staged.

Live outputs captured in this receipt folder:

- [live_idea_intervention.txt](live_idea_intervention.txt)
- [live_mvp_eval.txt](live_mvp_eval.txt)
- [live_mvp_cost.txt](live_mvp_cost.txt)
- [live_launch_demo.txt](live_launch_demo.txt)
- [live_scale_readout.txt](live_scale_readout.txt)

## Observed Results

| Area | Baseline | Kit result | Founder value indicated |
| --- | --- | --- | --- |
| Startup signal | Rough pitch only | `startup-signal - pitch: 7/10` | The pitch is viable enough to continue, but still needs review before a stronger claim |
| Evals | 2 happy-path cases | `69/100`, grade C, 0 honesty cases, 0 adversarial cases | The kit caught that the eval set would not catch hallucination or instruction override |
| Evals after repair | 8 cases with refusal and adversarial coverage | `97/100`, grade A, 2 honesty cases, 1 adversarial case | The kit gave a concrete bar for turning a demo eval set into a safer CI candidate |
| Tool contracts | First-draft MCP tools | `28/100`, grade F, 5 tools below bar | The kit caught raw secret exposure, destructive refund without safety contract, raw SQL passthrough, duplicate search tools, missing failure modes |
| Launch motion | Sample cohort readout | Biggest leak: `first_build -> second_build`, 38% lost. Motion: 72-hour second-build nudge to 3 accounts. 2 PQAs ready for handoff | The kit turned activation data into a specific operator action and kept outward actions gated |
| Scale motion | Sample cohort readout | 3 expansion-ready accounts, 5 deep moats, median moat 60 | The kit separated expansion-ready accounts from deep-moat accounts that should be retained before expansion |
| Live idea intervention | Rough LedgerOps AI pitch | Claude narrowed the wedge to refund triage for usage-based SaaS finance teams and named the missing proof: baseline handle time, senior-review rate, activation rate, hallucination rate, citation coverage, and second-workflow rate | Useful founder pressure because it converted broad category language into a smaller 30-day proof loop |
| Live MVP eval | Routed eval harness | 7/7 available cases passed. Fable tier was unavailable with this key and skipped, not graded | Useful mechanical evidence that the available tiers can run live, with a visible access gap instead of a fake pass |
| Live cost run | Same 12-question workload, three execution strategies | Naive Sonnet cost `$0.2191`. Cached Sonnet cost `$0.0559`, down 74%. Routed plus cached cost `$0.0314`, down 86% | Strong mechanical evidence that prompt caching and routing reduce cost on this workload |
| Live launch demo | Sample fictional founder cohort | Selected the second-build nudge as the one motion and gated email or GTM actions for approval | Useful operator guardrail, but the enrichment step could not identify fictional account IDs and returned no public signal |
| Live scale readout | Sample fictional account cohort | 3 GTM-ready accounts, 5 deep-moat accounts, median moat 60, and a targeted expansion plus reference play | Useful sample workflow evidence, not customer proof |

## Objections Tried

- The baseline eval set might look acceptable because both cases are gradeable. The eval gate rejected that by requiring honesty, adversarial coverage, and enough cases.
- The tool surface might look acceptable to a human because it has named tools. The contract gate rejected that because the model sees missing parameter docs, no failure modes, a raw secret, a destructive refund, and raw SQL.
- The launch and scale outputs might become generic advice. The deterministic reports named specific accounts, leaks, and gated actions.
- The live launch enrichment might imply the system can research account IDs. The run disproved that for fictional IDs and kept the output at "no public signal found."
- The live eval might imply the full model matrix passed. It did not. The Fable tier was skipped because this key lacks access.

## Decision

This run supports a narrow internal claim:

The kit found founder-relevant defects and live operating pressure before external build work: weak eval coverage, unsafe tool contracts, a too-broad wedge, missing before/after metrics, unclear launch motions, and unclear expansion motions.

This run does not support an external value claim:

No independent founder used the kit on their own workflow, no external reviewer had room to reject it, and the launch and scale runs used sample fictional data.

## Follow-up

- Run the same receipt flow with a real founder artifact.
- Add the founder's baseline artifact and objection notes.
- Keep this receipt labeled as internal until an outside user supplies the external receipt.
