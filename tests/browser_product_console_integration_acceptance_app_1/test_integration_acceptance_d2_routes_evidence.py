import hashlib
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
    RESEARCH_WORKSPACE_ROUTE_REGISTRY,
    build_browser_console_runtime,
)


_CORRELATION_ID = "corr-d2-integration"
_ARTIFACTS = (
    (
        "data-1",
        "data_snapshot",
        {"snapshot_id": "snapshot-1", "status": "REGISTERED"},
    ),
    (
        "quality-1",
        "data_quality",
        {
            "quality_status": "PASS_STRICT",
            "source_artifact_id": "data-1",
        },
    ),
    (
        "run-1",
        "research_run",
        {
            "run_id": "run-1",
            "run_status": "COMPLETE",
            "input_artifact_id": "quality-1",
        },
    ),
    (
        "watchlist-1",
        "ranked_watchlist",
        {
            "derived_from_artifact_id": "run-1",
            "candidates": [
                {
                    "symbol": "600000",
                    "name": "Sample Stock",
                    "rank": 1,
                    "total_score": 88.5,
                    "score_breakdown": {
                        "momentum": 90.0,
                        "quality": 87.0,
                    },
                    "reason_codes": ["VOLUME_EXPANSION"],
                    "risk_flags": ["HIGH_VOLATILITY"],
                    "risk_level": "HIGH",
                    "data_quality_state": "PASS_STRICT",
                    "confidence_level": "MEDIUM",
                    "operator_review_required": True,
                }
            ],
        },
    ),
    (
        "ai-1",
        "ai_explanation",
        {
            "subject": "registered-source-evidence",
            "model_name": "advisory-model",
            "prompt_version": "prompt-v1",
            "evaluation_status": "REVIEW_REQUIRED",
            "risk_flags": ["MODEL_DRIFT"],
            "risk_level": "HIGH",
            "contradiction_codes": ["THESIS_CONFLICT"],
            "contradicts_artifact_id": "watchlist-1",
        },
    ),
    (
        "validation-1",
        "paper_validation",
        {
            "validation_status": "PASS_WITH_REVIEW",
            "validated_at_utc": "2026-07-15T01:00:00Z",
            "validates_artifact_id": "watchlist-1",
        },
    ),
    (
        "shadow-1",
        "shadow_observation",
        {
            "observation_status": "OBSERVED",
            "observed_at_utc": "2026-07-15T02:00:00Z",
            "derived_from_artifact_id": "validation-1",
        },
    ),
    (
        "review-1",
        "operator_review",
        {
            "subject": "registered-review-evidence",
            "review_status": "REVIEW_REQUIRED",
            "reviewed_at_utc": "2026-07-15T03:00:00Z",
            "review_for_artifact_id": "shadow-1",
        },
    ),
    (
        "archive-1",
        "report_archive",
        {
            "archive_status": "PENDING_MANUAL_ARCHIVE",
            "archived_at_utc": "2026-07-15T04:00:00Z",
            "archive_for_artifact_id": "review-1",
        },
    ),
    (
        "audit-1",
        "audit_receipt",
        {
            "audit_status": "RECORDED",
            "source_artifact_id": "archive-1",
        },
    ),
    (
        "manifest-1",
        "manifest",
        {
            "manifest_status": "REGISTERED",
            "source_artifact_id": "audit-1",
            "correlates_with_artifact_id": (
                "missing-registered-evidence"
            ),
        },
    ),
)


def _json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
    ).encode("utf-8")


def _write_registered_fixture(root: Path) -> tuple[Path, dict[str, str]]:
    (root / "registered").mkdir()
    entries = []
    digests = {}

    for artifact_id, artifact_type, payload in _ARTIFACTS:
        relative_path = f"registered/{artifact_id}.json"
        content = _json_bytes(payload)
        digest = hashlib.sha256(content).hexdigest()
        (root / relative_path).write_bytes(content)
        digests[artifact_id] = digest
        entries.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "correlation_id": _CORRELATION_ID,
                "relative_path": relative_path,
                "content_sha256": digest,
            }
        )

    index_path = root / "index.json"
    index_path.write_bytes(
        _json_bytes(
            {
                "schema_version": (
                    "fcf.browser_console.artifact_index.v1"
                ),
                "correlation_id": _CORRELATION_ID,
                "entries": entries,
            }
        )
    )
    return index_path, digests


@pytest.fixture
def d2_application(tmp_path: Path):
    index_path, digests = _write_registered_fixture(tmp_path)
    runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
    )
    return runtime.application, digests


def _required_paths() -> tuple[str, ...]:
    return tuple(
        route.path
        for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
    ) + tuple(
        route.path
        for route in EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.routes
    )


