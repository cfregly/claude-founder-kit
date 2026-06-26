# Day-0 Trust Checklist

Use this before a Claude workflow touches customer data or takes an outward action.

- Evals: at least one win case, one honesty case, one permission case, one rollback case, and one
  stopping condition.
- Permissions: name what always runs, what asks first, and what never runs.
- Monitoring: log correctness, latency, fallback rate, policy denials, tool errors, missing traces,
  and cost per successful task.
- Rollback: keep a direct path or manual path ready before canary traffic starts.
- Stopping conditions: stop or slow on wrong answers, schema drift, policy drift, fallback spikes,
  latency regression, cost regression, or missing traces.
- Receipts: save the command, input fixture, output trace, decision, caveat, and next action.

This checklist is a candidate until it is adversarially-confirmed to add value on a real workflow.
