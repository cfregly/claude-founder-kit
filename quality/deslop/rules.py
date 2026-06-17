"""Deterministic de-slop rules: prose tells plus the visual AI-slop blacklist.

Canonical word, phrase, and visual lists live in slop_rules.json (the single
source the sibling repos sync from). Rules:

  Prose (lint_text):
    DS001  dash tell (em, en, horizontal bar, or figure dash)
    DS002  buzzword (AI / marketing vocabulary; "cutting edge" == "cutting-edge")
    DS003  filler phrase
    DS004  "it's not X, it's Y" framing (also "it isn't X, it's Y")
    DS005  generic template copy ("Welcome to...", "all-in-one solution")
    DS006  draft marker or unfilled placeholder (TODO, FIXME, lorem ipsum,
           "once this repo has a remote", an angle-bracket <your-org> stub)
    DS007  emoji used as decoration in prose

  Visual (lint_html), over HTML/CSS:
    DS010  purple / indigo / blue-to-purple color or gradient
    DS011  centered-everything (3+ `text-align: center`)
    DS012  emoji used as a design element
    DS013  colored left-border cards (`border-left: Npx solid ...`)

Severities: error (-15), warn (-8), info (-3). Score starts at 100, floor 0.
Prose and visual are graded separately (A-F), the way gstack grades a design
score apart from an AI-slop score.
"""
from __future__ import annotations

import json
import pathlib
import re

RULES = json.loads((pathlib.Path(__file__).parent / "slop_rules.json").read_text())

DASHES: list[str] = RULES["dashes"]
BUZZWORDS: list[str] = RULES["buzzwords"]
PHRASES: list[str] = RULES["phrases"]
GENERIC_COPY: list[str] = RULES["generic_copy"]
DRAFT_MARKERS: list[str] = RULES.get("draft_markers", [])

DEDUCTION = {"error": 15, "warn": 8, "info": 3}

# Buzzword stems match the stem plus any letter suffix: "leverag" -> leverages,
# "significan" -> significantly. Word-boundary start keeps them out of the
# middle of unrelated words.
# A hyphen in a buzzword matches a hyphen OR a space, so "cutting edge" is caught
# like "cutting-edge" -- the spaced form is the easy evasion. Stem plus any
# letter suffix as before ("leverag" -> leverages).
BUZZ_RE = re.compile(
    r"\b(" + "|".join(re.escape(s).replace(r"\-", r"[\s\-]") for s in BUZZWORDS)
    + r")[a-z]*", re.I)
PHRASE_RE = re.compile(
    "|".join(re.escape(p).replace("'", "['’]") for p in PHRASES), re.I
)
GENERIC_RE = re.compile("|".join(re.escape(g) for g in GENERIC_COPY), re.I)
DASH_RE = re.compile("[" + "".join(DASHES) + "]")
# Also catches the contraction: "it isn't just X, it's Y".
NOT_X_BUT_Y = re.compile(r"\bit(?:['’]?s not|\s?isn['’]?t)\b[^.]{0,40}?,?\s*it['’]?s\b", re.I)
EMOJI = re.compile("[\U0001F000-\U0001FAFF\uFE0F]")

HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
# "Centered everything" is the tell, in CSS or Tailwind/flexbox form. Count all
# horizontal-centering signals; 3+ is the AI-template rhythm. Vertical centering
# (align-items) is left out -- it is common and not a slop tell on its own.
CENTER = re.compile(
    r"text-align\s*:\s*center"
    r"|justify-content\s*:\s*center"
    r"|place-(?:items|content)\s*:\s*center"
    r"|\btext-center\b|\bmx-auto\b|\bjustify-center\b"
    r"|\bplace-(?:items|content)-center\b",
    re.I)
# Colored left-border card: the CSS form or the Tailwind thick left border
# (border-l-2/4/8), the starter-template accent.
BORDER_LEFT = re.compile(
    r"border-left\s*:\s*\d+px\s+solid|\bborder-l-\d\b", re.I)
# Purple/indigo/violet shows up in real CSS as more than hex. Catch rgb()/hsl()
# and Tailwind utility classes (from-purple-500, bg-violet-600), or the #1
# AI-site tell walks right past a hex-only check.
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.I)
HSL = re.compile(r"hsla?\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%", re.I)
TAILWIND_PURPLE = re.compile(
    r"\b(?:from|via|to|bg|text|border|ring|fill|stroke)-"
    r"(?:purple|violet|indigo|fuchsia)-\d{2,3}\b", re.I)

