from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.fcp_0104_registered_volume_flow_indicator_runtime_app_1 import (
    INDICATOR_KINDS,
    RegisteredVolumeFlowArtifact,
    build_reference_artifact_bytes,
    build_reference_registry_snapshot,
    build_reference_volume_flow_snapshot,
    calculate_registered_volume_flow_indicators,
    render_volume_flow_snapshot_json,
)


AS_OF = "2026-07-24T06:30:00Z"


def _load(payload: dict[str, object]):
    content = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    artifact = RegisteredVolumeFlowArtifact(
        artifact_id="registered-volume-flow-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T06:10:00Z",
    )
    return calculate_registered_volume_flow_indicators(
        content,
        artifact,
        build_reference_registry_snapshot(),
        as_of_utc=AS_OF,
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes().decode("ascii"))


def test_reference_pack_calculates_exact_volume_flow_values():
    snapshot = build_reference_volume_flow_snapshot()

    assert INDICATOR_KINDS == ("MFI", "OBV", "VOLUME_PRICE_TREND")
    assert {
        key: dict(value) for key, value in snapshot.result_values.items()
    } == {
        "registered-mfi-3": {"value": "79.83193277"},
        "registered-obv-3": {"value": "190"},
        "registered-volume-price-trend-3": {"value": "38.66666667"},
    }
    assert snapshot.catalog_version == "v2"
    assert len(snapshot.supported_kind_sources) == 17
    assert len(snapshot.missing_candidate_kinds) == 36
    assert not set(INDICATOR_KINDS).intersection(snapshot.missing_candidate_kinds)


def test_snapshot_is_immutable_deterministic_and_non_authorizing():
    first = build_reference_volume_flow_snapshot()
    second = build_reference_volume_flow_snapshot()

    assert isinstance(first.result_values, MappingProxyType)
    assert isinstance(first.supported_kind_sources, MappingProxyType)
    with pytest.raises(TypeError):
        first.result_values["registered-obv-3"] = {"value": "0"}
    assert first.snapshot_hash == second.snapshot_hash
    assert render_volume_flow_snapshot_json(first) == render_volume_flow_snapshot_json(
        second
    )
    assert first.operator_review_required and first.read_only
    assert first.deterministic_engine_authority
    assert not any(
        (
            first.scoring_authority,
            first.ranking_authority,
            first.recommendation_authority,
            first.account_authority,
            first.execution_authority,
        )
    )


def test_suspended_bar_is_excluded_from_all_calculations():
    payload = _payload()
    suspended = next(bar for bar in payload["bars"] if bar["is_suspended"])
    suspended["high"] = "999"
    suspended["low"] = "999"
    suspended["close"] = "999"

    snapshot = _load(payload)
    assert snapshot.snapshot_hash != build_reference_volume_flow_snapshot().snapshot_hash
    assert snapshot.result_values == build_reference_volume_flow_snapshot().result_values


def test_artifact_hash_and_length_are_fail_closed():
    content = build_reference_artifact_bytes()
    artifact = RegisteredVolumeFlowArtifact(
        artifact_id="registered-volume-flow-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T06:10:00Z",
    )
    with pytest.raises(ValueError, match="byte length mismatch"):
        calculate_registered_volume_flow_indicators(
            content,
            replace(artifact, byte_length=len(content) + 1),
            build_reference_registry_snapshot(),
            as_of_utc=AS_OF,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        calculate_registered_volume_flow_indicators(
            content,
            replace(artifact, artifact_hash="0" * 64),
            build_reference_registry_snapshot(),
            as_of_utc=AS_OF,
        )


def test_future_bar_and_unregistered_factor_are_rejected():
    payload = _payload()
    payload["bars"][-1]["timestamp_utc"] = "2026-07-25T06:00:00Z"
    with pytest.raises(ValueError, match="future bars"):
        _load(payload)

    payload = _payload()
    payload["indicator_requests"][0]["factor_ref"] = "missing-factor@v1"
    with pytest.raises(ValueError, match="factor is not registered"):
        _load(payload)


def test_requests_require_unique_sorted_full_pack():
    payload = _payload()
    payload["indicator_requests"].reverse()
    with pytest.raises(ValueError, match="unique and sorted"):
        _load(payload)

    payload = _payload()
    payload["indicator_requests"].pop()
    with pytest.raises(ValueError, match="every registered kind"):
        _load(payload)


def test_closed_schema_registry_identity_and_catalog_version_are_exact():
    payload = _payload()
    payload["unexpected"] = "not-registered"
    with pytest.raises(ValueError, match="closed registered schema"):
        _load(payload)

    payload = _payload()
    payload["registry_version"] = "v1"
    with pytest.raises(ValueError, match="registry identity mismatch"):
        _load(payload)

    payload = _payload()
    payload["catalog_version"] = "v3"
    with pytest.raises(ValueError, match="successor version"):
        _load(payload)


def test_reference_pack_uses_ascii_json_and_exact_registry_type():
    content = build_reference_artifact_bytes()
    artifact = RegisteredVolumeFlowArtifact(
        artifact_id="registered-volume-flow-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T06:10:00Z",
    )
    with pytest.raises(TypeError, match="exact runtime snapshot"):
        calculate_registered_volume_flow_indicators(
            content,
            artifact,
            object(),
            as_of_utc=AS_OF,
        )
