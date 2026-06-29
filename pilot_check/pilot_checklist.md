# Pilot-check programmatic tool calling Pilot Checklist

Use this before a Claude workflow in your product touches customer data or takes an outward action.

- Product workflow: name the customer task, the tool boundary, the data touched, and the action risk.
- Proof case: at least one same-answer case, one approval case, one deny case, one fallback case, and
  one stopping condition.
- Receipt: save the command, workload name, tool name, expected answer, direct answer, programmatic
  answer, token counts, trace gate, fallback state, and cost scope.
- Approval queue: name what always runs, what asks first, and what never runs.
- Logs: save run id, actor, intent, permission, pilot check, access level, fallback, receipt source,
  trace status, and a log hash. Do not log API keys, raw secrets, or unnecessary customer payloads.
- Monitoring: aggregate correctness, latency, fallback rate, policy denials, tool errors, missing
  traces, missing receipts, missing logs, and cost per successful task.
- Fallback: keep a direct path or manual path ready before pilot traffic starts.
- Kill switch: stop or slow on wrong answers, schema drift, caller-path drift, missing container,
  fallback reason, policy drift, fallback spikes, latency regression, cost regression, or missing
  receipts.
- Access ladder: offline first, shadow only after proof cases pass, pilot only with logs and controls,
  default only with fallback, monitoring, owner, and kill switch.

Avoid broad tools, raw customer payloads in logs, unsupported caller paths, unowned alerts, and
default access before the workflow, proof case, receipt, approval queue, fallback, and kill switch all
pass.

This checklist is a candidate until it is adversarially-confirmed to add value on a real workflow.
