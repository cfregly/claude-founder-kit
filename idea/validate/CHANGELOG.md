# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-06-13

### Changed
- Synced the deslop canon to 1.1.0 (extended dash set: horizontal bar and figure
  dash).

## [0.1.1] - 2026-06-13

### Fixed
- Platform-risk scoring credits a pitch that ANSWERS the risk (owns the workflow
  of record, the customer eval set, the data boundary) instead of only penalizing
  the vendor mention. The pitch that best answered platform risk used to score
  worst.
- A strong pitch with no weak dimensions now gets a "scale the wedge" call
  instead of the generic "narrow the buyer."

### Changed
- SKILL.md frames the deterministic score as a fast triage signal. The Claude
  intervention is the judgment.

## [0.1.0] - 2026-06-13

### Added
- Deterministic signal scoring, model routing by consequence, and a small eval
  harness.
- Relationship-Activation-Retention growth scorer and the Dot-Dash-Star use-case
  classifier.
- MCP server exposing the scoring tools.
- `scripts/check_docs.py` doc-correctness gate and a CI workflow.
