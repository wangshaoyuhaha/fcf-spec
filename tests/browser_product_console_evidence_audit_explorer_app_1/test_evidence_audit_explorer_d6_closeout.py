from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS,
    REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS,
    build_evidence_audit_explorer_integration_acceptance,
    build_research_workspace_integration_acceptance,
)


def _model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-evidence-d6-final",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(_model())


def test_d6_evidence_audit_final_acceptance_passes():
    acceptance = (
        build_evidence_audit_explorer_integration_acceptance(
            _application()
        )
    )

    assert acceptance.status == "PASSED"
    assert acceptance.ok is True
    assert all(acceptance.checks.values())


def test_d6_all_seven_evidence_routes_are_available():
    application = _application()

    assert REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS == (
        "/evidence",
        "/evidence/artifacts",
        "/evidence/lineage",
        "/evidence/risk",
        "/evidence/validation",
        "/evidence/review",
        "/evidence/archive",
    )

    for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
        response = application.dispatch("GET", path)
        assert response.status == 200


def test_d6_all_evidence_routes_remain_read_only():
    application = _application()

    for method in EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS:
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
            assert application.dispatch(
                method,
                path,
            ).status == 405


def test_d6_invalid_queries_fail_closed():
    application = _application()

    assert application.dispatch(
        "GET",
        "/evidence?execute=true",
    ).status == 400
    assert application.dispatch(
        "GET",
        "/evidence?limit=0",
    ).status == 400
    assert application.dispatch(
        "GET",
        "/evidence?artifact_ids=%ZZ",
    ).status == 400


def test_d6_permanent_authority_boundary_is_preserved():
    acceptance = (
        build_evidence_audit_explorer_integration_acceptance(
            _application()
        )
    )

    assert acceptance.paper_only is True
    assert acceptance.loopback_only is True
    assert acceptance.registered_artifact_only is True
    assert acceptance.read_only is True
    assert acceptance.operator_review_required is True
    assert acceptance.ai_advisory_only is True
    assert acceptance.deterministic_engine_authority is True


def test_d6_unknown_and_traversal_routes_fail_closed():
    application = _application()

    assert application.dispatch(
        "GET",
        "/evidence/not-registered",
    ).status == 404
    assert application.dispatch(
        "GET",
        "/evidence/../audit",
    ).status == 404
    assert application.dispatch(
        "GET",
        "/evidence/%2e%2e/audit",
    ).status == 404


def test_d6_health_confirms_no_live_authority():
    response = _application().dispatch("GET", "/health")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert '"mode": "paper-only"' in body
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body


def test_d6_research_workspace_acceptance_remains_passed():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.status == "PASSED"
    assert acceptance.ok is True
    assert all(acceptance.checks.values())
