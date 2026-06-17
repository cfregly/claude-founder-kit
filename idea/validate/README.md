# Validate, the startup signal lab

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Diagnose the company.** A 15-minute founder demo for showing how Claude can turn messy startup signal into practical product, GTM, and architecture decisions.

**Proves:** Claude tool use with deterministic scoring, model routing by consequence (Haiku / Sonnet / Opus), a small eval harness, MCP portability, and an Agent SDK review loop.
**Production lesson:** route by consequence, not ego - and answer the platform-risk question before investors or customers ask it.
**Run in under 5 minutes:** `python -m startup_signal_lab.score examples/strong_pitch.md` - 8 of 10, offline, no API key.

This repo is intentionally built for live developer-audience demos:

1. Paste a pitch, website copy, or README.
2. Run local deterministic scoring for value proposition, urgency, platform risk, moat, and customer pain. This is the gate that verifies the run, and it runs offline.
3. Claude reads those scores and writes a founder-grade intervention every run: what to build, what to cut, what to measure, and what model and tooling architecture to use.
4. Run a small eval harness that grades Claude's intervention on quality hit-rate, latency, routing choice, and token cost (`python scripts/run_eval.py`).
5. Expose the scoring functions as MCP tools.

The intervention runs Claude (`claude-opus-4-8`) on every analysis, so set `ANTHROPIC_API_KEY` before you run the app or the eval harness. The deterministic scorers run without a key and are the receipt CI re-runs.

## Relationship, Activation, Retention

A founder demo should not stop at the pitch. The linter also scores the growth
spine every Claude startup lives or dies on:

- **Relationship** - who already trusts you, and the community or partner that brings the next 25 buyers.
- **Activation** - the aha moment and the time-to-value from sign-up to first useful result.
- **Retention** - what brings a user back the second time, and what expands as they grow. For an AI product the eval set is the moat: the demo wins the trial, the evals win the renewal.

It is a loop, not a funnel. Retained users are the cheapest acquisition you have,
so retention feeds the top of the next cohort. The scorer names the weakest stage
and hands back the office-hours questions for it. A companion classifier sorts the
pitch's AI use cases into Dot (small, proven, ship now), Dash (connective work,
build next), and Star (the high-ceiling bet, narrate but do not stake the company
on it yet) so the founder sequences for fast payback first.

## Why this demo works in front of founders

Founders do not want another generic chatbot. They want a platform partner who can help them make a sharper product decision today. This demo shows Claude as a product-and-architecture co-pilot that understands startup constraints: speed, unit economics, platform risk, data boundaries, and defensible moats.

## Demo path: zero to wow in under 15 minutes

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add ANTHROPIC_API_KEY: the intervention runs Claude on every analysis
streamlit run app.py
```

The app runs Claude (`claude-opus-4-8`) on every analysis, so set `ANTHROPIC_API_KEY` first. Want to see the deterministic gate alone, offline? Score a pitch headless with `python -m startup_signal_lab.score examples/strong_pitch.md`.

## Environment variables

```bash
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_FAST_MODEL=claude-haiku-4-5
CLAUDE_DEFAULT_MODEL=claude-sonnet-4-6
CLAUDE_DEEP_MODEL=claude-opus-4-8
```

## MCP server

```bash
python -m startup_signal_lab.mcp_server
```

Tools exposed:

- `score_startup_signal`
- `route_claude_model`
- `estimate_unit_economics`
- `draft_founder_intervention`
- `founder_office_hours` - the advisor's forcing questions for the weak dimensions (why now, why not the frontier labs or the cloud, what compounds, data boundary, unit economics)
- `score_growth_readiness` - the Relationship -> Activation -> Retention spine, with the weakest stage to fix first
- `classify_ai_use_cases` - sort the pitch into Dot (ship now), Dash (build next), and Star (the vision bet) by return horizon and risk
- `founder_growth_office_hours` - forcing questions for the weakest growth stage, plus the use-case portfolio

## Claude Skill

Packaged as a Claude Skill in [`skills/startup-linter/SKILL.md`](skills/startup-linter/SKILL.md). Upload the `skills/startup-linter/` folder in the Claude app under Settings > Skills (see [Anthropic's skills guide](https://github.com/anthropics/skills)). Then say "diagnose my startup" or "score my pitch." Claude runs the scoring, the Relationship-Activation-Retention read, the use-case sort, and the founder intervention from one prompt: the same diagnosis without cloning the repo.

## Example pitches

[`examples/strong_pitch.md`](examples/strong_pitch.md) is a strong pitch. It scores 8 of 10, answers platform risk, and earns a scale-the-wedge call. [`examples/sample_pitch.md`](examples/sample_pitch.md) is a mid-stage one with weaker spots. Paste either into the app, or score it headless, to see the signal score, the office-hours agenda, and the intervention. A pitch that names a model provider but never answers "why won't they absorb this?" scores worse than one that does, by design.

Score it headless from the repo root:

```bash
python -m startup_signal_lab.score examples/strong_pitch.md   # 8/10
```

## Claude Agent SDK example

See `examples/agent_sdk_repo_reviewer.py` for a repo-review agent that uses the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) to inspect a repository and produce a founder-ready launch plan.

This example needs the optional Agent SDK, which is intentionally not in `requirements.txt`: `pip install claude-agent-sdk`.

## Why this belongs in a founder workshop

This is a small repo by design. It is meant to be cloned during an office-hours session, extended during a build-a-thon, and used as a reference for how to turn messy founder signal into a sharper product wedge, Claude model-routing decision, and eval/activation plan.

Pair it with a production engineering demo such as the `build/` module of claude-startup-mvp: this module shows the founder intervention, and the build module shows the agent/evals/cost discipline underneath it.

## Where this fits

Six public repos, one per stage of Anthropic's Founder's Playbook (Idea, MVP, Launch, Scale), plus two disciplines that run across every stage. The playbook names what a founder does at each stage. These are the runnable tools that do it. Claude runs the judgment on every stage, and a deterministic gate verifies the output before it ships.

- **Idea**, validate to problem-solution fit: **[claude-startup-idea](https://github.com/cfregly/claude-startup-idea) (this repo)**
- **MVP**, build the product, then a security review before any user: [claude-startup-mvp](https://github.com/cfregly/claude-startup-mvp)
- **Launch**, turn traction into a growth engine that runs without founder bottlenecks: [claude-startup-launch](https://github.com/cfregly/claude-startup-launch)
- **Scale**, build a GTM function and compound data into a moat: [claude-startup-scale](https://github.com/cfregly/claude-startup-scale)
- **Quality**, every stage: [claude-deslop](https://github.com/cfregly/claude-deslop)
- **Cost**, every stage: [claude-cost-control](https://github.com/cfregly/claude-cost-control)

## Limitations

The scores are a structured starting point, not a verdict. Deterministic scoring
is a heuristic that opens the conversation and gates the run. The judgment is the
intervention Claude writes on top of it, and that runs Claude on every analysis,
so the app and the eval harness need ANTHROPIC_API_KEY set.

## License

MIT. See [LICENSE](LICENSE).
