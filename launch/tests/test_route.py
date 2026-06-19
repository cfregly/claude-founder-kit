"""Offline tests for the company router: classify by signal, draft into the outbox. No key, no network."""

from activation.route import router


def test_classify_routes_by_signal():
    assert router.classify("AI agent that rolls up usage across every account")[0] == "ptc"
    assert router.classify("answers questions over your contracts and legal documents")[0] == "citations"
    assert router.classify("a collaborative editor for product teams")[0] == "unrouted"


def test_route_drafts_into_the_outbox(tmp_path):
    batch = tmp_path / "batch.csv"
    batch.write_text(
        "# fictional sample cohort, placeholder names only\n"
        "company,first_name,one_liner\n"
        "Fabrikam,Sam,incident response agent that triages logs and traces across services\n"
        "Contoso,Lee,answers questions over your clinical records and policy documents\n"
        "Litware,Alex,a collaborative editor for product teams\n"
    )
    outbox = tmp_path / "outbox"
    summary = router.route(batch, outbox=outbox)

    # the leading comment line is skipped, not counted as a company
    assert summary["total"] == 3
    assert summary["ptc"] == 1 and summary["citations"] == 1 and summary["unrouted"] == 1

    fabrikam = (outbox / "fabrikam.ptc.md").read_text()
    assert "Hey Sam," in fabrikam and "Token MINNing" in fabrikam
    contoso = (outbox / "contoso.citations.md").read_text()
    assert "Hey Lee," in contoso and "grounded answers" in contoso
    # the opener is hyper-personalized to each company's use case within its segment
    assert "Quick tip for an agent that triages logs and traces across services." in fabrikam
    assert "Quick tip for a product that answers over clinical notes." in contoso
    # the first-name placeholder is always filled, and the unrouted company gets no draft
    assert "{first_name}" not in fabrikam and "{first_name}" not in contoso
    assert not (outbox / "litware.ptc.md").exists() and not (outbox / "litware.citations.md").exists()


def test_use_case_personalizes_within_segment():
    assert router.use_case("usage metering across accounts", "ptc") == "an agent that rolls up usage across accounts"
    assert router.use_case("contract review copilot", "citations") == "a product that answers over contracts"
    # an unmatched use case falls back to the segment default, never empty
    assert router.use_case("a generic helper bot", "ptc") == "an agent that calls a tool many times"


def test_body_anchors_are_present_in_the_templates():
    # the --refine deepening replaces these exact substrings; if a template drifts, this fails loud
    ptc = (router.EXAMPLES / "ptc-email.md").read_text()
    citations = (router.EXAMPLES / "citations-email.md").read_text()
    assert router.PTC_WORKLOAD_ANCHOR in ptc
    assert router.PTC_TOOL_ANCHOR in ptc
    assert router.CITATIONS_DOC_ANCHOR in citations


def test_apply_body_rewrites_only_the_anchors():
    draft = (
        "If your app calls your own tool to answer a question and that tool returns a lot of results, "
        "every result lands in context.\n"
        '{ "name": "query_region_sales", "input_schema": {} }\n'
        "| without PTC | 9,451 |\n"
    )
    out = router._apply_body(draft, "ptc", "your on-call agent queries logs and traces", "query logs")
    assert "your on-call agent queries logs and traces" in out
    assert "query_logs" in out and "query_region_sales" not in out  # spaces become underscores
    assert "9,451" in out  # the verified number is never touched

    cit = "When you answer over a contract, a policy, or a support doc, the source matters."
    out2 = router._apply_body(cit, "citations", "a clinical note or a patient record")
    assert "a clinical note or a patient record" in out2
    assert "a contract, a policy, or a support doc" not in out2


def test_apply_body_strips_dashes_and_semicolons():
    out = router._apply_body("over a contract, a policy, or a support doc.", "citations",
                             "a clinical note; a lab report — scanned")
    assert "—" not in out and ";" not in out


def test_route_is_deterministic_and_offline(tmp_path):
    """The router is the deterministic spine: same batch, same routing, no key needed."""
    batch = tmp_path / "b.csv"
    batch.write_text("company,one_liner\nA,usage analytics agent across accounts\n")
    a = router.route(batch, outbox=tmp_path / "o1")
    b = router.route(batch, outbox=tmp_path / "o2")
    assert a["routed"][0]["brief"] == b["routed"][0]["brief"] == "ptc"
