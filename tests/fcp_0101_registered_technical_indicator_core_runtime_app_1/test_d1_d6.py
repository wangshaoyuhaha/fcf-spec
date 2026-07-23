from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1 import (
    INDICATOR_KINDS,
    REFERENCE_AS_OF_UTC,
    RegisteredMarketArtifact,
    build_reference_artifact_bytes,
    calculate_registered_indicators,
)


def _artifact(content: bytes) -> RegisteredMarketArtifact:
    return RegisteredMarketArtifact(
        artifact_id="registered-technical-indicator-reference-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T02:10:00Z",
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes())


def _content(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_d1_exact_registered_artifact_is_required() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        calculate_registered_indicators(
            content,
            replace(artifact, byte_length=1),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        calculate_registered_indicators(
            content,
            replace(artifact, artifact_hash="2" * 64),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )


def test_d2_closed_ascii_schema_and_decimal_strings_are_enforced() -> None:
    payload = _payload()
    payload["unexpected"] = True
    changed = _content(payload)
    with pytest.raises(ValueError, match="closed registered schema"):
        calculate_registered_indicators(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    payload = _payload()
    bars = payload["bars"]
    assert isinstance(bars, list)
    bars[0]["close"] = 11.0
    changed = _content(payload)
    with pytest.raises(ValueError, match="decimal string"):
        calculate_registered_indicators(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d3_all_registered_core_indicators_are_deterministic() -> None:
    content = build_reference_artifact_bytes()
    snapshot = calculate_registered_indicators(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert tuple(
        value.split(".")[-1].upper()
        for value in (
            "factor.technical.atr",
            "factor.technical.bollinger",
            "factor.technical.ema",
            "factor.technical.rsi",
            "factor.technical.sma",
            "factor.technical.vwap",
        )
    ) == tuple(sorted(INDICATOR_KINDS))
    assert snapshot.result_values["request.sma"]["value"] == "15"
    assert snapshot.result_values["request.ema"]["value"] == "15"
    assert snapshot.result_values["request.rsi"]["value"] == "100"
    assert snapshot.result_values["request.atr"]["value"] == "3"
    assert snapshot.result_values["request.vwap"]["value"] == "15.04761905"
    assert snapshot.result_values["request.bollinger"] == {
        "lower": "13.36700684",
        "middle": "15",
        "stddev": "0.81649658",
        "upper": "16.63299316",
    }


def test_d4_future_bars_and_invalid_ohlc_fail_closed() -> None:
    payload = _payload()
    bars = payload["bars"]
    assert isinstance(bars, list)
    bars[-1]["timestamp_utc"] = "2026-07-25T00:00:00Z"
    changed = _content(payload)
    with pytest.raises(ValueError, match="future bars"):
        calculate_registered_indicators(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    payload = _payload()
    bars = payload["bars"]
    assert isinstance(bars, list)
    bars[0]["high"] = "8"
    changed = _content(payload)
    with pytest.raises(ValueError, match="OHLC ordering"):
        calculate_registered_indicators(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d5_suspension_is_explicit_and_excluded() -> None:
    content = build_reference_artifact_bytes()
    snapshot = calculate_registered_indicators(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert snapshot.result_values["request.sma"]["value"] == "15"
    payload = _payload()
    bars = payload["bars"]
    assert isinstance(bars, list)
    bars[3]["is_suspended"] = False
    changed = _content(payload)
    with pytest.raises(ValueError, match="suspension"):
        calculate_registered_indicators(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d6_snapshot_is_immutable_reproducible_and_non_authorizing() -> None:
    content = build_reference_artifact_bytes()
    first = calculate_registered_indicators(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    second = calculate_registered_indicators(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert isinstance(first.result_values, MappingProxyType)
    with pytest.raises(TypeError):
        first.result_values["x"] = {}  # type: ignore[index]
    assert first.deterministic_engine_authority
    assert first.operator_review_required and first.read_only
    assert not any(
        (
            first.scoring_authority,
            first.recommendation_authority,
            first.account_authority,
            first.execution_authority,
        )
    )
