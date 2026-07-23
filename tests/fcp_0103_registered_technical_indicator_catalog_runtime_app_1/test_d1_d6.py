from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.fcp_0103_registered_technical_indicator_catalog_runtime_app_1 import (
    ACCEPTED_CANDIDATE_KINDS,
    FOUNDATION_KIND_SOURCES,
    PHASE_ID,
    RegisteredIndicatorCatalogArtifact,
    build_reference_artifact_bytes,
    build_reference_catalog_snapshot,
    build_reference_registry_snapshot,
    load_registered_indicator_catalog,
    render_catalog_snapshot_json,
)


OBSERVED_AT_UTC = "2026-07-24T05:30:00Z"


def _load_payload(payload: dict[str, object]):
    content = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    artifact = RegisteredIndicatorCatalogArtifact(
        artifact_id="registered-technical-indicator-catalog-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T05:10:00Z",
    )
    return load_registered_indicator_catalog(
        content,
        artifact,
        build_reference_registry_snapshot(),
        observed_at_utc=OBSERVED_AT_UTC,
    )


def _reference_payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes().decode("ascii"))


def test_reference_catalog_reports_exact_registered_coverage_and_missing_candidates():
    snapshot = build_reference_catalog_snapshot()

    assert PHASE_ID == (
        "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1"
    )
    assert snapshot.state == "CATALOG_PARTIAL"
    assert dict(snapshot.supported_kind_sources) == dict(
        sorted(FOUNDATION_KIND_SOURCES.items())
    )
    assert len(snapshot.supported_kind_sources) == 14
    assert snapshot.missing_candidate_kinds == tuple(
        sorted(set(ACCEPTED_CANDIDATE_KINDS) - set(FOUNDATION_KIND_SOURCES))
    )
    assert {"MFI", "OBV", "REALIZED_VOLATILITY"}.issubset(
        snapshot.missing_candidate_kinds
    )
    assert snapshot.reason_codes == (
        "REGISTERED_FOUNDATION_COVERAGE_PARTIAL",
        "MISSING_CANDIDATES_VISIBLE",
    )


def test_snapshot_is_immutable_and_has_no_decision_or_execution_authority():
    snapshot = build_reference_catalog_snapshot()

    assert isinstance(snapshot.supported_kind_sources, MappingProxyType)
    assert isinstance(snapshot.factor_refs, MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.factor_refs["SMA"] = "other@v1"
    assert snapshot.operator_review_required is True
    assert snapshot.read_only is True
    assert snapshot.calculation_activation_allowed is False
    assert snapshot.scoring_allowed is False
    assert snapshot.ranking_allowed is False
    assert snapshot.recommendation_allowed is False
    assert snapshot.account_authority is False
    assert snapshot.execution_authority is False


def test_reference_render_and_snapshot_hash_are_deterministic():
    first = build_reference_catalog_snapshot()
    second = build_reference_catalog_snapshot()

    assert first.snapshot_hash == second.snapshot_hash
    assert render_catalog_snapshot_json(first) == render_catalog_snapshot_json(second)
    rendered = json.loads(render_catalog_snapshot_json(first))
    assert rendered["state"] == "CATALOG_PARTIAL"
    assert rendered["missing_candidate_kinds"] == list(
        first.missing_candidate_kinds
    )


def test_artifact_hash_and_length_are_fail_closed():
    content = build_reference_artifact_bytes()
    artifact = RegisteredIndicatorCatalogArtifact(
        artifact_id="registered-technical-indicator-catalog-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T05:10:00Z",
    )

    with pytest.raises(ValueError, match="byte length mismatch"):
        load_registered_indicator_catalog(
            content,
            replace(artifact, byte_length=len(content) + 1),
            build_reference_registry_snapshot(),
            observed_at_utc=OBSERVED_AT_UTC,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_indicator_catalog(
            content,
            replace(artifact, artifact_hash="0" * 64),
            build_reference_registry_snapshot(),
            observed_at_utc=OBSERVED_AT_UTC,
        )


def test_catalog_rejects_unregistered_factor_and_foundation_mapping():
    payload = _reference_payload()
    payload["entries"][0]["factor_ref"] = "missing-factor@v1"
    with pytest.raises(ValueError, match="factor is not registered"):
        _load_payload(payload)

    payload = _reference_payload()
    payload["entries"][0]["foundation_ref"] = "V2-R20"
    with pytest.raises(ValueError, match="foundation mapping is not registered"):
        _load_payload(payload)


def test_catalog_rejects_duplicate_kind_and_open_schema():
    payload = _reference_payload()
    payload["entries"].append(dict(payload["entries"][0]))
    with pytest.raises(ValueError, match="indicator kinds must be unique"):
        _load_payload(payload)

    payload = _reference_payload()
    payload["unexpected"] = "not-registered"
    with pytest.raises(ValueError, match="closed registered schema"):
        _load_payload(payload)


def test_catalog_rejects_non_ascii_and_non_exact_registry_snapshot():
    content = b'{"catalog_id":"caf\\xc3\\xa9"}'
    artifact = RegisteredIndicatorCatalogArtifact(
        artifact_id="registered-technical-indicator-catalog-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T05:10:00Z",
    )
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_indicator_catalog(
            content,
            artifact,
            build_reference_registry_snapshot(),
            observed_at_utc=OBSERVED_AT_UTC,
        )
    with pytest.raises(TypeError, match="exact runtime snapshot"):
        load_registered_indicator_catalog(
            build_reference_artifact_bytes(),
            RegisteredIndicatorCatalogArtifact(
                artifact_id="registered-technical-indicator-catalog-test",
                artifact_hash=hashlib.sha256(
                    build_reference_artifact_bytes()
                ).hexdigest(),
                byte_length=len(build_reference_artifact_bytes()),
                rights_id="local-research-rights-v1",
                registered_at_utc="2026-07-24T05:10:00Z",
            ),
            object(),
            observed_at_utc=OBSERVED_AT_UTC,
        )


def test_catalog_registry_identity_is_exact():
    payload = _reference_payload()
    payload["registry_version"] = "v2"

    with pytest.raises(ValueError, match="registry identity mismatch"):
        _load_payload(payload)