# DS006 draft seams. DRAFT_RE matches authoring markers and template-leftover
# phrases; PLACEHOLDER_RE matches angle-bracket fill-me stubs (<your-org>,
# <YOUR_API_KEY>) without flagging real HTML tags or <https://...> autolinks.
DRAFT_RE = (re.compile(r"\b(" + "|".join(re.escape(m) for m in DRAFT_MARKERS) + r")\b", re.I)
            if DRAFT_MARKERS else None)
PLACEHOLDER_RE = re.compile(
    r"<[^>\n]{0,60}?\b(your|insert|replace|placeholder|todo|"
    r"org[-_ ]?name|user[-_ ]?name|repo[-_ ]?name|api[-_ ]?key)\b[^>\n]{0,60}?>",
    re.I,
)

# Markdown code is not prose: blank fenced (```/~~~) and inline (`...`) code so
# the prose rules don't fire on code samples. A README legitimately shows
# `leverage` as a flag or <your-org> inside an install snippet; catching that
# is the per-repo check_docs gate's job, not the prose linter's. Newlines are
# preserved so reported line numbers stay accurate.
_FENCED_RE = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+?`")


def _strip_code(text: str) -> str:
    text = _FENCED_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)


def _finding(rule, severity, message, fix, line=None):
    return {"rule": rule, "severity": severity, "line": line,
            "message": message, "fix": fix}


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _is_purplish_rgb(r: int, g: int, b: int) -> bool:
    """Purple/indigo/violet: blue dominant, green the suppressed channel, red at
    or below blue. Catches violet #7C3AED and indigo #4F46E5; skips clay, slate,
    and pure blue, where green is not suppressed below red."""
    if b < 120 or b != max(r, g, b):
        return False
    # Violet (high red): green clearly below both red and blue.
    if g < r and g < b and (min(r, b) - g) > 25:
        return True
    # Indigo (low red, e.g. #4F46E5): blue dominates by a wide margin and green
    # does not exceed red, which rules out pure blue and cyan.
    return g <= r and (b - max(r, g)) >= 60


def _is_purplish(hexstr: str) -> bool:
    h = hexstr.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return _is_purplish_rgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _purple_signals(html: str) -> list[str]:
    """Purple/indigo/violet tells across the ways real CSS sets color: hex,
    rgb(), hsl() (hue in the violet band, not a gray), and Tailwind classes."""
    found: list[str] = [m.group(0) for m in HEX.finditer(html) if _is_purplish(m.group(0))]
    for m in RGB.finditer(html):
        if _is_purplish_rgb(int(m.group(1)), int(m.group(2)), int(m.group(3))):
            found.append(m.group(0))
    for m in HSL.finditer(html):
        hue, sat, lig = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 250 <= hue <= 292 and sat >= 30 and 20 <= lig <= 80:
            found.append(m.group(0))
    found += [m.group(0) for m in TAILWIND_PURPLE.finditer(html)]
    return sorted(set(found))


def lint_text(text: str, config: dict | None = None) -> list[dict]:
    """Prose de-slop findings for plain text or Markdown."""
    text = _strip_code(text)
    out: list[dict] = []
    for m in DASH_RE.finditer(text):
        out.append(_finding("DS001", "warn", f"dash tell: {m.group(0)!r}",
                            "Use a comma, colon, period, or middot.",
                            _line_of(text, m.start())))
    seen: set[str] = set()
    for m in BUZZ_RE.finditer(text):
        w = m.group(0).lower()
        if w in seen:
            continue
        seen.add(w)
        out.append(_finding("DS002", "warn", f"buzzword: {m.group(0)!r}",
                            "Cut it or replace it with a number or a concrete noun.",
                            _line_of(text, m.start())))
    for m in PHRASE_RE.finditer(text):
        out.append(_finding("DS003", "error", f"filler phrase: {m.group(0)!r}",
                            "Delete it and state the point.",
                            _line_of(text, m.start())))
    for m in NOT_X_BUT_Y.finditer(text):
        out.append(_finding("DS004", "warn",
                            f'"it is not X, it is Y" framing: {m.group(0)!r}',
                            "Say the Y. Drop the setup.", _line_of(text, m.start())))
    for m in GENERIC_RE.finditer(text):
        out.append(_finding("DS005", "warn", f"generic template copy: {m.group(0)!r}",
                            "Replace with a specific claim, with a number.",
                            _line_of(text, m.start())))
    if DRAFT_RE is not None:
        for m in DRAFT_RE.finditer(text):
            out.append(_finding("DS006", "warn", f"draft marker: {m.group(0)!r}",
                                "Finish the draft: remove the marker or write the real line.",
                                _line_of(text, m.start())))
    for m in PLACEHOLDER_RE.finditer(text):
        out.append(_finding("DS006", "warn", f"unfilled placeholder: {m.group(0)!r}",
                            "Replace the placeholder with the real value before shipping.",
                            _line_of(text, m.start())))
    emoji = sorted(set(EMOJI.findall(text)))
    if emoji:
        first = EMOJI.search(text)
        out.append(_finding("DS007", "warn", f"emoji in prose: {' '.join(emoji)}",
                            "Cut the decorative emoji. A number or a plain noun "
                            "carries more, and emoji read as AI-generated.",
                            _line_of(text, first.start()) if first else None))
    return _apply_config(out, config)


def lint_html(html: str, config: dict | None = None) -> list[dict]:
    """Visual AI-slop findings for rendered HTML/CSS."""
    out: list[dict] = []
    purples = _purple_signals(html)
    if purples:
        out.append(_finding("DS010", "warn",
                            f"purple/indigo palette: {', '.join(purples[:4])}",
                            "The purple-gradient look is the #1 AI-site tell. Pick a "
                            "brand color with intent.",
                            None))
    centers = len(CENTER.findall(html))
    if centers >= 3:
        out.append(_finding("DS011", "warn",
                            f"centered-everything ({centers} text-align:center)",
                            "Center sparingly. Left-align body and most headings."))
    emoji = sorted(set(EMOJI.findall(html)))
    if emoji:
        out.append(_finding("DS012", "warn", f"emoji as decoration: {' '.join(emoji)}",
                            "Cut decorative emoji; use a real icon system if needed."))
    if BORDER_LEFT.search(html):
        out.append(_finding("DS013", "info", "colored left-border card",
                            "The `border-left: 3px solid accent` card is a starter-"
                            "template tell. Let spacing and type carry the card."))
    return _apply_config(out, config)


def _score(findings: list[dict]) -> int:
    return max(0, 100 - sum(DEDUCTION[f["severity"]] for f in findings))


def grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def load_config(start: str | None = None) -> dict:
    """Load a .desloprc (JSON) from `start` (or cwd), walking up to the repo root.

    Lets a founder or advisor bless intentional choices so the linter does not
    nag, and ship one house-style file across a portfolio. Keys (all optional):
    allow_words (buzzword stems to permit), allow_phrases, disable_rules.
    """
    d = pathlib.Path(start or ".").resolve()
    for cur in [d, *d.parents]:
        rc = cur / ".desloprc"
        if rc.is_file():
            cfg = json.loads(rc.read_text())
            return {
                "allow_words": [w.lower() for w in cfg.get("allow_words", [])],
                "allow_phrases": [p.lower() for p in cfg.get("allow_phrases", [])],
                "disable_rules": set(cfg.get("disable_rules", [])),
                "_path": str(rc),
            }
        if (cur / ".git").exists():
            break
    return {"allow_words": [], "allow_phrases": [], "disable_rules": set()}


def _apply_config(findings: list[dict], config: dict | None) -> list[dict]:
    if not config:
        return findings
    disabled = config.get("disable_rules") or set()
    allow_w = config.get("allow_words") or []
    allow_p = config.get("allow_phrases") or []
    out = []
    for f in findings:
        if f["rule"] in disabled:
            continue
        # Whole-word match against the flagged term, not a substring: blessing
        # "nova" must not suppress "innovative", and blessing "robust" must still
        # suppress "robust". The message quotes the flagged term, so the word
        # boundaries land on the quotes.
        msg = f.get("message", "").lower()
        if f["rule"] == "DS002" and any(re.search(r"\b" + re.escape(w) + r"\b", msg) for w in allow_w):
            continue
        if f["rule"] == "DS003" and any(re.search(r"\b" + re.escape(p) + r"\b", msg) for p in allow_p):
            continue
        out.append(f)
    return out


def _looks_like_html(text: str) -> bool:
    return bool(re.search(r"<\w+[\s>]|style\s*=|</\w+>", text))


def lint(text: str, config: dict | None = None) -> dict:
    """Lint text (and, if it looks like HTML, its visual layer too)."""
    prose = lint_text(text, config)
    is_html = _looks_like_html(text)
    visual = lint_html(text, config) if is_html else []
    pscore, vscore = _score(prose), _score(visual)
    report = {
        "prose_score": pscore, "prose_grade": grade(pscore),
        "findings": prose + visual,
    }
    if visual or is_html:
        report["visual_score"] = vscore
        report["visual_grade"] = grade(vscore)
    return report
