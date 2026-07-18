from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1.artifact_index import (
    RegisteredConsoleArtifact,
)
from apps.browser_product_console_runtime_app_1.read_model import (
    ConsoleArtifactRecord,
    ConsoleReadModel,
)
from apps.browser_product_console_runtime_app_1.research_workspace_views import (
    build_governance_workspace_model,
)
from apps.browser_product_console_runtime_app_1.web_console import (
    BrowserProductConsoleApplication,
)
from apps.v2_r38_local_operator_factor_governance_projection_foundation_app_1 import (
    GovernanceProjectionField,
    OperatorFactorGovernanceProjection,
)
from apps.v2_r39_browser_operator_factor_governance_projection_integration_app_1 import (
    build_registered_browser_governance_projection_payload,
)
from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import (
    V2_R40_BROWSER_FACTOR_GOVERNANCE_FIELD_PRESENTATION_BOUNDARY,
    V2R40BrowserFactorGovernanceFieldPresentationBoundary,
    build_factor_governance_field_presentation,
    build_field_presentation_acceptance,
    build_read_model,
)


def _projection(value: str = "registered-value") -> OperatorFactorGovernanceProjection:
    return OperatorFactorGovernanceProjection(
        projection_id="field-presentation-v1",
        candidate_id="field-candidate",
        factor_id="field-factor",
        evidence_series_id="field-series",
        market="a-share",
        evaluated_at_utc="2026-07-22T00:00:00Z",
        state="REVIEW_REQUIRED",
        confidence="HIGH",
        fields=(
            GovernanceProjectionField(
                "z-inferred", value, "INFERRED", "MEDIUM", ("b" * 64,)
            ),
            GovernanceProjectionField(
                "a-observed", "source-value", "OBSERVED", "HIGH", ("a" * 64,)
            ),
        ),
        reason_codes=("operator-review-required",),
    )


def _payload(value: str = "registered-value") -> dict[str, object]:
    return build_registered_browser_governance_projection_payload(_projection(value))


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict[str, object],
) -> ConsoleArtifactRecord:
    registration = RegisteredConsoleArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        correlation_id="r40-correlation",
        relative_path=f"artifacts/{artifact_id}.json",
        content_sha256="d" * 64,
    )
    return ConsoleArtifactRecord(
        artifact_id=registration.artifact_id,
        artifact_type=registration.artifact_type,
        relative_path=registration.relative_path,
        content_sha256=registration.content_sha256,
        payload=payload,
    )


def _model(records: tuple[ConsoleArtifactRecord, ...]) -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r40-correlation",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(item.artifact_id for item in records),
        artifact_records=records,
    )


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R40_BROWSER_FACTOR_GOVERNANCE_FIELD_PRESENTATION_BOUNDARY
    assert boundary.read_only and boundary.operator_review_required
    assert not boundary.network_fetch_allowed and not boundary.write_controls_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_unsafe_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R40BrowserFactorGovernanceFieldPresentationBoundary(
            automatic_approval_allowed=True
        )


def test_d2_presentation_makes_origins_and_confidence_explicit():
    presentation = build_factor_governance_field_presentation(
        "projection-artifact", _payload()
    )
    assert tuple(field.origin for field in presentation.fields) == (
        "OBSERVED",
        "INFERRED",
    )
    assert tuple(field.confidence for field in presentation.fields) == (
        "HIGH",
        "MEDIUM",
    )


def test_d2_presentation_rows_are_deterministically_sorted_and_immutable():
    presentation = build_factor_governance_field_presentation("artifact", _payload())
    assert tuple(field.field_id for field in presentation.fields) == (
        "a-observed",
        "z-inferred",
    )
    with pytest.raises(FrozenInstanceError):
        presentation.state = "READY"  # type: ignore[misc]


def test_d2_invalid_projection_fails_closed():
    payload = _payload()
    payload["projection_hash"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        build_factor_governance_field_presentation("artifact", payload)


def test_d3_read_model_counts_observed_and_inferred_fields():
    presentation = build_factor_governance_field_presentation("artifact", _payload())
    read_model = build_read_model(presentation)
    assert read_model.payload["observed_field_count"] == 1
    assert read_model.payload["inferred_field_count"] == 1
    assert read_model.payload["factor_activation"] is False


def test_d3_acceptance_is_read_only_and_non_actionable():
    presentation = build_factor_governance_field_presentation("artifact", _payload())
    acceptance = build_field_presentation_acceptance(presentation)
    assert acceptance.status == "PASSED_READ_ONLY_FIELD_PRESENTATION"
    assert acceptance.origins_explicit and acceptance.field_count == 2
    assert not acceptance.factor_activated and not acceptance.action_created


def test_d4_workspace_contains_typed_projection_presentation():
    record = _record("projection", "factor_governance_projection", _payload())
    workspace = build_governance_workspace_model(_model((record,)))
    assert len(workspace.projection_presentations) == 1
    assert workspace.projection_presentations[0].candidate_id == "field-candidate"


def test_d4_workspace_revalidates_projection_and_fails_closed():
    payload = _payload()
    payload["automatic_approval"] = True
    record = _record("projection", "factor_governance_projection", payload)
    with pytest.raises(ValueError, match="cannot approve"):
        build_governance_workspace_model(_model((record,)))


def test_d4_required_governance_pair_availability_is_unchanged():
    records = (
        _record("model", "model_governance", {"model_id": "model"}),
        _record("policy", "policy_snapshot", {"policy_id": "policy"}),
    )
    workspace = build_governance_workspace_model(_model(records))
    assert workspace.state == "AVAILABLE"
    assert workspace.projection_presentations == ()


def test_d5_http_page_renders_semantic_field_table():
    record = _record("projection", "factor_governance_projection", _payload())
    response = BrowserProductConsoleApplication(_model((record,))).dispatch(
        "GET", "/governance"
    )
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "Factor Governance Field Detail" in body
    assert "OBSERVED" in body and "INFERRED" in body
    assert "Registered source snapshots" in body


def test_d5_http_page_escapes_registered_field_values():
    record = _record(
        "projection",
        "factor_governance_projection",
        _payload("<script>alert(1)</script>"),
    )
    body = BrowserProductConsoleApplication(_model((record,))).dispatch(
        "GET", "/governance"
    ).body.decode("utf-8")
    assert "<script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body


def test_d6_page_has_no_mutation_surface_and_post_is_rejected():
    record = _record("projection", "factor_governance_projection", _payload())
    app = BrowserProductConsoleApplication(_model((record,)))
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405
