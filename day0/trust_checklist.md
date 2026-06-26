# Day-0 Trust Checklist

Use this before a Claude workflow touches customer data or takes an outward action.

- Workload: name the customer task, the tool boundary, the data touched, and the action risk.
- Evals: at least one win case, one honesty case, one permission case, one rollback case, and one
  stopping condition.
- Permissions: name what always runs, what asks first, and what never runs.
- Logs: save run id, actor, intent, permission, rollout decision, fallback, source ids, trace status,
  and a log hash. Do not log API keys, raw secrets, or unnecessary customer payloads.
- Monitoring: aggregate correctness, latency, fallback rate, policy denials, tool errors, missing
  traces, missing logs, and cost per successful task.
- Rollback: keep a direct path or manual path ready before canary traffic starts.
- Stopping conditions: stop or slow on wrong answers, schema drift, policy drift, fallback spikes,
  latency regression, cost regression, missing traces, or missing audit logs.
- Receipts: save the command, input fixture, output trace, decision, caveat, and next action.
- Access ladder: offline first, shadow only after evals pass, canary only with logs and controls,
  default only with fallback, monitoring, owner, and stop trigger.

Avoid broad tools, raw customer payloads in logs, unsupported caller paths, unowned alerts, and
default access before the workload, eval, logs, controls, and brake all pass.

This checklist is a candidate until it is adversarially-confirmed to add value on a real workflow.
