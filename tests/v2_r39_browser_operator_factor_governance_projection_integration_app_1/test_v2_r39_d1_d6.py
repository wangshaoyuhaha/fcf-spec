from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1.artifact_index import (
    SUPPORTED_ARTIFACT_TYPES,
    ConsoleArtifactIndex,
    LoadedConsoleArtifact,
    LoadedConsoleArtifactIndex,
    RegisteredConsoleArtifact,
)
from apps.browser_product_console_runtime_app_1.read_model import (
    ConsoleArtifactRecord,
    ConsoleReadModel,
    build_console_read_model,
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
    ARTIFACT_TYPE,
    SCHEMA_VERSION,
    V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY,
    V2R39BrowserOperatorFactorGovernanceProjectionBoundary,
    build_integration_acceptance,
    build_read_model,
    build_registered_browser_governance_projection_payload,
    parse_registered_browser_governance_projection,
)


def _projection() -> OperatorFactorGovernanceProjection:
    hashes = ("a" * 64, "b" * 64, "c" * 64)
    fields = (
        GovernanceProjectionField(
            "evidence-origin", "OBSERVED", "OBSERVED", "HIGH", (hashes[0],)
        ),
        GovernanceProjectionField(
            "projection-state", "REVIEW_REQUIRED", "INFERRED", "HIGH", hashes
        ),
    )
    return OperatorFactorGovernanceProjection(
        projection_id="browser-projection-v1",
        candidate_id="browser-candidate",
        factor_id="browser-factor",
        evidence_series_id="browser-series",
        market="a-share",
        evaluated_at_utc="2026-07-21T00:00:00Z",
        state="REVIEW_REQUIRED",
        confidence="HIGH",
        fields=fields,
        reason_codes=("operator-review-required", "no-factor-activation"),
    )


def _payload() -> dict[str, object]:
    return build_registered_browser_governance_projection_payload(_projection())


def _registration(artifact_id: str, artifact_type: str) -> RegisteredConsoleArtifact:
    return RegisteredConsoleArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        correlation_id="r39-correlation",
        relative_path=f"artifacts/{artifact_id}.json",
        content_sha256="d" * 64,
    )


def _record(artifact_id: str, artifact_type: str, payload: dict[str, object]):
    registration = _registration(artifact_id, artifact_type)
    return ConsoleArtifactRecord(
        artifact_id=registration.artifact_id,
        artifact_type=registration.artifact_type,
        relative_path=registration.relative_path,
        content_sha256=registration.content_sha256,
        payload=payload,
    )


def _console_model(records: tuple[ConsoleArtifactRecord, ...]) -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r39-correlation",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(item.artifact_id for item in records),
        artifact_records=records,
    )


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY
    assert not boundary.write_controls_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R39BrowserOperatorFactorGovernanceProjectionBoundary(write_controls_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_adapter_and_parser_round_trip_exact_projection():
    parsed = parse_registered_browser_governance_projection(_payload())
    assert parsed.projection == _projection()
    assert parsed.payload["schema_version"] == SCHEMA_VERSION


def test_d2_unknown_schema_is_rejected():
    payload = _payload()
    payload["schema_version"] = "unknown"
    with pytest.raises(ValueError, match="unsupported"):
        parse_registered_browser_governance_projection(payload)


def test_d2_projection_hash_mismatch_is_rejected():
    payload = _payload()
    payload["projection_hash"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        parse_registered_browser_governance_projection(payload)


def test_d3_unsafe_approval_flag_is_rejected():
    payload = _payload()
    payload["automatic_approval"] = True
    with pytest.raises(ValueError, match="cannot approve"):
        parse_registered_browser_governance_projection(payload)


def test_d3_unknown_field_origin_is_rejected():
    payload = _payload()
    payload["fields"][0]["origin"] = "UNKNOWN"  # type: ignore[index]
    with pytest.raises(ValueError, match="origin"):
        parse_registered_browser_governance_projection(payload)


def test_d3_artifact_type_is_registered_explicitly():
    assert ARTIFACT_TYPE in SUPPORTED_ARTIFACT_TYPES


def test_d4_console_read_model_validates_projection_before_use():
    registration = _registration("projection-artifact", ARTIFACT_TYPE)
    loaded = LoadedConsoleArtifactIndex(
        index=ConsoleArtifactIndex(
            "fcf.browser_console.artifact_index.v1",
            "r39-correlation",
            (registration,),
        ),
        index_path="registered-index.json",
        artifacts=(LoadedConsoleArtifact(registration, "projection.json", _payload()),),
    )
    model = build_console_read_model(loaded)
    assert model.artifact_records[0].artifact_type == ARTIFACT_TYPE


def test_d4_console_read_model_rejects_unsafe_projection():
    payload = _payload()
    payload["factor_activation"] = True
    registration = _registration("unsafe-projection", ARTIFACT_TYPE)
    loaded = LoadedConsoleArtifactIndex(
        ConsoleArtifactIndex(
            "fcf.browser_console.artifact_index.v1",
            "r39-correlation",
            (registration,),
        ),
        "registered-index.json",
        (LoadedConsoleArtifact(registration, "unsafe.json", payload),),
    )
    with pytest.raises(ValueError, match="activate"):
        build_console_read_model(loaded)


def test_d4_governance_workspace_includes_projection_artifact():
    record = _record("projection-artifact", ARTIFACT_TYPE, _payload())
    workspace = build_governance_workspace_model(_console_model((record,)))
    assert workspace.state == "INCOMPLETE"
    assert workspace.items[0].subject == "browser-candidate"


def test_d4_existing_required_governance_pair_remains_available():
    records = (
        _record("model", "model_governance", {"model_id": "model", "state": "READY"}),
        _record("policy", "policy_snapshot", {"policy_id": "policy", "state": "READY"}),
    )
    assert build_governance_workspace_model(_console_model(records)).state == "AVAILABLE"


def test_d5_http_governance_page_is_read_only_and_shows_projection():
    record = _record("projection-artifact", ARTIFACT_TYPE, _payload())
    response = BrowserProductConsoleApplication(_console_model((record,))).dispatch(
        "GET", "/governance"
    )
    body = response.body.decode("utf-8")
    assert response.status == 200 and "browser-candidate" in body
    assert "OBSERVED" in body and "INFERRED" in body
    assert "<form" not in body.lower() and "<button" not in body.lower()


def test_d6_presentation_and_acceptance_remain_non_actionable():
    artifact = parse_registered_browser_governance_projection(_payload())
    model = build_read_model(artifact)
    acceptance = build_integration_acceptance(artifact)
    assert isinstance(model.payload, MappingProxyType)
    assert acceptance.status == "PASSED_READ_ONLY_INTEGRATION"
    assert not acceptance.factor_activated and not acceptance.action_created
