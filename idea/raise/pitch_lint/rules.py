"""Deterministic lint rules for pitch decks.

A deck spec is JSON:

    {
      "company": "Brickline",
      "claims":   { "$1.2M ARR": "measured", "~$40K/mo": "modeled" },
      "entities": { "MegaCorp": "anonymize", "Acme": "named-ok" },
      "slides":   [ { "arc": "purpose", "headline": "...",
                      "lines": ["..."], "notes": "..." } ]
    }

Claim tiers: measured (you ran it), attested (someone with standing said it),
public (citable source), modeled (projection -- must carry a hedge).
A number with no claim entry is unsourced, and unsourced numbers fail decks.

Severities: error (-15), warn (-8), info (-3). Deck starts at 100, floor 0.
"""

from __future__ import annotations

from collections import defaultdict
import json
import pathlib
import re

DEDUCTION = {"error": 15, "warn": 8, "info": 3}

#: Per-rule deduction ceiling. A single category (say, five unsourced numbers)
#: should flag the category loudly, not single-handedly drive the deck to zero.
#: With the cap, the score still separates a strong deck with one weak area from
#: a deck that is weak across the board, instead of flooring both at F.
RULE_CAP = 30

# Shared de-slop canon, synced from the quality module (do not hand-edit
# slop_rules.json; run quality/scripts/sync.py).
_RULES = json.loads((pathlib.Path(__file__).parent / "slop_rules.json").read_text())

ARC = [
    "purpose", "problem", "solution", "why-now", "market",
    "competition", "product", "business-model", "team", "ask",
]

#: slides where a face without a number is an error, not a warning
NUMBERS_REQUIRED = {"market", "business-model", "ask"}
NUMBERS_SILENT = {"purpose", "competition", "team"}  # numberless is a fine choice here
ANY_NUM = re.compile(r"\d")

#: banned on a slide face: the shared buzzword + filler-phrase canon, plus the
#: one deck-specific tell ("the journey") the cross-repo canon leaves out. Stems
#: like "leverag" match as substrings ("leverages", "leveraging").
_PITCH_EXTRA = ["the journey"]
BANNED = _RULES["buzzwords"] + _RULES["phrases"] + _PITCH_EXTRA

#: emoji used as decoration is an AI-slop tell (gstack visual blacklist). The
#: high plane plus the emoji variation selector catches 🚀🔥💡 without flagging
#: legit deck glyphs like ✓, →, ★, or the middot.
EMOJI = re.compile("[\U0001F000-\U0001FAFF\uFE0F]")

#: generic template copy that screams AI-generated landing page (gstack)
GENERIC_COPY = _RULES["generic_copy"]

HEDGE = re.compile(r"~|\broughly\b|\babout\b|\bmodeled\b|\bon the order of\b|\bapprox", re.I)

#: numbers that demand a source: the figures investors diligence -- money,
#: percents, multiples, big counts. A bare decimal is deliberately NOT claimable:
#: "Python 3.11", "GPT-4", "SOC 2", and "Claude 3.5" are specs and names, not
#: traction stats, and flagging them as unsourced is noise. Real claims carry a
#: unit ($, %, x, K/M/B) that one of the branches below already catches.
CLAIMABLE_NUM = re.compile(
    r"[$€£¥]\s?\d[\d,.]*\s?(?:bn|mn|[KMBT])?\+?"   # $1.2M, €40K+, £1.2bn
    r"|\d[\d,.]*\s?%"                               # 37%
    r"|\d[\d,.]*\s?x\b"                             # 10x (the unicode × is left out
    #                                                 on purpose: "3× O'Reilly author"
    #                                                 is a credential, not a traction stat)
    r"|\b\d{1,3}(?:,\d{3})+\b"                      # 2,400  1,200,000 (grouped)
    r"|\b\d{1,3}(?:\.\d{3}){2,}\b"                  # 1.234.567 (EU period thousands);
    #                                                 2+ groups, so versions like 2.345 stay exempt
    r"|\b\d{4,}\b"                                  # 4+ contiguous digits
    r"|\b\d[\d,.]*\s?(?:bn|mn|[KMB])\b",            # 30K users, 1.2bn
    re.I,
)
YEAR = re.compile(r"\b(19|20)\d{2}\b")

NOTES_POLICY = re.compile(
    r"\bNEVER\b|never name|do not (say|mention)|ledger|internal only|confidential|guardrail",
    re.I,
)

