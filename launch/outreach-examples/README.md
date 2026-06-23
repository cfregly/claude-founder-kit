# Outreach examples

Example founder emails you can adapt for developer activation. Each one is a short, warm note to a
builder: it names the workload, shows the one Claude feature and the small code change, gives a real
before and after number from the matching brief, and links the one-command run. They are templates, not
sent mail. The `{first_name}` and `{your_name}` placeholders and the neutral sign-off are meant to be
filled in.

- [ptc-email.md](ptc-email.md): programmatic tool calling, for cost and speed in agents that call a tool a lot.
- [citations-email.md](citations-email.md): Citations, for accuracy in a product that answers over user docs.
- [agent-email.md](agent-email.md): code execution state, for reliability in a multi-step agent that keeps its sandbox state across turns.

Each email links to a runnable brief in `cfregly/claude-feature-hits`, and every number matches that
brief, so the reader sees the same figure when they run it.

## Who each one is for

Not the same email to 200 companies. Each brief maps to a different builder bottleneck, and you can route
a company to the right one from a signal in its one-line description.

**Cost and speed (programmatic tool calling)** goes to builders whose bottleneck is cost at scale or
latency from fan-out: an agent that calls a tool many times over data it then crunches, so the tool
outputs fill the context and the bill grows with the data the agent touches. Route here when the
description says ops, logs, traces, usage, billing, accounts, cohorts, or analytics. It fits AI ops
and incident response, FinOps and usage metering, log and trace triage, analytics and BI agents, and
customer-health or churn.

**Accuracy (Citations)** goes to builders whose bottleneck is a verifiable answer: a product that
answers over the user's own documents where a wrong source is a non-starter, so they cannot ship
without a pointer to the exact sentence. Route here when the description says documents, contracts,
records, filings, claims, policies, compliance, or names a regulated vertical like legal, health,
fintech, or insurance. It fits contract review, clinical-note answers, financial filings and KYC,
policy and claims analysis, and support or knowledge copilots over docs.

**Reliability (code execution state)** goes to builders whose bottleneck is a long-running or stateful code agent: a
multi-step agent that runs code in a sandbox and needs its files and state to persist across turns, so
without it they re-upload and re-run setup every call and write their own checkpointing glue. Route here
when the description says sandbox, isolated workspace, container, test code before production, coding
agents, digital twin, or a data agent that builds up intermediate artifacts. It fits sandboxed code
testing, isolated agent workspaces, and data or analytics agents that carry state.

**Security** goes to builders whose bottleneck is agent attack surface: prompt injection, MCP or app
connector access, destructive tools, compliance exports, audit, or customer-managed encryption. A
security route should become a discovery draft or a tool-boundary review, not a forced public feature
brief unless a measured security brief exists.

The dividing line is one question: which pillar is blocking the next production step: cost, speed,
reliability, accuracy, or security? The keyword router is the first cut, and `--refine` asks Claude
to settle the ones the keywords leave unrouted.

## Route and personalize it in one step

`python -m activation route batch.csv` from the launch module does this on a whole batch: it scores each
company's one-line description, drafts the matching email into the gated outbox, and tailors the opener
to the company's specific use case within the segment. Same brief, a different first line per company.
Add `--refine` and Claude deepens every draft so the whole body matches the company, the example
sentence and the code's tool name, not just the opener, and classifies the ones the keywords could not
call. Claude returns only the short phrases and the router substitutes them, so the verified numbers and
the links never move. Nothing is sent.

So the segmentation goes three levels deep: the pillar picks the brief, the use case writes the opener,
and `--refine` writes the body to the company.

Cost and speed, by use case:

| Use case | Signal in the description | The opener it writes |
| --- | --- | --- |
| FinOps and usage metering | usage, billing, meter | an agent that rolls up usage across accounts |
| AI ops and incident response | logs, traces, incident | an agent that triages logs and traces across services |
| Analytics and BI agents | analytics, dashboard, report | an agent that aggregates rows to answer a question |
| Customer health and churn | churn, retention, CRM | an agent that scores health across your customer base |
| Security and SOC triage | security, alert, vuln | an agent that triages findings across your fleet |

Citations, by use case:

| Use case | Signal in the description | The opener it writes |
| --- | --- | --- |
| Contract review (legal) | contract, clause, legal | a product that answers over contracts |
| Clinical-note answers (health) | clinical, medical, patient | a product that answers over clinical notes |
| Filings and KYC (fintech) | filing, KYC, finance | a product that answers over financial filings |
| Compliance and regulatory | compliance, regulatory, risk | a product that answers over compliance and regulatory docs |
| Policy and claims (insurance) | policy, claim, insurance | a product that answers over policies and claims |
| Support and knowledge copilots | support, ticket, knowledge | a product that answers over your support and knowledge docs |

Code execution state, by use case:

| Use case | Signal in the description | The opener it writes |
| --- | --- | --- |
| Sandboxed code testing | coding agent, test code, before production | an agent that runs and tests code across turns |
| Digital twin or environment | digital twin, simulation, environment | an agent that builds up an environment across turns |
| Data or analytics agent | data, CSV, notebook, model | a data agent that builds up state across turns |
