from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path

import pytest

from apps.fcp_0093_btc_coin_metrics_reference_rate_local_csv_validation_app_1 import (
    CoinMetricsBTCReferenceCSVRegistration,
    CoinMetricsBTCReferenceCSVValidationRequest,
    render_validation_json,
    validate_registered_coin_metrics_btc_reference_csv,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


AS_OF = "2026-07-23T04:10:00Z"


def _bytes() -> bytes:
    return (
        b"asset,time,ReferenceRateUSD\n"
        b"btc,2026-07-22T22:00:00.000000000Z,65995.0524599649\n"
        b"btc,2026-07-22T23:00:00.000000000Z,65969.0594517826\n"
        b"btc,2026-07-23T00:00:00.000000000Z,65983.1860485096\n"
    )


def _registration(raw: bytes, **changes: object) -> CoinMetricsBTCReferenceCSVRegistration:
    values: dict[str, object] = {
        "artifact_id": "coin-metrics-btc-reference-source-v1",
        "source_id": "coin-metrics-community-api",
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-23T04:05:00Z",
        "rights": LocalEventRights(
            license_id="operator-registered-community-data",
            permitted_use="local-paper-research",
            retention_days=30,
        ),
    }
    values.update(changes)
    return CoinMetricsBTCReferenceCSVRegistration(**values)


def _request(raw: bytes, **changes: object) -> CoinMetricsBTCReferenceCSVValidationRequest:
    values: dict[str, object] = {
        "registration": _registration(raw),
        "output_artifact_id": "coin-metrics-btc-reference-validation-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return CoinMetricsBTCReferenceCSVValidationRequest(**values)


def _run(tmp_path: Path, raw: bytes | None = None):
    payload = raw if raw is not None else _bytes()
    path = tmp_path / "reference.csv"
    path.write_bytes(payload)
    return validate_registered_coin_metrics_btc_reference_csv(path, _request(payload))


def test_d1_registration_and_request_are_closed_and_immutable() -> None:
    raw = _bytes()
    request = _request(raw)
    assert request.registration.media_type == "text/csv"
    assert request.expected_asset == "btc"
    with pytest.raises(FrozenInstanceError):
        request.expected_asset = "eth"  # type: ignore[misc]
    with pytest.raises(ValueError, match="closed to btc"):
        _request(raw, expected_asset="eth")
    with pytest.raises(ValueError, match="cannot precede"):
        _request(raw, as_of_utc="2026-07-23T04:04:59Z")
    with pytest.raises(ValueError, match="retrieval or provider authority"):
        _registration(raw, network_retrieval_allowed=True)


def test_d2_path_gate_is_regular_bounded_and_exact(tmp_path: Path) -> None:
    raw = _bytes()
    target = tmp_path / "target.csv"
    target.write_bytes(raw)
    link = tmp_path / "link.csv"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="must not be a symlink"):
        validate_registered_coin_metrics_btc_reference_csv(link, _request(raw))
    with pytest.raises(FileNotFoundError, match="not a regular file"):
        validate_registered_coin_metrics_btc_reference_csv(
            tmp_path / "missing.csv", _request(raw)
        )
    with pytest.raises(ValueError, match="byte length mismatch"):
        validate_registered_coin_metrics_btc_reference_csv(
            target,
            _request(raw, registration=_registration(raw, byte_length=len(raw) - 1)),
        )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_registered_coin_metrics_btc_reference_csv(
            target,
            _request(raw, registration=_registration(raw, content_sha256="0" * 64)),
        )


def test_d3_exact_schema_decimal_and_clock_validation(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result.observation_count == 3
    assert result.observation_start_utc == "2026-07-22T22:00:00Z"
    assert result.observation_end_utc == "2026-07-23T00:00:00Z"
    assert result.cadence_seconds == 3_600
    assert result.observation_kind == "NEUTRAL_REFERENCE_RATE_USD"
    invalid_cases = (
        (_bytes().replace(b"ReferenceRateUSD", b"price"), "header mismatch"),
        (_bytes().replace(b"btc,2026", b"eth,2026", 1), "unexpected asset"),
        (_bytes().replace(b"65995.0524599649", b"6.5e4"), "invalid decimal lexeme"),
        (
            _bytes().replace(
                b"2026-07-22T23:00:00.000000000Z",
                b"2026-07-22T22:30:00.000000000Z",
            ),
            "cadence mismatch",
        ),
    )
    for raw, message in invalid_cases:
        with pytest.raises(ValueError, match=message):
            _run(tmp_path, raw)


def test_d4_output_is_ascii_path_free_and_value_free(tmp_path: Path) -> None:
    rendered = render_validation_json(_run(tmp_path))
    payload = json.loads(rendered)
    rendered.encode("ascii")
    assert payload["authority"]["operator_review_required"] is True
    assert payload["authority"]["source_values_retained"] is False
    assert payload["authority"]["mark_or_index_authority"] is False
    assert "reference.csv" not in rendered
    for prohibited in ("65995", "65969", "65983", "ReferenceRateUSD"):
        assert prohibited not in rendered


def test_d5_malformed_and_temporally_invalid_rows_fail_closed(tmp_path: Path) -> None:
    cases = (
        (b"\xef\xbb\xbf" + _bytes(), "must not contain a BOM"),
        (_bytes().rstrip(b"\n"), "must end with a newline"),
        (_bytes().replace(b"\n", b"\n\n", 1), "blank CSV row"),
        (
            _bytes().replace(
                b"2026-07-22T23:00:00.000000000Z",
                b"2026-07-22T22:00:00.000000000Z",
            ),
            "duplicate clocks",
        ),
        (
            _bytes().replace(
                b"2026-07-23T00:00:00.000000000Z",
                b"2026-07-23T05:00:00.000000000Z",
            ),
            "future observations",
        ),
    )
    for raw, message in cases:
        with pytest.raises(ValueError, match=message):
            _run(tmp_path, raw)


def test_d6_result_cannot_gain_any_authority(tmp_path: Path) -> None:
    result = _run(tmp_path)
    for changes in (
        {"operator_review_required": False},
        {"local_only": False},
        {"network_used": True},
        {"sdk_used": True},
        {"source_rows_retained": True},
        {"source_values_retained": True},
        {"local_paths_retained": True},
        {"provider_selected": True},
        {"venue_selected": True},
        {"realtime_activated": True},
        {"data_promoted": True},
        {"mark_or_index_authority": True},
        {"signal_authority": True},
        {"product_authority": True},
        {"execution_authority": True},
    ):
        with pytest.raises(ValueError, match="cannot gain authority"):
            replace(result, **changes)
    with pytest.raises(ValueError, match="GAP-095 must remain open"):
        replace(result, gap_095_status="CLOSED")


def test_validation_and_rendering_are_deterministic(tmp_path: Path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)
    assert first == second
    assert first.result_hash == second.result_hash
    assert render_validation_json(first) == render_validation_json(second)


def test_runner_and_renderer_require_typed_inputs(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="request must be typed"):
        validate_registered_coin_metrics_btc_reference_csv(
            tmp_path, object()  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError, match="result must be typed"):
        render_validation_json(object())  # type: ignore[arg-type]