def test_d2_mapping_payload_renders_without_mutating_registered_evidence():
    payload = MappingProxyType({"status": "REVIEW_REQUIRED"})
    model = ConsoleReadModel(
        correlation_id="corr-d2-mapping",
        candidates=(),
        sections=MappingProxyType(
            {"ai_explanation": (payload,)}
        ),
        source_artifact_ids=(),
    )

    response = BrowserProductConsoleApplication(model).dispatch(
        "GET",
        "/risk",
    )

    assert response.status == 200
    assert b"REVIEW_REQUIRED" in response.body
    assert dict(payload) == {"status": "REVIEW_REQUIRED"}


def test_d2_all_product_routes_support_get_and_head(d2_application):
    application, _ = d2_application

    for path in _required_paths():
        get_response = application.dispatch("GET", path)
        head_response = application.dispatch("HEAD", path)

        assert get_response.status == 200, path
        assert get_response.body, path
        assert head_response.status == 200, path
        assert head_response.body == b"", path
        assert head_response.headers == get_response.headers, path


def test_d2_routes_remain_secure_read_only_and_fully_navigable(
    d2_application,
):
    application, _ = d2_application
    overview = application.dispatch("GET", "/").body.decode("utf-8")

    for path in _required_paths():
        response = application.dispatch("GET", path)
        headers = dict(response.headers)
        document = response.body.decode("utf-8").lower()

        assert overview.count(f'href="{path}"') == 1, path
        assert headers["Cache-Control"] == "no-store", path
        assert headers["X-Content-Type-Options"] == "nosniff", path
        assert headers["Content-Security-Policy"] == (
            "default-src 'self'; style-src 'unsafe-inline'"
        ), path
        assert "<form" not in document, path
        assert "<button" not in document, path
        assert "<script" not in document, path
        assert "method=" not in document, path


def test_d2_workspace_surfaces_render_registered_payloads(d2_application):
    application, _ = d2_application
    expected = {
        "/data": ("snapshot-1", "PASS_STRICT"),
        "/stocks": (
            "600000",
            "VOLUME_EXPANSION",
            "HIGH_VOLATILITY",
        ),
        "/runs": ("run-1", "COMPLETE"),
        "/ai-comparison": (
            "advisory-model",
            "prompt-v1",
            "REVIEW_REQUIRED",
        ),
        "/validation": (
            "PASS_WITH_REVIEW",
            "OBSERVED",
            "validation-1",
        ),
        "/review": (
            "registered-review-evidence",
            "REVIEW_REQUIRED",
            "shadow-1",
        ),
        "/reports": ("PENDING_MANUAL_ARCHIVE", "review-1"),
        "/audit": ("audit-1", "manifest-1"),
    }

    for path, markers in expected.items():
        document = application.dispatch("GET", path).body.decode("utf-8")
        for marker in markers:
            assert marker in document, (path, marker)


def test_d2_registered_identity_path_and_digest_are_visible(d2_application):
    application, digests = d2_application
    document = application.dispatch(
        "GET",
        "/evidence/artifacts",
    ).body.decode("utf-8")

    for artifact_id in (
        "watchlist-1",
        "ai-1",
        "review-1",
        "audit-1",
        "manifest-1",
    ):
        assert artifact_id in document
        assert f"registered/{artifact_id}.json" in document
        assert digests[artifact_id] in document


def test_d2_lineage_shows_typed_and_unresolved_registered_references(
    d2_application,
):
    application, _ = d2_application
    document = application.dispatch(
        "GET",
        "/evidence/lineage",
    ).body.decode("utf-8")

    for relation in (
        "DERIVED_FROM",
        "VALIDATES",
        "REVIEWS",
        "ARCHIVES",
        "CONTRADICTS",
    ):
        assert relation in document
    assert "Unresolved registered references" in document
    assert "missing-registered-evidence" in document


def test_d2_risk_contradiction_and_advisory_ai_evidence_are_visible(
    d2_application,
):
    application, _ = d2_application
    response = application.dispatch("GET", "/evidence/risk")
    document = response.body.decode("utf-8")

    assert response.status == 200
    assert "HIGH_VOLATILITY" in document
    assert "MODEL_DRIFT" in document
    assert "THESIS_CONFLICT" in document
    assert "advisory-model" in document
    assert "prompt-v1" in document
    assert "Registered-artifact-only and read-only" in document


def test_d2_validation_review_and_archive_lifecycle_is_visible(
    d2_application,
):
    application, _ = d2_application
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
    assert "REVIEW_REQUIRED" in review
    assert "archive-1" in archive
    assert "PENDING_MANUAL_ARCHIVE" in archive


def test_d2_registered_evidence_rendering_is_deterministic(d2_application):
    application, _ = d2_application
    first = application.dispatch("GET", "/evidence")
    second = application.dispatch("GET", "/evidence")

    assert first.status == second.status == 200
    assert first.headers == second.headers
    assert first.body == second.body


def test_d2_write_methods_remain_unavailable(d2_application):
    application, _ = d2_application

    for path in _required_paths():
        assert application.dispatch("POST", path).status == 405, path
