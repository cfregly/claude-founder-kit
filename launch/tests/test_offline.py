"""The offline contract: the deterministic spine runs with no key, the generative
steps raise loud.

Two halves, both verified here. The deterministic spine (capture, measure, the
gate, the report template) is the receipt and the CI gate, so it runs with no key
and no SDK. The generative steps (enrich, decide, draft) run Claude on every run,
so with no key they raise a clear RuntimeError instead of degrading to a quiet
fallback. CI does not install the anthropic SDK, so each missing-key test forces
the SDK to look present and asserts the missing-KEY message, not the missing-SDK
one.
"""

import pytest

from activation import pipeline
from activation.decide import motion
from activation.draft import nudges
from activation.enrich import research
from activation.platform import client


class _SDKPresent:
    """A non-None stand-in for anthropic.Anthropic, so the missing-key tests
    exercise the missing-KEY path even where the real SDK is not installed."""


def _no_key_sdk_present(monkeypatch):
    """No key, but the SDK looks installed: the missing-KEY path."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client, "Anthropic", _SDKPresent)
    assert client.available() is False  # available() is still False with no key


def _no_sdk(monkeypatch):
    """No SDK at all: the missing-SDK path. Key state does not matter."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client, "Anthropic", None)


# The generative steps raise loud, not a silent skip.

def test_require_client_raises_on_missing_key(monkeypatch):
    _no_key_sdk_present(monkeypatch)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        client.require_client()


def test_require_client_raises_on_missing_sdk(monkeypatch):
    _no_sdk(monkeypatch)
    with pytest.raises(RuntimeError, match="anthropic SDK"):
        client.require_client()


def test_enrich_raises_without_key(monkeypatch):
    _no_key_sdk_present(monkeypatch)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        research.enrich_pqas(["acct_02", "acct_03"], cohort_name="t")


def test_decide_raises_without_key(monkeypatch):
    _no_key_sdk_present(monkeypatch)
    readout = {"biggest_dropoff": {"from": "first_build", "to": "second_build", "lost_pct": 0.38}}
    plan = {"proposed": [{"id": "second_build_nudge", "motion": "Send the nudge.", "moves": "time-to-second-build"}]}
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        motion.decide_motion(readout, plan)


def test_draft_raises_without_key(monkeypatch):
    _no_key_sdk_present(monkeypatch)
    plan = {"proposed": [{"id": "x", "motion": "m", "moves": "v", "rationale": "r"}]}
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        nudges.draft_nudges(plan)


def test_draft_no_proposed_actions_is_not_a_call(monkeypatch):
    """Nothing proposed means nothing to draft. That is not a Claude call, so it
    does not raise even with no key."""
    _no_key_sdk_present(monkeypatch)
    out = nudges.draft_nudges({"proposed": []})
    assert out["drafts"] == {}


def test_pipeline_live_raises_without_key(monkeypatch):
    """The live path runs Claude, so with no key it raises, not a quiet downgrade."""
    _no_key_sdk_present(monkeypatch)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        pipeline.run(live=True)


# The deterministic spine runs offline: this is what make demo and CI rely on.

def test_pipeline_offline_produces_the_report(monkeypatch):
    _no_sdk(monkeypatch)
    result = pipeline.run()  # live=False, the deterministic spine
    assert "ACTIVATION" in result["report"]
    assert result["decision"] is None  # the generative steps did not run
