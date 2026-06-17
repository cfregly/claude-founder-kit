"""Run with: python -m tests.test_rules (stdlib only)."""

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pitch_lint.rules import grade, lint_deck

EXAMPLES = pathlib.Path(__file__).resolve().parent.parent / "examples"


def load(name):
    return json.loads((EXAMPLES / name).read_text())


def test_sloppy_deck_fails():
    r = lint_deck(load("sloppy_deck.json"))
    assert r["grade"] == "F", r["score"]
    rules = {f["rule"] for f in r["findings"]}
    # every signature failure mode must fire
    for must in ("PD001", "PD003", "PD004", "PD005", "PD006", "PD007", "PD010"):
        assert must in rules, f"{must} missing from {rules}"


def test_sharp_deck_is_clean():
    r = lint_deck(load("sharp_deck.json"))
    assert r["score"] == 100 and not r["findings"], r["findings"]


def test_unsourced_number_is_an_error():
    deck = {"slides": [{"arc": "market", "headline": "Big",
                        "lines": ["$50B market, 40% CAGR"]}]}
    rules = {f["rule"]: f["severity"] for f in lint_deck(deck)["findings"]}
    assert rules.get("PD006") == "error"


def test_modeled_without_hedge_warns():
    deck = {"claims": {"$140K": "modeled"},
            "slides": [{"arc": "business-model", "headline": "Unit economics",
                        "lines": ["$140K ARR per account"]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD006" in rules


def test_platform_risk_required_on_competition():
    deck = {"slides": [{"arc": "competition", "headline": "A 2x2 we win",
                        "lines": ["We beat everyone on both axes, 10 ways"]}]}
    msgs = [f["rule"] for f in lint_deck(deck)["findings"]]
    assert "PD011" in msgs


def test_platform_word_alone_does_not_satisfy_platform_risk():
    # "We are a platform" is positioning, not an answer to platform risk, so
    # PD011 must still fire on a competition slide that only names the word.
    deck = {"slides": [{"arc": "competition", "headline": "We are a platform company",
                        "lines": ["We win on features across the board."]}]}
    assert "PD011" in {f["rule"] for f in lint_deck(deck)["findings"]}


def test_emoji_on_face_warns():
    deck = {"slides": [{"arc": "product", "headline": "Shipped the capture app 🚀",
                        "lines": ["Live now."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD012" in rules


def test_generic_template_copy_warns():
    deck = {"slides": [{"arc": "purpose",
                        "headline": "Welcome to the all-in-one solution",
                        "lines": ["For every team."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD013" in rules


def test_sharp_deck_has_no_emoji_or_generic_findings():
    r = lint_deck(load("sharp_deck.json"))
    rules = {f["rule"] for f in r["findings"]}
    assert "PD012" not in rules and "PD013" not in rules


def test_findings_carry_auto_vs_ask_fix_kind():
    deck = {"slides": [{"arc": "purpose", "headline": "Our seamless platform 🚀",
                        "lines": ["We are passionate about synergy."]}]}
    by_rule = {f["rule"]: f["fix_kind"] for f in lint_deck(deck)["findings"]}
    assert by_rule["PD003"] == "auto"   # delete the banned word: mechanical
    assert by_rule["PD012"] == "auto"   # cut the emoji: mechanical
    assert by_rule.get("PD005", "ask") == "ask"  # add a number: judgment


def test_retention_rule_flags_a_deck_with_no_retention():
    deck = {"slides": [{"arc": "purpose", "headline": "We help teams ship",
                        "lines": ["We acquire users fast."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD014" in rules


def test_retention_rule_satisfied_when_retention_present():
    deck = {"slides": [{"arc": "business-model", "headline": "Net revenue retention is the engine",
                        "lines": ["Accounts expand seat by seat."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD014" not in rules


def test_grade_boundaries():
    assert grade(90) == "A" and grade(80) == "B" and grade(49) == "F"


# --- calibration regression tests: real decks broke the linter until these held.

def test_version_and_spec_numbers_are_not_unsourced():
    # "Python 3.11", "SOC 2", "GPT-4" are specs and names, not traction stats.
    deck = {"slides": [{"arc": "product", "headline": "Ships on every push",
                        "lines": ["Runs on Python 3.11 with SOC 2 Type II and GPT-4."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD006" not in rules


def test_raise_amount_on_ask_is_exempt():
    # The raise is the ask, not a number you source as measured/public/modeled.
    deck = {"slides": [{"arc": "ask", "headline": "The ask",
                        "lines": ["Raising $12M to reach the next milestone."]}]}
    rules = {f["rule"] for f in lint_deck(deck)["findings"]}
    assert "PD006" not in rules


def test_other_stats_on_ask_slide_still_checked():
    # Exempting the raise must not exempt an unsourced traction stat beside it.
    deck = {"slides": [{"arc": "ask", "headline": "The ask",
                        "lines": ["Raising $12M on the back of 80% gross margins."]}]}
    f006 = [f for f in lint_deck(deck)["findings"] if f["rule"] == "PD006"]
    assert len(f006) == 1 and "80%" in f006[0]["message"]


def test_ask_slide_exempts_only_the_raise_dollar():
    # The raise ($ on a "raising" line) is exempt, but another unsourced $ stat
    # on the ask slide is still flagged.
    deck = {"slides": [{"arc": "ask", "headline": "The ask",
                        "lines": ["Raising $12M for the next push.",
                                  "We have $4M in signed pipeline already."]}]}
    f006 = [f for f in lint_deck(deck)["findings"] if f["rule"] == "PD006"]
    msgs = " ".join(f["message"] for f in f006)
    assert "$4M" in msgs and "$12M" not in msgs, msgs


def test_unsourced_number_deduped_per_slide():
    # A figure in both the headline and a line is one finding, not two.
    deck = {"slides": [{"arc": "market", "headline": "We chase $5M",
                        "lines": ["$5M is the wedge."]}]}
    f006 = [f for f in lint_deck(deck)["findings"] if f["rule"] == "PD006"]
    assert len(f006) == 1


def test_pd007_named_company_deduped_per_face():
    # A named-ok company sharing a line with a figure is one finding per face,
    # not one per line, the same way PD006 dedupes its numbers per face.
    deck = {"entities": {"Acme": "named-ok"},
            "slides": [{"arc": "traction", "headline": "Acme signed for $2M",
                        "lines": ["Acme expanded to $3M", "Acme renewed at $4M"]}]}
    f007 = [f for f in lint_deck(deck)["findings"] if f["rule"] == "PD007"]
    assert len(f007) == 1, f007


def test_nine_word_headline_is_info_not_warn():
    deck = {"slides": [{"arc": "purpose",
                        "headline": "one two three four five six seven eight nine",
                        "lines": ["short line"]}]}
    f001 = [f for f in lint_deck(deck)["findings"] if f["rule"] == "PD001"]
    assert f001 and f001[0]["severity"] == "info"


def test_per_rule_cap_bounds_one_category():
    # Two unsourced numbers and five unsourced numbers both saturate the PD006
    # cap, so the same deck shape scores identically -- one weak area cannot
    # alone floor a deck at zero.
    base = lambda lines: {"slides": [{"arc": "market", "headline": "Market", "lines": lines}]}
    two = lint_deck(base(["$10M and 20% here"]))["score"]
    five = lint_deck(base(["$10M, 20%, 30%, 40%, 50% here"]))["score"]
    assert two == five


def test_realistic_deck_lands_in_the_middle_band():
    # The bundled realistic deck must score like a real founder deck: not the
    # strawman F, not the engineered 100. A linter that cannot separate a strong
    # deck from a rough one is useless; this is the regression that proves it can.
    r = lint_deck(load("realistic_deck.json"))
    assert 65 <= r["score"] < 90 and r["grade"] in ("B", "C"), r["score"]


def test_real_world_number_formats_are_claimable():
    from pitch_lint.rules import _claim_numbers
    nums = _claim_numbers("2,400 customers, 10,000 users, €48M, £1.2bn, 99.9% uptime")
    for tok in ("2,400", "10,000", "€48M", "£1.2bn", "99.9%"):
        assert tok in nums, (tok, nums)


def test_spec_and_rating_tokens_are_not_claimable():
    from pitch_lint.rules import _claim_numbers
    # GPT-4o, Top 3, #1, 4.8/5, 24/7, Python 3.11 are specs and ratings, not stats.
    assert _claim_numbers("GPT-4o, Top 3, #1 on G2, 4.8/5, 24/7, Python 3.11") == []


def test_unicode_multiplier_credential_is_not_a_traction_claim():
    from pitch_lint.rules import _claim_numbers
    # "3x O'Reilly author" / "2x founder" use the unicode multiply as a credential
    # (three-time, two-time), not a multiple to source. The unicode sign stays
    # exempt so it never flags a bio line; ASCII "10x faster" is still a claim.
    assert _claim_numbers("3× O'Reilly author and 2× founder") == []
    assert "10x" in _claim_numbers("A clean 10x improvement.")


def test_european_period_thousands_claimable_but_versions_exempt():
    from pitch_lint.rules import _claim_numbers
    assert "1.234.567" in _claim_numbers("We signed 1.234.567 users in Germany.")
    # A single period group (2.345, 3.11) is a version, not a thousands figure.
    assert _claim_numbers("Runs on build 2.345 and Python 3.11.") == []


def test_comma_and_bn_numbers_source_round_trip():
    deck = {"claims": {"2,400 customers": "measured", "£1.2bn TAM": "public"},
            "slides": [{"arc": "market", "headline": "Market",
                        "lines": ["A £1.2bn TAM with 2,400 customers, plus 9,000 leads"]}]}
    f006 = [x["message"] for x in lint_deck(deck)["findings"] if x["rule"] == "PD006"]
    assert len(f006) == 1 and '"9,000"' in f006[0]  # claimed ones sourced; 9,000 flagged


def test_a_claim_does_not_source_a_substring_number():
    # An "85%" claim must not silently source a bare "5%" elsewhere on the face.
    # Substring matching used to hide a genuinely unsourced number.
    deck = {"claims": {"85% gross retention": "measured"},
            "slides": [{"arc": "business-model", "headline": "Retention",
                        "lines": ["85% gross retention, but only 5% upgrade"]}]}
    f006 = [x for x in lint_deck(deck)["findings"] if x["rule"] == "PD006"]
    assert len(f006) == 1 and '"5%"' in f006[0]["message"], f006


def test_pd015_flags_selling_to_everyone():
    deck = {"slides": [{"arc": "purpose", "headline": "A platform for everyone",
                        "lines": ["Built for any company and every team."]}]}
    assert "PD015" in {f["rule"] for f in lint_deck(deck)["findings"]}


def test_pd015_quiet_with_a_specific_wedge():
    deck = {"slides": [{"arc": "purpose", "headline": "Resolve support tickets",
                        "lines": ["For heads of support at Series B-D SaaS companies."]}]}
    assert "PD015" not in {f["rule"] for f in lint_deck(deck)["findings"]}


def test_report_groups_findings_into_investor_dimensions():
    # The readout leads with the four dimensions a founder is judged on. A
    # competition slide that dodges platform risk lands under "the questions".
    r = lint_deck({"slides": [{"arc": "competition", "headline": "We win",
                               "lines": ["We beat everyone, ten ways over and out."]}]})
    assert set(r["dimensions"]) == {"story", "diligence", "questions", "ask"}
    assert r["dimensions"]["questions"]["warns"] >= 1  # the platform-risk miss


# --- the optional Claude narrative judge. Offline only: these prove the fallback
# and that the advisory read never changes the deterministic score or exit code.
# The live call is verified by hand with a key, the way the README shows.

def test_judge_falls_back_without_a_key():
    from pitch_lint import judge  # import first so its one-time load_dotenv runs now
    saved = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        out = judge.judge_deck(load("sharp_deck.json"))
        assert out["live"] is False
        assert out["model"] == "claude-opus-4-8"
    finally:
        if saved is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved


def test_judge_is_a_noop_when_the_sdk_is_missing():
    from pitch_lint import judge
    saved = judge.Anthropic
    judge.Anthropic = None
    os.environ["ANTHROPIC_API_KEY"] = "unused-in-this-test"
    try:
        assert judge.judge_deck(load("sharp_deck.json"))["live"] is False
    finally:
        judge.Anthropic = saved
        os.environ.pop("ANTHROPIC_API_KEY", None)


def test_judge_offline_for_an_empty_deck():
    from pitch_lint import judge
    assert judge.judge_deck({"slides": []})["live"] is False


def test_render_marks_skipped_when_not_live():
    from pitch_lint import judge
    assert "skipped" in judge.render({"live": False})


def test_cli_judge_does_not_change_the_exit_code():
    # The narrative read is advisory: it must not move the deterministic exit
    # code, whether it runs by default, is forced with --judge, or is skipped
    # with --no-judge. Force the offline judge path (Anthropic = None) so this
    # never touches the network.
    from pitch_lint import __main__ as cli, judge
    saved = judge.Anthropic
    judge.Anthropic = None
    try:
        default = cli.main([str(EXAMPLES / "sharp_deck.json")])
        judged = cli.main([str(EXAMPLES / "sharp_deck.json"), "--judge"])
        skipped = cli.main([str(EXAMPLES / "sharp_deck.json"), "--no-judge"])
        assert default == judged == skipped == 0
    finally:
        judge.Anthropic = saved


def test_cli_no_judge_skips_the_read_even_with_a_key():
    # --no-judge must skip the read even when a key is set, and must not change
    # the deterministic exit code. Stays offline: judge_deck is patched on the
    # judge module (the CLI imports it from there at call time), so it never
    # constructs a client.
    from pitch_lint import __main__ as cli, judge
    saved_key = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = "unused-in-this-test"
    called = {"judge": False}
    saved_judge, saved_avail = judge.judge_deck, judge.available

    def _record(*a, **k):  # the read must not run under --no-judge
        called["judge"] = True
        return {"live": False, "model": judge.MODEL}

    judge.judge_deck = _record
    judge.available = lambda: True  # pretend a live judge is possible
    try:
        code = cli.main([str(EXAMPLES / "sharp_deck.json"), "--no-judge"])
        assert code == 0
        assert called["judge"] is False
    finally:
        judge.judge_deck, judge.available = saved_judge, saved_avail
        if saved_key is None:
            os.environ.pop("ANTHROPIC_API_KEY", None)
        else:
            os.environ["ANTHROPIC_API_KEY"] = saved_key


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
