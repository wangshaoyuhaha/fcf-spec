from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    ConsoleResponse,
    REQUIRED_RESEARCH_WORKSPACE_PATHS,
    ResearchWorkspaceIntegrationAcceptance,
    UNSAFE_HTTP_METHODS,
    build_research_workspace_integration_acceptance,
)


def _model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-d5",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(_model())


def test_d5_integration_acceptance_passes_complete_console():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.ok is True
    assert acceptance.status == "PASSED"
    assert acceptance.route_paths == REQUIRED_RESEARCH_WORKSPACE_PATHS
    assert all(acceptance.checks.values())


def test_d5_all_registered_routes_support_get_and_head():
    application = _application()

    for path in REQUIRED_RESEARCH_WORKSPACE_PATHS:
        get_response = application.dispatch("GET", path)
        head_response = application.dispatch("HEAD", path)

        assert get_response.status == 200
        assert get_response.body
        assert head_response.status == 200
        assert head_response.body == b""
        assert head_response.headers == get_response.headers


def test_d5_all_registered_routes_reject_unsafe_methods():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    expected_count = (
        len(REQUIRED_RESEARCH_WORKSPACE_PATHS)
        * len(UNSAFE_HTTP_METHODS)
    )
    assert len(acceptance.write_statuses) == expected_count
    assert set(acceptance.write_statuses.values()) == {405}


def test_d5_navigation_is_complete_on_every_workspace():
    application = _application()

    for route in REQUIRED_RESEARCH_WORKSPACE_PATHS:
        body = application.dispatch("GET", route).body.decode("utf-8")
        for path in REQUIRED_RESEARCH_WORKSPACE_PATHS:
            assert body.count(f'href="{path}"') == 1


def test_d5_pages_expose_no_mutating_browser_controls():
    application = _application()

    for path in REQUIRED_RESEARCH_WORKSPACE_PATHS:
        body = application.dispatch("GET", path).body.decode(
            "utf-8"
        ).lower()
        assert "<form" not in body
        assert "<button" not in body
        assert "method=" not in body
        assert "<script" not in body


def test_d5_unknown_and_traversal_paths_fail_closed():
    application = _application()

    assert application.dispatch("GET", "/not-registered").status == 404
    assert application.dispatch("GET", "/../audit").status == 404
    assert application.dispatch("GET", "/%2e%2e/audit").status == 404


def test_d5_query_string_is_normalized_without_expanding_scope():
    application = _application()

    response = application.dispatch(
        "GET",
        "/audit?view=registered",
    )

    assert response.status == 200
    assert "Audit History" in response.body.decode("utf-8")


def test_d5_health_preserves_permanent_boundary():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.health_payload["status"] == "ok"
    assert acceptance.health_payload["mode"] == "paper-only"
    assert acceptance.health_payload["host_scope"] == "loopback-only"
    assert (
        acceptance.health_payload["operator_review_required"]
        is True
    )
    assert acceptance.health_payload["correlation_id"] == "corr-d5"


def test_d5_security_headers_are_present_on_every_workspace():
    application = _application()

    for path in REQUIRED_RESEARCH_WORKSPACE_PATHS:
        response = application.dispatch("GET", path)
        headers = dict(response.headers)

        assert headers["Cache-Control"] == "no-store"
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Content-Security-Policy"] == (
            "default-src 'self'; style-src 'unsafe-inline'"
        )


def test_d5_acceptance_mappings_are_immutable():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    with pytest.raises(TypeError):
        acceptance.checks["route_registry_exact"] = False
    with pytest.raises(TypeError):
        acceptance.get_statuses["/"] = 500
    with pytest.raises(TypeError):
        acceptance.health_payload["mode"] = "live"


def test_d5_acceptance_rejects_status_ok_mismatch():
    with pytest.raises(ValueError, match="status and ok must agree"):
        ResearchWorkspaceIntegrationAcceptance(
            status="PASSED",
            ok=False,
            route_paths=REQUIRED_RESEARCH_WORKSPACE_PATHS,
            checks={},
            get_statuses={},
            head_statuses={},
            write_statuses={},
            health_payload={},
        )


def test_d5_integration_acceptance_rejects_failed_route():
    real_application = _application()

    class FailedRouteApplication:
        def dispatch(self, method: str, path: str) -> ConsoleResponse:
            if method.upper() == "GET" and path == "/audit":
                return ConsoleResponse(
                    status=500,
                    content_type="text/plain; charset=utf-8",
                    body=b"failed",
                )
            return real_application.dispatch(method, path)

    acceptance = build_research_workspace_integration_acceptance(
        FailedRouteApplication()
    )

    assert acceptance.ok is False
    assert acceptance.status == "REJECTED"
    assert acceptance.checks["all_get_200"] is False
    assert acceptance.checks["security_cache_control"] is False


def test_d5_integration_acceptance_has_no_execution_authority():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.paper_only is True
    assert acceptance.loopback_only is True
    assert acceptance.registered_artifact_only is True
    assert acceptance.operator_review_required is True
    assert acceptance.ai_advisory_only is True
    assert acceptance.deterministic_engine_authority is True
