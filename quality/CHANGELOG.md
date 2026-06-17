# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-06-13

### Fixed
- DS011 (centered-everything) and DS013 (left-border card) read Tailwind and
  flexbox forms, not only raw CSS. Modern landing pages center with `text-center`
  / `justify-center` / `mx-auto` and draw card accents with `border-l-4`, all of
  which a CSS-property-only check missed. A single centered hero stays clean.

## [0.1.2] - 2026-06-13

### Fixed
- DS010 detects purple/indigo set with `rgb()`, `hsl()` (violet hue band), and
  Tailwind utility classes (`from-purple-500`, `bg-violet-600`), not only hex.
  Real landing pages express the #1 AI-site tell in these forms, and a hex-only
  check walked right past them. Blue, clay, and desaturated grays stay clean.

## [0.1.1] - 2026-06-13

### Added
- DS007: emoji used as decoration in prose, the prose counterpart to the visual
  DS012.
- Canon 1.1.0: the dash set now includes the horizontal bar (U+2015) and figure
  dash (U+2012), closing the em-dash evasion an adversarial pass found.

### Fixed
- DS002 catches the spaced buzzword variant: "cutting edge" now fires like
  "cutting-edge".
- DS004 catches the contraction: "it isn't X, it's Y", not only "it's not X".

## [0.1.0] - 2026-06-13

### Added
- Prose rules DS001-DS006 and visual rules DS010-DS013, scored A-F.
- DS006: draft markers and unfilled placeholders (TODO, FIXME, an angle-bracket
  `<your-org>` stub, "once this repo has a remote").
- Prose rules now skip fenced and inline code, so install snippets are not
  graded as prose.
- Canonical `slop_rules.json` with `scripts/sync.py` to copy it into the sibling
  repos and fail on drift.
- `.desloprc` to bless intentional words, phrases, and rules.
- `deslop` console entry point. Installable with `pipx install claude-deslop`.
- `scripts/check_docs.py` doc-correctness gate and a CI workflow that self-lints
  the README and reproduces the sloppy/clean marquee.
