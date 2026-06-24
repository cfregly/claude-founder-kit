---
name: deslop
description: >-
  De-slop a document, README, landing page, or any prose: strip the AI-slop
  tells (em-dashes, buzzwords, filler phrases, "it's not X, it's Y" framing,
  generic template copy) and, for rendered HTML, the visual AI-slop blacklist
  (purple gradients, centered-everything, emoji-as-design, border-left cards).
  Runs the deterministic `deslop` linter, then rewrites the flagged lines.
  Use when asked to de-slop, remove AI tells, make writing sound human, kill
  em-dashes and buzzwords, or check a page for the AI-generated look. Triggers
  on "deslop", "de-slop", "remove AI slop", "kill the em-dashes", "make this
  not sound like AI", "buzzword check", or "does this look AI-generated".
---

# deslop

The quality discipline runs across the kit's stage docs and artifacts. It is the gate that proves the output: the credibility check every repo, deck, resume, and profile can pass through, one canonical ruleset against prose and rendered-HTML slop. The rule score is deterministic by design, that is what a gate is, and it runs offline in CI with no key. The optional semantic pass (`--judge`, default-on and TTY-gated for interactive runs) reads for the slop the rules cannot enumerate, and it never changes the score.

One canonical ruleset (`deslop/slop_rules.json`), two surfaces: prose tells and
visual AI-slop. The rules are deterministic so the result is the same every run,
and the same JSON drives the gates in the sibling repos (resume/deck builder and
the three linters) through `scripts/sync.py`.

## Workflow

### 1. Lint first, do not rewrite from memory

Run the linter and read the findings. Never guess at slop. Let the rules find it.

```bash
python -m deslop path/to/file.md      # prose
python -m deslop path/to/page.html    # prose + visual
git diff --name-only | xargs -I{} python -m deslop {}   # a whole change
```

Each finding has a rule id, a location, and a concrete fix. Exit code is the
count of error+warn findings, so this drops into a pre-commit hook or CI step.

### 2. Rewrite the flagged lines, keep the meaning

- Dashes (DS001): comma, colon, period, or middot. Never an em-dash or en-dash.
- Buzzwords (DS002): cut the adjective or replace it with a number or a concrete
  noun. "robust" and "comprehensive" usually mean nothing. Delete them.
- Filler phrases (DS003): delete and state the point.
- "It's not X, it's Y" (DS004): say the Y, drop the setup.
- Generic copy (DS005): replace with a specific claim about this thing, with a
  number.
- Visual (DS010-DS013): no purple/indigo palette, center sparingly, no
  decorative emoji, let spacing and type carry a card instead of a left border.

### 3. Re-lint until clean

Re-run the linter. Prose should reach grade A (100) and visual should clear its
blacklist. A sentence that carries no number, decision, or caveat gets deleted.

## The rule of thumb

Numbers over adjectives. Short, verb-led sentences. If a line could open any
company's landing page, it says nothing. Make it say something only this one
could say.

## When a flag is intentional

If the founder means to keep a word, phrase, or rule, do not fight the linter:
add it to a `.desloprc` at the repo root (`allow_words`, `allow_phrases`,
`disable_rules`). The CLI auto-loads it. An advisor can reuse one house-style
file across a portfolio.

## Updating the rules

`deslop/slop_rules.json` is the single source. After editing it, run
`python scripts/sync.py` to push the change into the sibling repos, and
`python scripts/sync.py --check` to confirm nothing drifted.
