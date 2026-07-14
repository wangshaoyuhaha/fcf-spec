from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleArtifactRecord,
    ConsoleReadModel,
    ConsoleResponse,
    EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS,
    REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS,
    build_evidence_audit_explorer_integration_acceptance,
    build_research_workspace_integration_acceptance,
)


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict,
) -> ConsoleArtifactRecord:
    return ConsoleArtifactRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        relative_path=f"registered/{artifact_id}.json",
        content_sha256="d" * 64,
        payload=payload,
    )


def _model() -> ConsoleReadModel:
    records = (
        _record(
            "manifest-1",
            "manifest",
            {"status": "READY"},
        ),
        _record(
            "validation-1",
            "paper_validation",
            {
                "validation_status": "PASS_WITH_REVIEW",
                "validated_at_utc": "2026-07-14T01:00:00Z",
                "validates_artifact_id": "manifest-1",
            },
        ),
        _record(
            "shadow-1",
            "shadow_observation",
            {
                "observation_status": "OBSERVED",
                "observed_at_utc": "2026-07-14T02:00:00Z",
                "derived_from_artifact_id": "validation-1",
            },
        ),
        _record(
            "review-1",
            "operator_review",
            {
                "review_status": "REVIEW_REQUIRED",
                "reviewed_at_utc": "2026-07-14T03:00:00Z",
                "review_for_artifact_id": "shadow-1",
            },
        ),
        _record(
            "archive-1",
            "report_archive",
            {
                "archive_status": "ARCHIVED",
                "archived_at_utc": "2026-07-14T04:00:00Z",
                "archive_for_artifact_id": "review-1",
            },
        ),
        _record(
            "ai-1",
            "ai_evaluation",
            {
                "model_name": "advisory-model",
                "prompt_version": "prompt-v1",
                "evaluation_status": "PASS_WITH_REVIEW",
                "risk_flags": ["MODEL_DRIFT"],
                "risk_level": "HIGH",
                "contradiction_codes": ["THESIS_CONFLICT"],
                "contradicts_artifact_id": "manifest-1",
            },
        ),
    )
    return ConsoleReadModel(
        correlation_id="corr-d5",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(
            record.artifact_id for record in records
        ),
        artifact_records=records,
    )


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(_model())


def test_d5_all_evidence_routes_are_available():
    application = _application()

    for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
        response = application.dispatch("GET", path)
        document = response.body.decode("utf-8")

        assert response.status == 200
        assert "registered-artifact-only" in document.lower()
        assert "read-only" in document.lower()


def test_d5_all_evidence_routes_support_head():
    application = _application()

    for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
        get_response = application.dispatch("GET", path)
        head_response = application.dispatch("HEAD", path)

        assert head_response.status == 200
        assert head_response.body == b""
        assert head_response.headers == get_response.headers


def test_d5_all_unsafe_methods_are_rejected():
    application = _application()

    for method in EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS:
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
            assert application.dispatch(
                method,
                path,
            ).status == 405


def test_d5_navigation_contains_all_explorer_routes_once():
    document = _application().dispatch(
        "GET",
        "/evidence",
    ).body.decode("utf-8")

    for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
        assert document.count(f'href="{path}"') == 1


def test_d5_artifact_filter_is_deterministic():
    application = _application()
    path = (
        "/evidence/artifacts"
        "?artifact_ids=validation-1"
        "&limit=10"
        "&sort_order=ASC"
    )

    first = application.dispatch("GET", path)
    second = application.dispatch("GET", path)
    document = first.body.decode("utf-8")

    assert first.status == 200
    assert first.body == second.body
    assert "validation-1" in document
    assert "archive-1" not in document
    assert "d" * 64 in document
    assert "registered/validation-1.json" in document


def test_d5_risk_and_ai_filters_use_explicit_registered_evidence():
    response = _application().dispatch(
        "GET",
        (
            "/evidence/risk"
            "?risk_flags=MODEL_DRIFT"
            "&contradiction_codes=THESIS_CONFLICT"
        ),
    )
    document = response.body.decode("utf-8")

    assert response.status == 200
    assert "ai-1" in document
    assert "MODEL_DRIFT" in document
    assert "THESIS_CONFLICT" in document
    assert "advisory-model" in document
    assert "prompt-v1" in document


