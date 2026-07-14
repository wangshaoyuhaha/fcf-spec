from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    REQUIRED_RESEARCH_WORKSPACE_PATHS,
    UNSAFE_HTTP_METHODS,
    build_overview_workspace_model,
    build_research_workspace_integration_acceptance,
)


def _model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-d6-final",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(_model())


def test_d6_final_acceptance_passes():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.status == "PASSED"
    assert acceptance.ok is True
    assert all(acceptance.checks.values())


def test_d6_all_eleven_workspaces_are_available():
    overview = build_overview_workspace_model(_model())

    assert overview.available_workspace_paths == (
        REQUIRED_RESEARCH_WORKSPACE_PATHS
    )
    assert overview.planned_workspace_paths == ()


def test_d6_all_workspaces_remain_read_only():
    application = _application()

    for method in UNSAFE_HTTP_METHODS:
        for path in REQUIRED_RESEARCH_WORKSPACE_PATHS:
            assert application.dispatch(method, path).status == 405


def test_d6_permanent_authority_boundary_is_preserved():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.paper_only is True
    assert acceptance.loopback_only is True
    assert acceptance.registered_artifact_only is True
    assert acceptance.operator_review_required is True
    assert acceptance.ai_advisory_only is True
    assert acceptance.deterministic_engine_authority is True


def test_d6_unknown_routes_fail_closed():
    application = _application()

    assert application.dispatch("GET", "/not-registered").status == 404
    assert application.dispatch("GET", "/../audit").status == 404
    assert application.dispatch("GET", "/%2e%2e/audit").status == 404


def test_d6_health_confirms_no_live_authority():
    response = _application().dispatch("GET", "/health")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert '"mode": "paper-only"' in body
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body
