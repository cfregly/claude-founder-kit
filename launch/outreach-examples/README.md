# Outreach examples

Example founder emails you can adapt for developer activation. Each one is a short, warm note to a
builder: it names the workload, shows the one Claude feature and the small code change, gives a real
before and after number from the matching brief, and links the one-command run. They are templates, not
sent mail. The `{first_name}` and `{your_name}` placeholders and the neutral sign-off are meant to be
filled in.

- [ptc-email.md](ptc-email.md): programmatic tool calling, for an agent that calls a tool a lot.
- [citations-email.md](citations-email.md): Citations, for a product that answers over user docs.

Each email links to a runnable brief in `cfregly/claude-feature-briefs`, and every number matches that
brief, so the reader sees the same figure when they run it.

## Who each one is for

Not the same email to 200 companies. Each brief maps to a different builder bottleneck, and you can route
a company to the right one from a signal in its one-line description.

**Token MINNing (programmatic tool calling)** goes to builders whose bottleneck is cost at scale: an
agent that calls a tool many times over data it then crunches, so the tool outputs fill the context and
the bill grows with the data the agent touches. Route here when the description says agent, automate,
ops, observability, logs, traces, usage, billing, accounts, cohorts, or analytics. It fits AI ops and
incident response, FinOps and usage metering, log and trace triage, analytics and BI agents, and
customer-health or churn.

**Citations** goes to builders whose bottleneck is trust to ship: a product that answers over the user's
own documents where a wrong source is a non-starter, so they cannot ship without a verifiable pointer to
the exact sentence. Route here when the description says documents, contracts, records, filings, claims,
policies, compliance, or names a regulated vertical like legal, health, fintech, or insurance. It fits
contract review, clinical-note answers, financial filings and KYC, policy and claims analysis, and
support or knowledge copilots over docs.

The dividing line is one question: is the bottleneck the bill or the trust? Send Token MINNing to the
bill and Citations to the trust.

## Route and personalize it in one step

`python -m activation route batch.csv` from the launch module does this on a whole batch: it scores each
company's one-line description, drafts the matching email into the gated outbox, and tailors the opener
to the company's specific use case within the segment. Same brief, a different first line per company.
Add `--refine` to have Claude classify the ones the keywords could not call. Nothing is sent.

So the segmentation goes two levels deep: the segment picks the brief, the use case writes the opener.

Token MINNing, by use case:

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
| Policy and claims (insurance) | policy, claim, insurance | a product that answers over policies and claims |
| Support and knowledge copilots | support, ticket, knowledge | a product that answers over your support and knowledge docs |