# Answering platform risk takes more than the word "platform": "we are a
# platform" is a positioning line, not an answer. Match the actual answer, the
# why-not framing, the incumbent or default-path question, a moat, lock-in, or a
# switching cost.
PLATFORM_RISK = re.compile(
    r"why not|incumbent|default path|platform risk|\bmoat\b|lock[ -]?in|"
    r"switching cost|can'?t (?:replicate|copy|be absorbed)|won'?t absorb|defensib",
    re.I)

#: PD015 the wedge. A deck that sells to "everyone" has no first buyer. Investors
#: fund a wedge, not a market. This is the founder mistake that sinks more decks
#: than any unsourced number: a vague audience and no named first segment.
EVERYONE = re.compile(
    r"\bfor everyone\b|\bany (?:company|business|team|org|developer|user)\b"
    r"|\b(?:all|every) (?:compan|business|team|developer|industr|user)"
    r"|businesses of all sizes|companies of all sizes|from startups to enterprises",
    re.I)

#: Each rule rolls up to a dimension a founder is judged on, so the readout reads
#: like a deck review ("you don't answer platform risk"), not a lint dump
#: ("PD011 warn"). The deterministic linter covers structure, diligence hygiene,
#: and the AI-startup questions; the strategic narrative call is the pitch-deck
#: Claude skill's job, not a regex's.
DIMENSION = {
    "PD001": "story", "PD002": "story", "PD008": "story", "PD009": "story",
    "PD003": "diligence", "PD004": "diligence", "PD006": "diligence",
    "PD007": "diligence", "PD012": "diligence", "PD013": "diligence",
    "PD011": "questions", "PD014": "questions", "PD015": "questions",
    "PD005": "ask", "PD010": "ask",
}
DIMENSION_LABEL = {
    "story": "Does it tell the whole story?",
    "diligence": "Will it survive diligence?",
    "questions": "Does it answer what investors will ask?",
    "ask": "Is the ask clear?",
}


# AUTO-FIX vs ASK, the same split the agent linter uses. 'auto' findings are
# mechanical: delete the banned phrase, swap the em-dash, cut the emoji. 'ask'
# findings need a founder's judgment: write the number, source the claim, answer
# platform risk. An advisor applies the auto set and books a call for the rest.
FIX_KIND = {"PD003": "auto", "PD004": "auto", "PD012": "auto"}


def fix_kind(rule: str) -> str:
    return FIX_KIND.get(rule, "ask")


def _finding(rule, severity, slide, message, fix):
    return {"rule": rule, "severity": severity, "slide": slide,
            "message": message, "fix": fix, "fix_kind": fix_kind(rule)}


def _face_text(slide: dict) -> str:
    return " ".join([slide.get("headline", "")] + list(slide.get("lines", [])))


def _claim_numbers(text: str) -> list[str]:
    """Numbers in this text that require a claim tier (years exempt)."""
    out = []
    for m in CLAIMABLE_NUM.finditer(text):
        tok = m.group(0).strip()
        if YEAR.fullmatch(tok):
            continue
        out.append(tok)
    return out


