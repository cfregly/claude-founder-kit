"""Offline tests for the company router: classify by signal, draft into the outbox. No key, no network."""

from activation.route import router


def test_classify_routes_by_signal():
    assert router.classify("AI agent that rolls up usage across every account")[0] == "ptc"
    assert router.classify("answers questions over your contracts and legal documents")[0] == "citations"
    assert router.classify("a collaborative editor for product teams")[0] == "unrouted"


def test_route_drafts_into_the_outbox(tmp_path):
    batch = tmp_path / "batch.csv"
    batch.write_text(
        "company,first_name,one_liner\n"
        "Acme,Sam,incident response agent that triages logs and traces across services\n"
        "Docly,Lee,answers questions over your clinical records and policy documents\n"
        "Vellum,Alex,a collaborative editor for product teams\n"
    )
    outbox = tmp_path / "outbox"
    summary = router.route(batch, outbox=outbox)

    assert summary["total"] == 3
    assert summary["ptc"] == 1 and summary["citations"] == 1 and summary["unrouted"] == 1

    acme = (outbox / "acme.ptc.md").read_text()
    assert "Hey Sam," in acme and "Token MINNing" in acme
    docly = (outbox / "docly.citations.md").read_text()
    assert "Hey Lee," in docly and "grounded answers" in docly
    # the first-name placeholder is always filled, and the unrouted company gets no draft
    assert "{first_name}" not in acme and "{first_name}" not in docly
    assert not (outbox / "vellum.ptc.md").exists() and not (outbox / "vellum.citations.md").exists()


def test_route_is_deterministic_and_offline(tmp_path):
    """The router is the deterministic spine: same batch, same routing, no key needed."""
    batch = tmp_path / "b.csv"
    batch.write_text("company,one_liner\nA,usage analytics agent across accounts\n")
    a = router.route(batch, outbox=tmp_path / "o1")
    b = router.route(batch, outbox=tmp_path / "o2")
    assert a["routed"][0]["brief"] == b["routed"][0]["brief"] == "ptc"
