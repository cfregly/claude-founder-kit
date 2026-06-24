---
name: pitch-deck
description: >-
  Build or sharpen a startup pitch deck on the Sequoia 10-slide arc, with a
  claims ledger (measured / attested / public / modeled) and a deterministic
  linter (pitch_lint) that fails decks where words stopped fighting for their
  place. Use when a founder asks to create a pitch deck, sharpen a pitch,
  review a deck, apply the Sequoia template, prep a fundraise narrative, or
  fix a deck an investor bounced. Triggers on "pitch deck", "sequoia
  template", "investor deck", "sharpen my pitch", "deck review", "fundraise
  narrative", or any combination of "deck / pitch / raise" with "create /
  review / sharpen / fix".
---

# pitch-deck

A founder runs this at the Idea stage of a founder playbook for Claude builders, to
pressure-test the raise before they build. It builds and lints a pitch deck on
the Sequoia arc, with a claims
ledger and a deterministic
linter that fails decks where words stopped fighting for their place. Built on
the Claude Developer Platform: the pitch_lint score is the deterministic gate,
and claude-opus-4-8 reads the narrative arc the rules cannot, by default when a
key is set. The score runs the same with or without a key, so CI stays green.

The discipline is the product: assertions for headlines, numbers on faces,
sources for every figure, and a linter that fails the build when the deck
goes soft.

## Workflow

### 1. Intake

Collect whatever exists: pitch paste, README, memo, current deck text.
Do not start writing slides yet.

### 2. Claims inventory (do this before any prose)

Extract every number and named company. For each number, ask the founder to
tier it:

- **measured** - you ran it. You can show the run
- **attested** - someone with standing stated it. You can name who
- **public** - citable public source
- **modeled** - a projection. It must carry a hedge ("~", "roughly", "modeled")

A number the founder cannot tier is **unsourced: it does not enter the
deck.** Park it in the inventory with what receipt would unlock it. For each
named company, record `named-ok` (permission exists) or `anonymize`.

### 3. Map to the arc

Use [`templates/sequoia.json`](../../templates/sequoia.json): ten slides, each
with the question it must answer and the trap it usually falls into. Three
house rules layered on top:

- **Competition must answer platform risk**: why not the incumbents, why not
  the cloud, why not the model providers - what survives platform gravity?
- **Why-now must name the forcing function** and what compounds in the
  founder's favor: data, workflow, distribution, urgency.
- **Strongest measured evidence by slide 3.** Partners decide early.

### 4. Draft

- Headlines are assertions (≤ 8 words). The headline is the claim. The lines
  are the evidence.
- Lines ≤ 20 words. No banned phrases, no em-dashes on faces.
- Numbers on faces, hedged by tier. Logos without numbers, numbers without
  logos.
- Speaker notes are a talk track: what the founder says, nothing else.
- Diagrams must look like their names: a loop looks like a loop, a funnel
  narrows.
- De-slop everything, notes included: no em-dashes anywhere, minimal bold,
  plain punctuation, verb-led lines, numbers over adjectives. The linter only
  polices faces (PD003/PD004). Hold the notes to the same bar yourself.

### 5. Lint, then iterate

```bash
python -m pitch_lint deck.json --min-score 80
```

The score is the gate. Fix every error, justify every surviving warning to the
founder out loud. Re-lint until the gate passes. Never hand-wave a PD006
(unsourced number): that one sinks decks in diligence, not just in lint.

With a key set, claude-opus-4-8 prints a narrative read below the score: the arc
beats that do not earn the next, the gaps, and the strongest slide. Use it to
push on the story the rules cannot see. It is advisory and never moves the gate.
Pass `--no-judge` to skip it.

### 6. Render (optional)

```bash
node render/deck_from_spec.mjs deck.json          # presenter deck
NO_NOTES=1 node render/deck_from_spec.mjs deck.json  # share-safe, notes stripped
```

Send only the PDF or the notes-stripped variant. The noted file is the
founder's, alone.

## What NOT to do

- Never invent a number, a customer, or an outcome. Empty slide beats fake
  evidence.
- Never upgrade modeled into measured because it reads better.
- Never put strategy rules in the speaker notes. Notes are for the mouth.