def lint_deck(deck: dict) -> dict:
    slides = deck.get("slides", [])
    claims = deck.get("claims", {}) or {}
    entities = deck.get("entities", {}) or {}
    findings: list[dict] = []
    f = findings.append

    # ---- per-slide rules -------------------------------------------------
    first_measured_at = None
    for i, s in enumerate(slides, start=1):
        arc = s.get("arc", f"slide-{i}")
        label = f"{i}:{arc}"
        headline = s.get("headline", "")
        lines = list(s.get("lines", []))
        face = _face_text(s)
        notes = s.get("notes", "")

        # PD001 headline length: the headline is the claim. A crisp 9-10 word
        # headline is a nudge (info), not a real defect; the run-on (>14) is the
        # error. This keeps the "aim for 8" discipline without scoring a sharp
        # 9-word assertion as harshly as a 20-word sentence on a slide.
        hw = len(headline.split())
        if hw > 14:
            f(_finding("PD001", "error", label,
                       f"headline is {hw} words; the headline is the claim",
                       "Cut to one assertion, 8 words or fewer."))
        elif hw > 10:
            f(_finding("PD001", "warn", label,
                       f"headline is {hw} words",
                       "Aim for 8 or fewer. Every word fights for its place."))
        elif hw > 8:
            f(_finding("PD001", "info", label,
                       f"headline is {hw} words",
                       "Tighten toward 8. The headline is the claim."))

        # PD002 line length
        for ln in lines:
            lw = len(ln.split())
            if lw > 30:
                f(_finding("PD002", "error", label,
                           f"line is {lw} words: \"{ln[:50]}...\"",
                           "Slides are not paragraphs. Cut to 20 words or fewer."))
            elif lw > 20:
                f(_finding("PD002", "warn", label,
                           f"line is {lw} words: \"{ln[:50]}...\"",
                           "Cut to 20 words or fewer."))

        # PD003 banned phrases
        low = face.lower()
        for b in BANNED:
            if b in low:
                f(_finding("PD003", "error", label,
                           f"banned phrase: \"{b}\"",
                           "Say what it does, with a number. Adjectives are not evidence."))

        # PD004 em-dash on a face
        if "—" in face:
            f(_finding("PD004", "warn", label, "em-dash on a slide face",
                       "Use a period, colon, or middot. Faces are not essays."))

        # PD012 emoji as decoration: an AI-slop visual tell on a slide face
        emoji = EMOJI.findall(face)
        if emoji:
            f(_finding("PD012", "warn", label,
                       f"emoji on a slide face: {' '.join(emoji)}",
                       "Cut the emoji. A number or a system icon carries more "
                       "than a glyph, and emoji read as AI-generated."))

        # PD013 generic template copy (the AI landing-page voice)
        for g in GENERIC_COPY:
            if g in low:
                f(_finding("PD013", "warn", label,
                           f"generic template copy: \"{g}\"",
                           "Replace with a specific claim about this company, "
                           "with a number. Template copy says nothing."))

        # PD005 numberless slide
        if not ANY_NUM.search(face):
            if arc in NUMBERS_REQUIRED:
                f(_finding("PD005", "error", label,
                           f"a {arc} slide with no numbers",
                           "This slide IS its numbers. Add the figure or cut the slide."))
            elif arc not in NUMBERS_SILENT:
                f(_finding("PD005", "warn", label, "no numbers on this slide",
                           "Find the number that proves the sentence."))

        # Claims present on this face: hedge discipline + measured tracking
        present_keys = [k for k in claims if k in face]
        for k in present_keys:
            tier = claims[k]
            if tier == "modeled" and not HEDGE.search(face):
                f(_finding("PD006", "warn", label,
                           f"modeled claim \"{k}\" stated without a hedge",
                           "Modeled numbers say so: \"~\", \"roughly\", \"modeled\"."))
            if tier == "measured" and first_measured_at is None:
                first_measured_at = i

        # PD006 unsourced numbers. Dedupe per face: a figure that shows up in
        # both the headline and a line is one finding, not two. The raise amount
        # on the ask slide is the ask itself, not a diligence stat -- a "$12M"
        # sitting next to "raising" carries no source tier, so exempt it (other
        # stats on the ask slide, like an ARR projection, are still checked).
        # A number is sourced only if a present claim key vouches for that exact
        # figure, matched as a whole token. Substring matching would let an
        # "85% gross retention" claim silently source a bare "5%" elsewhere on
        # the face, hiding a genuinely unsourced number.
        sourced = set()
        for k in present_keys:
            sourced.update(_claim_numbers(k))
        # The raise amount on the ask slide is the ask itself, not a diligence
        # stat, so exempt the $ figure that shares a line with "rais(e|ing)", but
        # only that figure, not every $ on the face. An unsourced traction $ stat
        # elsewhere on the ask slide is still flagged.
        raise_tokens: set[str] = set()
        if arc == "ask":
            for ln in [headline] + lines:
                if re.search(r"rais(e|ing)", ln, re.I):
                    raise_tokens.update(t for t in _claim_numbers(ln)
                                        if t.lstrip().startswith("$"))
        for tok in dict.fromkeys(_claim_numbers(face)):
            if tok in sourced:
                continue
            if tok in raise_tokens:
                continue
            f(_finding("PD006", "error", label,
                       f"unsourced number: \"{tok}\"",
                       "Add it to `claims` as measured / attested / public / "
                       "modeled, or delete it. Unsourced numbers sink decks."))

        # PD007 entity discipline
        for name, policy in entities.items():
            if name in face:
                if policy == "anonymize":
                    f(_finding("PD007", "error", label,
                               f"\"{name}\" is marked anonymize",
                               "Describe the category, not the company."))
                elif policy == "named-ok":
                    # Dedupe per face: a named company that shares a line with a
                    # figure is one finding, even when it recurs across lines, the
                    # same way PD006 dedupes its numbers per face.
                    if any(name in ln and _claim_numbers(ln)
                           for ln in [headline] + lines):
                        f(_finding("PD007", "warn", label,
                                   f"\"{name}\" shares a line with a figure",
                                   "Logos without numbers, numbers without logos."))

        # PD010 notes are a talk track, not a rulebook
        if notes and NOTES_POLICY.search(notes):
            f(_finding("PD010", "error", label,
                       "policy language in speaker notes",
                       "Notes carry what you say on stage. Rules live elsewhere."))

        # PD011 the platform-risk answer
        if arc == "competition" and not PLATFORM_RISK.search(face):
            f(_finding("PD011", "warn", label,
                       "competition slide never answers platform risk",
                       "Answer \"why not the platform / model providers?\" "
                       "before an investor asks it."))

    # ---- deck-level rules ------------------------------------------------
    present = {s.get("arc") for s in slides}
    for arc in ARC:
        if arc not in present:
            sev = "warn" if arc in {"purpose", "problem", "why-now", "competition", "ask"} else "info"
            f(_finding("PD008", sev, "deck", f"missing {arc} slide",
                       "The Sequoia arc earns its reputation. Cover it or cut it knowingly."))
    if len(slides) > 12:
        f(_finding("PD008", "warn", "deck",
                   f"{len(slides)} slides; partners decide early",
                   "12 max. Everything else is appendix."))

    # PD009 early exit: strongest evidence up front
    if first_measured_at is not None and first_measured_at > 3:
        f(_finding("PD009", "warn", "deck",
                   f"first measured number appears on slide {first_measured_at}",
                   "A 5-minute read must hit real evidence by slide 3."))
    if first_measured_at is None and claims:
        f(_finding("PD009", "info", "deck", "no measured-tier claims anywhere",
                   "Modeled-only decks read as hopes. Measure something."))

    # PD014 the retention answer: a growth story with no retention is a leaky
    # bucket. Acquisition poured into low retention compounds to near zero.
    all_faces = " ".join(_face_text(s) for s in slides).lower()
    retention_words = ("retention", "retain", "renewal", "renew", "expansion",
                       "nrr", "net revenue retention", "net dollar retention",
                       "churn", "second build", "comes back")
    if slides and not any(w in all_faces for w in retention_words):
        f(_finding("PD014", "warn", "deck",
                   "no slide addresses retention, expansion, or renewal",
                   "Growth without retention is a leaky bucket. Name the retention "
                   "metric (NRR, second use, expansion) on a face."))

    # PD015 the wedge: selling to "everyone" is no first buyer.
    if slides and EVERYONE.search(all_faces):
        f(_finding("PD015", "warn", "deck",
                   "sells to \"everyone\" -- no specific wedge or first buyer",
                   "Investors fund a wedge, not a market. Name the first 25 buyers: "
                   "the role and the segment, not \"any team\"."))

    per_rule: dict[str, int] = defaultdict(int)
    for x in findings:
        per_rule[x["rule"]] += DEDUCTION[x["severity"]]
    total = sum(min(v, RULE_CAP) for v in per_rule.values())
    score = max(0, 100 - total)
    return {"score": score, "grade": grade(score),
            "dimensions": _dimension_summary(findings), "findings": findings}


def _dimension_summary(findings: list[dict]) -> dict:
    """Roll the findings up to the four dimensions a founder is judged on, so the
    readout leads with the strategic gaps, not the format nitpicks."""
    out = {}
    for dim in ("story", "diligence", "questions", "ask"):
        fs = [f for f in findings if DIMENSION.get(f["rule"]) == dim]
        errs = sum(1 for f in fs if f["severity"] == "error")
        warns = sum(1 for f in fs if f["severity"] == "warn")
        status = "solid" if not fs else ("gap" if errs else "soft")
        out[dim] = {"label": DIMENSION_LABEL[dim], "status": status,
                    "errors": errs, "warns": warns,
                    "rules": sorted({f["rule"] for f in fs})}
    return out


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
