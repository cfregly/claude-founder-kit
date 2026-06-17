"""The whole pipeline: deterministic, reproducible, and the report has its sections."""

from activation import contracts, pipeline
from activation.capture import queries


def test_event_count_and_funnel():
    rows = pipeline.capture_rows()
    assert len(rows) == 165
    q = {x["id"]: x["value"] for x in queries.run_all(rows)}
    assert q["Q9"] == 5  # the second-build commitment signal
    funnel = "/".join(str(q["Q11"][s]) for s in contracts.STAGES)
    assert funnel == "12/12/10/8/5/4/3/1"


def test_report_is_deterministic():
    assert pipeline.run()["report"] == pipeline.run()["report"]


def test_report_has_every_section():
    text = pipeline.run()["report"]
    for section in ["ACTIVATION", "RETENTION", "PIPELINE", "THE ONE MOTION",
                    "Ran on its own", "Waiting on you", "Will not do on its own"]:
        assert section in text
    assert "second-build nudge" in text  # the one motion for this cohort


def test_deltas_render_with_prev_state():
    prev = {"activation_rate": 0.62, "retention_rate": 0.57,
            "time_to_second_build_days": 9, "pqas_ready_for_handoff": ["acct_02"],
            "signups_total": 9}
    text = pipeline.run(prev_state=prev)["report"]
    assert "vs last week" in text
    assert "+5 pts" in text  # activation 67% against last week's 62%


def test_signals_match_the_funnel():
    rows = pipeline.capture_rows()
    sig = pipeline.signals_from(rows)
    assert sig["signups_total"] == 12
    assert sig["time_to_first_value_days"] == 2.0
