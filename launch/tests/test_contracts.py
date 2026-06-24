"""The canonical contracts: stage order, event mapping, phases, gates."""

from activation import contracts as c
from activation.capture.backends import get_backend


def test_stage_order():
    assert c.STAGES == [
        "touchpoint", "signup", "first_call", "first_build",
        "second_build", "weekly_active", "production", "handoff",
    ]


def test_stage_for():
    assert c.stage_for("api_key_created") == "second_build"  # the commitment signal
    assert c.stage_for("api_call") == "first_call"
    assert c.stage_for("tokens") is None  # volume-only, crosses no milestone


def test_phase_for():
    assert c.phase_for("first_call") == "Try"
    assert c.phase_for("first_build") == "Adopt"
    assert c.phase_for("second_build") == "Build"
    assert c.phase_for("production") == "Monetize"


def test_gates():
    assert (c.ALWAYS, c.ASK, c.NEVER) == ("always", "ask", "never")


def test_unknown_backend_fails_loud():
    import pytest

    with pytest.raises(ValueError, match="unknown ACTIVATION_BACKEND"):
        get_backend("posthoggg")
