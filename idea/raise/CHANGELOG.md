# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2026-06-18

### Changed
- PD008 now counts only the main-arc slides toward the 12-slide limit. Clearly
  denoted appendix slides, a headline starting with "Appendix" or an explicit
  `"appendix": true`, are the backup an investor pages through after the pitch,
  so they no longer push a deck over the limit. A bloated main arc still warns.

## [0.1.6] - 2026-06-16

### Changed
- The claude-opus-4-8 narrative read now runs by default when a key is set,
  instead of behind an opt-in `--judge` flag. It still prints below the score,
  is advisory, and never changes the deterministic score or the exit code. Pass
  `--no-judge` to skip it. With no key it skips cleanly, so the pitch_lint score
  stays the gate and CI runs offline without a key. `--judge` is still accepted.
- Reframed the docs: the pitch_lint score is the deterministic gate that
  verifies the deck before it ships, and Claude does the narrative critique the
  rules cannot. Dropped the "optional layer" and "fallback" framing.

## [0.1.5] - 2026-06-13

### Added
- The readout now leads with the four dimensions an investor judges (does it
  tell the whole story, will it survive diligence, does it answer what investors
  will ask, is the ask clear), then the line items grouped under them. A deck
  review, not a lint dump. Numbers are one diligence signal, not the verdict.
- PD015, the wedge: a deck that sells to "everyone" has no first buyer.
  Investors fund a wedge, not a market. This is the founder mistake that sinks
  more decks than any unsourced number.

## [0.1.4] - 2026-06-13

### Fixed
- PD006 recognizes European period-grouped thousands ("1.234.567"). It requires
  two or more groups, so a version like "2.345" or "Python 3.11" stays exempt.

## [0.1.3] - 2026-06-13

### Fixed
- PD006 recognizes the number formats real decks use: comma-grouped thousands
  ("2,400 customers"), the "bn"/"mn" abbreviation, and the euro, pound, and yen
  currency symbols. These traction figures used to slip through unsourced. Specs
  and ratings (GPT-4o, Top 3, 4.8/5, Python 3.11) stay exempt.

## [0.1.2] - 2026-06-13

### Fixed
- A number is sourced only when a present claim key vouches for that exact
  figure. An "85% gross retention" claim no longer silently sources a bare "5%"
  elsewhere on the face, which had hidden a genuinely unsourced number.

### Changed
- Synced the deslop canon to 1.1.0 (extended dash set).

## [0.1.1] - 2026-06-13

### Fixed
- Calibration on real decks. Version and spec numbers (`Python 3.11`, `SOC 2`)
  no longer flag as unsourced. The raise amount on the ask slide is exempt from
  the source-tier check. A figure repeated on one slide counts once. Before
  this, realistic decks scored F across the board and could not be told apart.

### Changed
- PD001 headline length: 9-10 words is an info nudge, not a warn. The error is
  reserved for run-ons over 14 words. A per-rule deduction cap keeps one weak
  category from flooring an otherwise strong deck.

## [0.1.0] - 2026-06-13

### Added
- 14 rules (PD001-PD014): headline and line discipline, claim tiers, the
  platform-risk check, and the retention check.
- Claims ledger, Sequoia template, and a deck renderer.
- `scripts/check_docs.py` doc-correctness gate that keeps the README rule count
  in sync with the code, and a CI workflow that reproduces the 0-to-100 marquee.
