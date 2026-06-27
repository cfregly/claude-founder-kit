# Managed Agents Rigor Companion Pin Receipt, 2026-06-27

The value bar is adversarially-confirmed to add value.

## Pin

- Companion: `managed-agents`
- Repo: `https://github.com/cfregly/claude-managed-agents`
- Old pin: `2fa751ab2dc71460dc87307254c30f56f3162dbb`
- New pin: `46dfa8364e97e5287c668c789e6bdf0258aa7edd`
- Tag: `founder-kit-managed-agents-rigor-2026-06-27`
- Ledger: `docs/confirmed-improvements.md`

## What Changed

The companion now includes a cross-stack comparison harness. It runs the same deterministic
ops-triage workload across Claude Managed Agents, a self-managed Claude Messages tool loop, OpenAI
Agents SDK, and Google ADK with Gemini.

## Commands Run

```bash
cd /Users/admin/dev/anthropic/claude-managed-agents
python scripts/deslop_check.py
python -m compileall managed_agents run.py scripts
python -m unittest discover -s tests -q
set -a; source /Users/admin/dev/anthropic/.env; set +a; python run.py compare --live --providers managed,self-managed,openai,gemini
set -a; source /Users/admin/dev/anthropic/.env; set +a; python run.py --cleanup
git commit -m "Add managed agents comparison harness"
git tag founder-kit-managed-agents-rigor-2026-06-27
git push origin main
git push origin founder-kit-managed-agents-rigor-2026-06-27
```

## Why Founder-Kit Should Move

Founder-kit should point builders at the comparison harness, not only the smoke test. The live run
mechanically vetted the same workload across all four stacks, while the companion ledger still keeps
Managed Agents in candidate status until hosted-loop value is proven against the baselines.
