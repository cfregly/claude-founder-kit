"""Run with: python -m pytest, or python tests/test_rules.py (stdlib only)."""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from deslop.rules import RULES, grade, lint, lint_html, lint_text, load_config

EXAMPLES = pathlib.Path(__file__).resolve().parent.parent / "examples"


def load(name):
    return (EXAMPLES / name).read_text()


def test_canonical_ruleset_loads():
    assert RULES["buzzwords"] and RULES["phrases"] and RULES["visual"]["blacklist"]
    assert RULES["draft_markers"]


def test_sloppy_prose_fails():
    findings = lint_text(load("sloppy.md"))
    rules = {f["rule"] for f in findings}
    for must in ("DS002", "DS003", "DS004", "DS005"):
        assert must in rules, f"{must} missing from {rules}"


def test_clean_prose_is_grade_a():
    report = lint(load("clean.md"))
    assert report["prose_score"] == 100 and not report["findings"], report["findings"]


def test_buzzword_suffix_is_caught():
    rules = {f["rule"] for f in lint_text("This significantly leverages synergies.")}
    assert "DS002" in rules


def test_not_x_but_y_framing():
    rules = {f["rule"] for f in lint_text("It's not a tool, it's a platform.")}
    assert "DS004" in rules


def test_em_dash_is_caught():
    assert any(f["rule"] == "DS001" for f in lint_text("We shipped it — fast."))


def test_draft_marker_is_caught():
    assert any(f["rule"] == "DS006" for f in lint_text("TODO: write the quickstart."))


def test_unfinished_template_phrase_is_caught():
    rules = {f["rule"] for f in lint_text("Add the marketplace (once this repo has a remote).")}
    assert "DS006" in rules


def test_angle_bracket_placeholder_is_caught():
    rules = {f["rule"] for f in lint_text("Run: marketplace add <your-org>/repo here.")}
    assert "DS006" in rules


def test_clean_prose_has_no_draft_marker():
    assert not any(f["rule"] == "DS006" for f in lint_text("We shipped the linter today."))


def test_code_blocks_are_not_linted_as_prose():
    # A buzzword and a placeholder inside code must not fire prose rules; that
    # keeps deslop usable as a README gate (install snippets are not prose).
    md = "Real prose here.\n\n```bash\nclaude plugin add <your-org>/x  # leverage\n```\n"
    rules = {f["rule"] for f in lint_text(md)}
    assert "DS002" not in rules and "DS006" not in rules


def test_visual_slop_detected():
    rules = {f["rule"] for f in lint_html(load("sloppy_landing.html"))}
    assert "DS010" in rules  # purple palette
    assert "DS011" in rules  # centered everything
    assert "DS012" in rules  # emoji
    assert "DS013" in rules  # border-left card


def test_clean_palette_not_flagged():
    # Anthropic clay + warm grays: no purple, no emoji, one centered title.
    html = "<style>body{background:#CC785C} h1{text-align:center}</style><h1>Hi</h1>"
    rules = {f["rule"] for f in lint_html(html)}
    assert "DS010" not in rules and "DS011" not in rules


def test_desloprc_allows_blessed_words_and_disabled_rules():
    text = "Our robust pipeline. The bottom line is it ships."
    # Without config: robust (DS002) and "the bottom line" (DS003) both fire.
    base = {f["rule"] for f in lint_text(text)}
    assert "DS002" in base and "DS003" in base
    # With a config that blesses "robust" and the phrase, both are suppressed.
    cfg = {"allow_words": ["robust"], "allow_phrases": ["the bottom line"],
           "disable_rules": set()}
    allowed = {f["rule"] for f in lint_text(text, cfg)}
    assert "DS002" not in allowed and "DS003" not in allowed


def test_disable_rules_suppresses_a_visual_rule():
    html = '<div class="card" style="border-left: 3px solid #333">Hi</div>'
    assert "DS013" in {f["rule"] for f in lint_html(html)}
    assert "DS013" not in {f["rule"] for f in lint_html(html, {"disable_rules": {"DS013"}})}


def test_load_config_defaults_when_no_rc():
    cfg = load_config("/nonexistent-dir-xyz")
    assert cfg["allow_words"] == [] and cfg["disable_rules"] == set()


def test_grade_boundaries():
    assert grade(90) == "A" and grade(80) == "B" and grade(49) == "F"


# --- evasion-closing regression tests from the adversarial pass.

