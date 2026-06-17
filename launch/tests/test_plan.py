"""The gate ledger: what ran on its own, what waits, what is refused, and the audit."""

import pytest

from activation import pipeline
from activation.capture import cohort
from activation.measure import metrics
from activation.operate import plan as planning


@pytest.fixture(scope="module")
def p():
    rows = pipeline.capture_rows()
    return planning.plan(metrics.summarize(cohort.to_cohort(rows, "test")))


def test_audit_passes(p):
    assert planning.audit(p) == []


def test_did_are_internal_and_always(p):
    assert p["did"]
    for a in p["did"]:
        assert a["gate"] == "always"
        assert a["outward"] is False


def test_proposed_are_outward_and_ask(p):
    ids = {a["id"] for a in p["proposed"]}
    assert "second_build_nudge" in ids
    assert "pqa_handoff" in ids
    for a in p["proposed"]:
        assert a["gate"] == "ask"
        assert a["outward"] is True


def test_will_not_are_never(p):
    assert {a["id"] for a in p["will_not"]} == {
        "auto_email", "auto_spend", "auto_post", "auto_credits", "auto_handoff"}
    for a in p["will_not"]:
        assert a["gate"] == "never"


def test_audit_catches_a_smuggled_outward_action(p):
    tampered = {"did": p["did"] + [{"id": "x", "gate": "always", "outward": True}]}
    assert planning.audit(tampered)  # the boundary catches it
