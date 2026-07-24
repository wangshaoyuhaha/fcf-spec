from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.fcp_0105_registered_price_shape_indicator_runtime_app_1 import (
    INDICATOR_KINDS,
    RegisteredPriceShapeArtifact,
    build_reference_artifact_bytes,
    build_reference_price_shape_snapshot,
    build_reference_registry_snapshot,
    calculate_registered_price_shape_indicators,
    render_price_shape_snapshot_json,
)


AS_OF = "2026-07-24T07:30:00Z"


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes().decode("ascii"))


def _load(payload: dict[str, object]):
    content = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    artifact = RegisteredPriceShapeArtifact(
        artifact_id="registered-price-shape-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T07:10:00Z",
    )
    return calculate_registered_price_shape_indicators(
        content,
        artifact,
        build_reference_registry_snapshot(),
        as_of_utc=AS_OF,
    )


def test_reference_pack_calculates_exact_price_shape_values():
    snapshot = build_reference_price_shape_snapshot()

    assert len(INDICATOR_KINDS) == 8
    assert {
        key: dict(value) for key, value in snapshot.result_values.items()
    } == {
        "registered-bollinger-band-width-3": {"value": "0.27216553"},
        "registered-bollinger-breakout-3": {"value": "1"},
        "registered-bollinger-z-score-3": {"value": "3.67423461"},
        "registered-momentum-3": {"value": "3"},
        "registered-moving-average-slope-3": {"value": "1"},
        "registered-price-distance-from-moving-average-3": {"value": "0.25"},
        "registered-prior-high-breakout-3": {"value": "1"},
        "registered-range-breakout-3": {"value": "1"},
    }
    assert snapshot.catalog_version == "v3"
    assert len(snapshot.supported_kind_sources) == 25
    assert len(snapshot.missing_candidate_kinds) == 28
    assert not set(INDICATOR_KINDS).intersection(snapshot.missing_candidate_kinds)


def test_snapshot_is_immutable_deterministic_and_non_authorizing():
    first = build_reference_price_shape_snapshot()
    second = build_reference_price_shape_snapshot()

    assert isinstance(first.result_values, MappingProxyType)
    assert isinstance(first.supported_kind_sources, MappingProxyType)
    with pytest.raises(TypeError):
        first.result_values["registered-momentum-3"] = {"value": "0"}
    assert first.snapshot_hash == second.snapshot_hash
    assert render_price_shape_snapshot_json(first) == render_price_shape_snapshot_json(
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


def test_suspended_bar_is_excluded_from_every_calculation():
    payload = _payload()
    suspended = next(bar for bar in payload["bars"] if bar["is_suspended"])
    suspended["close"] = "9999"

    snapshot = _load(payload)
    reference = build_reference_price_shape_snapshot()
    assert snapshot.snapshot_hash != reference.snapshot_hash
    assert snapshot.result_values == reference.result_values


def test_zero_reference_dispersion_fails_closed_for_z_score():
    payload = _payload()
    eligible = [bar for bar in payload["bars"] if not bar["is_suspended"]]
    for bar in eligible[-4:-1]:
        bar["close"] = "12"
    z_request = next(
        request
        for request in payload["indicator_requests"]
        if request["indicator_kind"] == "BOLLINGER_Z_SCORE"
    )
    payload["indicator_requests"] = [z_request]
    with pytest.raises(ValueError, match="zero reference dispersion"):
        _load_single_request(payload)


def _load_single_request(payload: dict[str, object]):
    original = tuple(INDICATOR_KINDS)
    request = payload["indicator_requests"][0]
    payload["indicator_requests"] = [
        {
            **request,
            "indicator_kind": kind,
            "request_id": f"registered-{kind.lower().replace('_', '-')}-3",
            "factor_ref": next(
                item["factor_ref"]
                for item in _payload()["indicator_requests"]
                if item["indicator_kind"] == kind
            ),
        }
        for kind in original
    ]
    payload["indicator_requests"].sort(key=lambda item: item["request_id"])
    return _load(payload)


def test_artifact_hash_and_length_are_fail_closed():
    content = build_reference_artifact_bytes()
    artifact = RegisteredPriceShapeArtifact(
        artifact_id="registered-price-shape-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T07:10:00Z",
    )
    with pytest.raises(ValueError, match="byte length mismatch"):
        calculate_registered_price_shape_indicators(
            content,
            replace(artifact, byte_length=len(content) + 1),
            build_reference_registry_snapshot(),
            as_of_utc=AS_OF,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        calculate_registered_price_shape_indicators(
            content,
            replace(artifact, artifact_hash="0" * 64),
            build_reference_registry_snapshot(),
            as_of_utc=AS_OF,
        )


def test_future_bar_and_unregistered_factor_are_rejected():
    payload = _payload()
    payload["bars"][-1]["timestamp_utc"] = "2026-07-25T07:00:00Z"
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
    payload["registry_version"] = "v2"
    with pytest.raises(ValueError, match="registry identity mismatch"):
        _load(payload)

    payload = _payload()
    payload["catalog_version"] = "v4"
    with pytest.raises(ValueError, match="successor version"):
        _load(payload)


def test_reference_pack_uses_ascii_json_and_exact_registry_type():
    content = build_reference_artifact_bytes()
    artifact = RegisteredPriceShapeArtifact(
        artifact_id="registered-price-shape-test",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T07:10:00Z",
    )
    with pytest.raises(TypeError, match="exact runtime snapshot"):
        calculate_registered_price_shape_indicators(
            content,
            artifact,
            object(),
            as_of_utc=AS_OF,
        )
