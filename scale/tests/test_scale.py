"""The Scale-stage contract: the deterministic moat core runs offline and carries
the receipt; the Claude layer raises loud with no key.

Two halves, both verified here. The moat core (score_account, summarize) is stdlib
only and deterministic, so the same sample cohort gives the same readout every run.
The generative stage (the GTM motion and the moat narrative) runs Claude on every
run, so with no key it raises a clear RuntimeError instead of degrading to a quiet
fallback. CI does not install the anthropic SDK, so the missing-key test forces the
SDK to look present and asserts the missing-KEY message, not the missing-SDK one.
"""

import json
from pathlib import Path

import pytest

from scale.generate import gtm
from scale.measure import metrics
from scale.platform import client

COHORT = json.loads((Path(__file__).resolve().parent.parent
                     / "examples" / "cohort.json").read_text())


@pytest.fixture(scope="module")
def readout():
    return metrics.summarize(COHORT)


# The deterministic moat core: the receipt and the CI gate.

def test_moat_scores(readout):
    by_name = {s["name"]: s for s in readout["scores"]}
    assert by_name["acct_01"]["moat"] == 100
    assert by_name["acct_01"]["band"] == "deep"
    assert by_name["acct_05"]["moat"] == 64        # deep moat, but down spend
    assert by_name["acct_10"]["moat"] == 12        # shallow


def test_moat_distribution_and_median(readout):
    assert readout["moat_distribution"] == {"deep": 5, "forming": 3, "shallow": 2}
    assert readout["median_moat"] == 60.0


def test_gtm_ready_set(readout):
    # A deep moat, rising spend, and sustained weekly use. acct_04 (flat spend) and
    # acct_05 (down spend) are deep but not expansion-ready.
    assert readout["gtm_ready_accounts"] == ["acct_01", "acct_02", "acct_03"]
    assert readout["the_number"]["value"] == 3
    assert readout["the_number"]["deep_moats"] == 5


def test_compounding_data_set(readout):
    assert readout["compounding_data_accounts"] == [
        "acct_01", "acct_02", "acct_03", "acct_04", "acct_06"]


def test_clean_cohort_has_no_integrity_flags():
    assert metrics.data_integrity(COHORT["accounts"]) == []


# The Claude layer raises loud, not a silent skip.

class _SDKPresent:
    """A non-None stand-in for anthropic.Anthropic, so the missing-key tests
    exercise the missing-KEY path even where the real SDK is not installed."""


def _no_key_sdk_present(monkeypatch):
    """No key, but the SDK looks installed: the missing-KEY path."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client, "Anthropic", _SDKPresent)
    assert client.available() is False  # available() is still False with no key


def test_require_client_raises_on_missing_key(monkeypatch):
    _no_key_sdk_present(monkeypatch)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        client.require_client()


def test_gtm_layer_raises_without_key(monkeypatch, readout):
    """The GTM and moat-narrative step runs Claude, so with no key it raises a clear
    error naming the missing key, not a quiet downgrade."""
    _no_key_sdk_present(monkeypatch)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        gtm.gtm_and_moat(readout)
