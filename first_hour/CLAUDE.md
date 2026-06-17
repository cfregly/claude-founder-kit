# CLAUDE.md

Agent guide for claude-first-hour, a runnable tour of the Claude platform.

## What this is

Five scripts that climb the platform stack, from one Messages API call (step 1) to a
Managed Agent running a tool in a hosted sandbox (step 5). Each prints real output and
token counts. The headline `make demo` runs the live tour, steps 1 to 4.

## Run

- `make demo` runs steps 1-4 live. Needs `ANTHROPIC_API_KEY` and fails fast without it.
- `make tour` runs steps 1-4 live. Needs `ANTHROPIC_API_KEY` (copy `.env.example` to `.env`).
- `make agent` runs step 5 live. Needs the key and the managed-agents beta on the org.
- `make check` gates the prose in README.md and CLAUDE.md (no em dashes, en dashes, or semicolons).

## Layout

- `tour/setup.py` loads a local `.env`, builds the client, and resolves the model.
- `tour/step1_message.py` through `step5_managed_agent.py` are the five steps, run in order.
- `transcript.md` is a recorded real run kept as a reference of the expected output.
- `check.py` is the prose gate.

## Extend

- Add a step as `tour/stepN_name.py`, import from `setup`, and add it to the `tour` target.
- Keep each step short and self-contained. One concept per file.
- Regenerate `transcript.md` by running the tour live and pasting the output, with any
  account resource ids replaced by placeholders.

## Before commit

Run `make check`. Keep prose free of em dashes, en dashes, and semicolons. The default
model is `claude-sonnet-4-6` for cost. Never commit `.env`.
