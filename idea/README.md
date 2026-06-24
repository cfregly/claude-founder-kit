# Idea, validate the signal and lint the raise

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**The Idea stage of a founder workflow kit for Claude builders.** Validate the idea before you build, and pressure-test the raise. Two tools live here, co-located, each with its own working code, tests, and gate.

- `validate/` scores the startup signal and argues against the idea, so the weak spots surface before you write a line of product code.
- `raise/` builds and lints the pitch deck on the Sequoia arc, so the story holds up before an investor reads it.

Claude runs the judgment in both tools. A deterministic score runs offline and is the gate CI re-runs. The score never needs an API key, so the gate stays reproducible.

## Value Bar

The Idea tools are candidates until they are adversarially-confirmed to add value for a founder deciding what to build or how to pitch it. A clean score means the artifact passed the local rules. It does not mean the advice helped unless a skeptical founder or reviewer compares it with a baseline and leaves a receipt.

## The two tools

### validate: score the signal, argue against the idea

`validate/` is the startup validation linter. It scores raw founder signal, a pitch, site copy, or a README, into product, GTM, and architecture decisions. Local deterministic scoring rates value proposition, urgency, platform risk, moat, and customer pain, runs a Relationship-Activation-Retention growth read that names the weakest stage, and sorts the AI use cases into Dot (ship now), Dash (build next), and Star (the vision bet). Then `claude-opus-4-8` reads those scores and writes the founder intervention: what to build, what to cut, what to measure, and the model and tooling to use. The deterministic scoring is the gate, and it runs without a key.

```bash
cd validate
python -m startup_signal_lab.score examples/strong_pitch.md   # 8/10, offline
```

### raise: build the deck, lint it on the arc

`raise/` is the pitch and raise linter. It builds a deck on the Sequoia 10-slide arc, holds a claims ledger where every number carries a source tier (measured, attested, public, or modeled), and runs `pitch_lint`, a deterministic linter that fails a deck where the words stopped fighting for their place. A sloppy deck scores 0 of 100 and fails the gate. The same company rewritten on the arc scores 100. The `pitch_lint` score is the gate and runs without a key. With a key set, `claude-opus-4-8` reads the narrative arc the rules cannot and prints an advisory read that never moves the score.

```bash
cd raise
python -m pitch_lint examples/sharp_deck.json   # 100/100, offline
```

## Run it

From the repo root, `make` drives both tools at once:

```bash
make check    # both sub-tools doc-correctness gates
make test     # both sub-tools test suites
make demo     # each sub-tools demo
```

Each target runs the matching target inside `validate/` and `raise/`, so every existing gate runs from inside the subdir that owns it. To work on one tool alone, `cd` into its subdir and run that tool's own `make` targets.

## Where this fits

This is the **Idea** module of [claude-founder-kit](../README.md). The full journey runs as modules in one repo: first_hour, idea, mvp, launch, scale, quality, cost. The kit names what a founder does at each stage, and these are the runnable tools that do it. Each stage keeps a deterministic gate, and live Claude calls run only where the command says a key is required. One `make demo` from the repo root runs the live walkthrough when a key is set.

## License

MIT. See [LICENSE](LICENSE).