def test_emoji_in_prose_is_flagged_ds007():
    assert "DS007" in {f["rule"] for f in lint_text("We ship value fast 🚀🔥 every day.")}


def test_horizontal_bar_and_figure_dash_are_caught():
    # The em/en evader: U+2015 horizontal bar and U+2012 figure dash.
    assert "―" in RULES["dashes"] and "‒" in RULES["dashes"]
    assert any(f["rule"] == "DS001" for f in lint_text("Results matter ― always."))


def test_spaced_buzzword_variant_is_caught():
    # "cutting edge" (spaced) must fire like "cutting-edge" (hyphenated).
    assert "DS002" in {f["rule"] for f in lint_text("We build cutting edge tools.")}
    assert "DS002" in {f["rule"] for f in lint_text("Our cutting-edge stack.")}


def test_isnt_contraction_framing_is_caught():
    assert "DS004" in {f["rule"] for f in lint_text("It isn't just a tool, it's a movement.")}


def test_purple_caught_across_css_formats():
    # Real landing pages set the #1 AI tell via rgb()/hsl()/Tailwind, not just hex.
    for css in ("style=\"background:rgb(124,58,237)\"",
                "style=\"background:hsl(258,90%,66%)\"",
                "class=\"bg-gradient-to-r from-purple-500 to-indigo-600\""):
        assert "DS010" in {f["rule"] for f in lint_html(f"<div {css}>Hi</div>")}, css


def test_blue_clay_and_gray_not_flagged_as_purple():
    for css in ("style=\"background:rgb(37,99,235)\"",   # blue
                "style=\"background:#CC785C\"",           # clay
                "style=\"background:hsl(258,5%,50%)\"",   # desaturated gray
                "class=\"bg-blue-500\""):
        assert "DS010" not in {f["rule"] for f in lint_html(f"<div {css}>Hi</div>")}, css


def test_indigo_hex_flagged_as_purple():
    # indigo-600 #4F46E5 is a canonical AI-slop color the hex path used to miss:
    # its low red made the violet heuristic skip it.
    assert "DS010" in {f["rule"] for f in lint_html('<div style="background:#4F46E5">Hi</div>')}


def test_centered_everything_caught_in_tailwind_and_flexbox():
    tw = '<a class="text-center"></a><b class="mx-auto"></b><i class="justify-center"></i>'
    assert "DS011" in {f["rule"] for f in lint_html(tw)}


def test_single_centered_element_is_not_flagged():
    assert "DS011" not in {f["rule"] for f in lint_html('<h1 class="text-center">Hero</h1>')}


def test_tailwind_left_border_card_caught():
    assert "DS013" in {f["rule"] for f in lint_html('<div class="border-l-4 border-purple-500">x</div>')}


# --- the optional Claude judge. Offline only: these prove the fallback and that
# the advisory pass never changes the deterministic score or exit code. The live
# call is verified by hand with a key, the way the README shows.

def test_judge_falls_back_without_a_key():
    from deslop import judge  # import first so its one-time load_dotenv runs now
    saved = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        out = judge.judge_text("Our platform delivers value across many use cases.")
        assert out["live"] is False
        assert out["findings"] == []
        assert out["model"] == "claude-opus-4-8"
    finally:
        if saved is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved


def test_judge_is_offline_for_empty_text():
    from deslop import judge
    out = judge.judge_text("   ")
    assert out["live"] is False and out["findings"] == []


def test_judge_is_a_noop_when_the_sdk_is_missing():
    from deslop import judge
    saved = judge.Anthropic
    judge.Anthropic = None
    os.environ["ANTHROPIC_API_KEY"] = "unused-in-this-test"
    try:
        assert judge.judge_text("Our platform delivers value.")["live"] is False
    finally:
        judge.Anthropic = saved
        os.environ.pop("ANTHROPIC_API_KEY", None)


def test_cli_judge_does_not_change_the_exit_code():
    # --judge is advisory: it must not move the deterministic exit code. Force the
    # offline judge path (Anthropic = None) so this never touches the network.
    from deslop import __main__ as cli
    from deslop import judge
    saved = judge.Anthropic
    judge.Anthropic = None
    try:
        plain = cli.main([str(EXAMPLES / "clean.md")])
        judged = cli.main([str(EXAMPLES / "clean.md"), "--judge"])
        assert plain == judged
    finally:
        judge.Anthropic = saved


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