@pytest.mark.parametrize(
    "path",
    (
        "/evidence?execute=true",
        "/evidence?limit=0",
        "/evidence?limit=501",
        "/evidence?limit=1&limit=2",
        "/evidence?artifact_ids=",
        "/evidence?artifact_ids=%ZZ",
        "/evidence?sort_order=RANDOM",
        "/evidence?artifact_ids=../unsafe",
    ),
)
def test_d5_invalid_query_fails_closed(path):
    response = _application().dispatch("GET", path)
    document = response.body.decode("utf-8")

    assert response.status == 400
    assert "REJECTED_QUERY" in document
    assert "<script" not in document.lower()


def test_d5_correlation_mismatch_returns_filtered_empty():
    response = _application().dispatch(
        "GET",
        "/evidence/artifacts?correlation_id=corr-other",
    )
    document = response.body.decode("utf-8")

    assert response.status == 200
    assert "FILTERED_EMPTY" in document
    assert "No registered artifact matches the query" in document


def test_d5_validation_review_and_archive_linkage_is_visible():
    application = _application()

    validation = application.dispatch(
        "GET",
        "/evidence/validation",
    ).body.decode("utf-8")
    review = application.dispatch(
        "GET",
        "/evidence/review",
    ).body.decode("utf-8")
    archive = application.dispatch(
        "GET",
        "/evidence/archive",
    ).body.decode("utf-8")

    assert "validation-1" in validation
    assert "shadow-1" in validation
    assert "review-1" in review
    assert "archive-1" in archive


def test_d5_lineage_exposes_typed_registered_relationships():
    document = _application().dispatch(
        "GET",
        "/evidence/lineage?artifact_ids=archive-1",
    ).body.decode("utf-8")

    assert "archive-1" in document
    assert "review-1" in document
    assert "ARCHIVES" in document


def test_d5_unknown_and_traversal_routes_fail_closed():
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


def test_d5_security_headers_and_no_mutating_controls():
    application = _application()

    for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS:
        response = application.dispatch("GET", path)
        headers = dict(response.headers)
        document = response.body.decode("utf-8").lower()

        assert headers["Cache-Control"] == "no-store"
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Content-Security-Policy"] == (
            "default-src 'self'; style-src 'unsafe-inline'"
        )
        assert "<form" not in document
        assert "<button" not in document
        assert "method=" not in document
        assert "<script" not in document


def test_d5_integration_acceptance_passes():
    acceptance = (
        build_evidence_audit_explorer_integration_acceptance(
            _application()
        )
    )

    assert acceptance.status == "PASSED"
    assert acceptance.ok is True
    assert all(acceptance.checks.values())


def test_d5_acceptance_mappings_are_immutable():
    acceptance = (
        build_evidence_audit_explorer_integration_acceptance(
            _application()
        )
    )

    with pytest.raises(TypeError):
        acceptance.checks["mutate"] = True


def test_d5_research_workspace_acceptance_still_passes():
    acceptance = build_research_workspace_integration_acceptance(
        _application()
    )

    assert acceptance.status == "PASSED"
    assert acceptance.ok is True


def test_d5_failed_route_produces_rejected_acceptance():
    class FailedRouteApplication(BrowserProductConsoleApplication):
        def dispatch(
            self,
            method: str,
            raw_path: str,
        ) -> ConsoleResponse:
            if (
                method.upper() == "GET"
                and raw_path == "/evidence/archive"
            ):
                return ConsoleResponse(
                    status=500,
                    content_type="text/plain; charset=utf-8",
                    body=b"failed",
                )
            return super().dispatch(method, raw_path)

    acceptance = (
        build_evidence_audit_explorer_integration_acceptance(
            FailedRouteApplication(_model())
        )
    )

    assert acceptance.status == "REJECTED"
    assert acceptance.ok is False
    assert acceptance.checks["all_get_200"] is False
