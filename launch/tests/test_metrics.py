"""The measure stage reproduces the marquee numbers from the seed-7 cohort."""

import pytest

from activation import pipeline
from activation.capture import cohort
from activation.measure import metrics


@pytest.fixture(scope="module")
def readout():
    rows = pipeline.capture_rows()
    return metrics.summarize(cohort.to_cohort(rows, "test"))


def test_funnel_counts(readout):
    counts = {f["stage"]: f["count"] for f in readout["funnel"]}
    order = ["touchpoint", "signup", "first_call", "first_build",
             "second_build", "weekly_active", "production", "handoff"]
    assert [counts[s] for s in order] == [12, 12, 10, 8, 5, 4, 3, 1]


def test_rates(readout):
    assert readout["activation_rate"] == 0.67       # 8 builds / 12 signups
    assert readout["retention_rate"] == 0.62        # 5 second builds / 8 builds
    assert readout["engagement_retention"] == 0.5   # 4 weekly / 8 builds
    assert readout["time_to_second_build_days"] == 8


def test_biggest_leak(readout):
    d = readout["biggest_dropoff"]
    assert d["from"] == "first_build" and d["to"] == "second_build"
    assert d["lost_pct"] == 0.38  # 1 - 5/8


def test_pqas(readout):
    assert readout["pqas_ready_for_handoff"] == ["acct_02", "acct_03"]


def test_clean_cohort_has_no_integrity_flags(readout):
    issues = metrics.data_integrity(
        cohort.to_cohort(pipeline.capture_rows(), "test")["accounts"])
    assert issues == []
