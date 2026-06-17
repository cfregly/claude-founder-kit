# claude-first-hour

A runnable tour of the Claude developer platform, from a single API call up to a
server-managed agent. Clone it, run one command, and watch the whole stack work with
real token counts. Built to run in your first hour with the platform.

## What this answers

- **Question it answers:** what are the layers of the Claude platform, and how do they stack from one API call up to an agent
- **Input:** your `ANTHROPIC_API_KEY`
- **Output:** five runnable steps that print real responses and measured token counts, ending in a Managed Agent that runs a tool inside a hosted sandbox
- **What it is worth:** the platform mental model in one sitting, as code you can run and extend, not slides

## Run it in under a minute

```
cp .env.example .env        # add your ANTHROPIC_API_KEY
make demo
```

Runs the live tour, steps 1 to 4, with real output and token counts. Needs
`ANTHROPIC_API_KEY` and fails fast without it. Step 5 (the Managed Agent) also needs the
managed-agents beta.

## Run it live

```
cp .env.example .env        # add your ANTHROPIC_API_KEY
pip install -r requirements.txt
make tour                   # steps 1-4: message, thinking, tool, agent loop
make agent                  # step 5: a Managed Agent end to end (needs the managed-agents beta)
```

## The tour

| Step | File | What it teaches |
|---|---|---|
| 1 | `tour/step1_message.py` | the foundation: one Messages API call, a list of typed blocks, `stop_reason` |
| 2 | `tour/step2_thinking.py` | adaptive thinking and the effort dial |
| 3 | `tour/step3_tool.py` | one tool, one round trip: `tool_use` then `tool_result` |
| 4 | `tour/step4_agent_loop.py` | the agent: a manual loop over tools until the task is done |
| 5 | `tour/step5_managed_agent.py` | a Managed Agent: environment, agent, session, event stream |

Steps 1 to 4 run on the Messages API and need only a key. Step 5 uses Managed Agents,
where Anthropic runs the loop and hosts the container the tools run in.

The default model is `claude-sonnet-4-6` for a fast, low-cost tour. Set
`TOUR_MODEL=claude-opus-4-8` for the top tier. Model choice is the first cost lever.

## Where to go next

This is the front door. The tools that build on these primitives live at
[github.com/cfregly](https://github.com/cfregly), in two lines:

- **Founder Kit**, run on your own company: diagnose, build, harden, raise. Start with [claude-prompt-to-production](https://github.com/cfregly/claude-prompt-to-production) for the path from a first call to a deployed, cost-engineered product.
- **Activation System**, run on a developer cohort: capture, measure, operate.

Every artifact passes [claude-deslop](https://github.com/cfregly/claude-deslop), the
prose and visual slop gate.

## License

MIT. See [LICENSE](LICENSE).
