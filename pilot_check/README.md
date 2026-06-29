# programmatic tool calling Pilot Check

Check the founder's own product workflow before it touches pilot customer traffic. The pilot check
consumes a programmatic tool calling receipt and asks whether that exact workflow has earned pilot
access: proof case, receipt, approval queue, fallback, and kill switch.

The checked-in receipt is only the keyless sample. It uses the customer-evidence fan-out workflow
from `claude-feature-hits`. A founder should replace it by running the same programmatic tool calling comparison on their
own narrow product tool.

## Value Bar

This stage is a candidate until it is adversarially-confirmed to add value for a real builder taking
a Claude workflow toward production. A passing pilot check proves the proof case, receipt, approval
queue, fallback, and kill switch are present. It does not prove production safety or default launch
readiness.

## Run It

```bash
make pilot-check
make pilot-check RECEIPT=/tmp/programmatic_tool_calling_receipt.json
make check
make test
```

No API key is required for the default sample. To check a founder's own workflow, first emit a live
receipt from the programmatic tool calling comparison:

```bash
cd ../takehome-experiments/claude-feature-hits
make programmatic_tool_calling RECEIPT_OUT=/tmp/programmatic_tool_calling_receipt.json
cd ../../claude-founder-kit
make pilot-check RECEIPT=/tmp/programmatic_tool_calling_receipt.json
```

## What It Covers

| Control | File | What the demo proves |
| --- | --- | --- |
| Proof case | `evals/template.jsonl` | The workflow passes same-answer, lower-cost, approval, fallback, and kill-switch cases |
| Receipt | `templates/programmatic_tool_calling_receipt.json` | The checked proof carries caller path, token buckets, source IDs, and trace gate |
| Approval queue | `templates/pilot_check_controls.json` | Read-only proof can run, outward actions ask, destructive actions are denied |
| Pilot health | `templates/pilot_check_controls.json` | Each run reports correctness, latency, fallback, policy, and cost signals |
| Fallback | `templates/access_levels.json` | Pilot regressions route back to the direct path |
| Kill switch | `templates/access_levels.json` | Wrong answers, trace drift, missing receipts, fallback reasons, and cost regressions stop launch |
| Tool contract | `templates/tool_contract_template.json` | The founder's tool says what it can read, what it returns, and what it must not do |

## The Pilot-Check Contract

Before a workflow earns pilot access, write these down:

1. The product workflow: what customer task Claude should improve.
2. The proof case: what fixture or trace catches a wrong answer.
3. The receipt: same direct and programmatic answer, lower billed input, and clean trace gate.
4. The approval queue: what can run, what asks, and what never runs.
5. The receipt fields: what audit handles are saved on every task.
6. The pilot health signals: what gets aggregated from receipts and traces.
7. The access path: offline, shadow, pilot, then default.
8. The fallback: where traffic goes when the pilot check fails.
9. The kill switch: which failures pause or stop rollout.

## Founder Access Ladder

| Step | Founder question | Artifact |
| --- | --- | --- |
| Build | What product workflow and narrow tool are we testing? | tool contract plus fixture |
| Test | What proof case catches a wrong answer or unsafe action? | same-answer, approval, fallback, and stop cases |
| Control | What gets approved, denied, checked, and sent to fallback? | `pilot_check_controls.json` and `access_levels.json` |
| Access | What evidence earns the next level? | offline, shadow, pilot, then default check |

Avoid broad tools, raw customer payloads in logs, default rollout without fallback, and access that
advances without a passing proof case, receipt, approval queue, fallback, owner, and kill switch.
