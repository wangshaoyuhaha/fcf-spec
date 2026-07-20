from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    CANONICAL_COLUMNS,
    AShareDailyObservation,
    RegisteredDailyArtifact,
    calibrate_registered_a_share_daily_csv,
)


def _csv(
    *,
    factor: str = "0.8",
    factor_available: str = "2026-07-18T01:00:00Z",
    revision_at: str = "2026-07-18T02:00:00Z",
    status: str = "OBSERVED_TRADING",
    volume: str = "1000",
) -> bytes:
    header = ",".join(CANONICAL_COLUMNS)
    row = ",".join(
        (
            "000001.XSHE",
            "2026-07-17",
            "10",
            "11",
            "9",
            "10.5",
            volume,
            "10250.25",
            factor,
            "rq-calibration-v1" if factor else "",
            factor_available if factor else "",
            "2026-07-17T07:00:00Z",
            "2026-07-17T07:01:00Z",
            "2026-07-18T01:30:00Z",
            "2026-07-18T02:00:00Z",
            revision_at,
            status,
        )
    )
    return f"{header}\n{row}\n".encode("ascii")


def _registered(raw: bytes, **changes: object) -> RegisteredDailyArtifact:
    values = {
        "artifact_id": "registered-a-share-daily-v1",
        "source_id": "operator-local-calibration",
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-18T02:01:00Z",
        "rights_state": "DECLARED_LOCAL_RESEARCH",
        "retention_state": "LOCAL_DERIVED_ONLY",
    }
    values.update(changes)
    return RegisteredDailyArtifact(**values)


def _write(tmp_path: Path, raw: bytes) -> Path:
    path = tmp_path / "registered-daily.csv"
    path.write_bytes(raw)
    return path


def test_d1_contract_is_immutable_exact_and_provider_neutral() -> None:
    raw = _csv()
    registration = _registered(raw)
    assert registration.provider_selected is False
    assert registration.raw_repository_storage_allowed is False
    with pytest.raises(FrozenInstanceError):
        registration.source_id = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="exact decimal"):
        AShareDailyObservation(
            instrument_id="000001.XSHE",
            trade_date="2026-07-17",
            raw_open=10.0,
            raw_high="11",
            raw_low="9",
            raw_close="10",
            volume=1,
            amount="10",
            adjustment_factor="1",
            factor_version="v1",
            factor_available_at_utc="2026-07-18T01:00:00Z",
            event_at_utc="2026-07-17T07:00:00Z",
            available_at_utc="2026-07-17T07:01:00Z",
            first_tradable_at_utc="2026-07-18T01:30:00Z",
            ingested_at_utc="2026-07-18T02:00:00Z",
            revision_at_utc="2026-07-18T02:00:00Z",
            trading_status="OBSERVED_TRADING",
            source_artifact_sha256=registration.artifact_sha256,
        )


def test_d2_point_in_time_future_revision_fails_closed(tmp_path: Path) -> None:
    raw = _csv()
    with pytest.raises(ValueError, match="future revision"):
        calibrate_registered_a_share_daily_csv(
            _write(tmp_path, raw),
            _registered(raw),
            as_of_utc="2026-07-18T01:59:59Z",
        )


def test_d2_point_in_time_future_adjustment_factor_fails_closed(tmp_path: Path) -> None:
    raw = _csv(
        factor_available="2026-07-18T03:00:00Z",
        revision_at="2026-07-18T04:00:00Z",
    )
    with pytest.raises(ValueError, match="future adjustment factor"):
        calibrate_registered_a_share_daily_csv(
            _write(tmp_path, raw),
            _registered(raw),
            as_of_utc="2026-07-18T02:00:00Z",
        )


def test_d2_clocks_and_trading_status_are_explicit(tmp_path: Path) -> None:
    raw = _csv()
    observation = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw),
        as_of_utc="2026-07-18T02:00:00Z",
    ).observations[0]
    with pytest.raises(ValueError, match="monotonic"):
        replace(
            observation,
            available_at_utc="2026-07-19T00:00:00Z",
        )


def test_d2_ingest_may_precede_first_tradable_clock(tmp_path: Path) -> None:
    raw = _csv()
    observation = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw),
        as_of_utc="2026-07-18T02:00:00Z",
    ).observations[0]
    earlier_ingest = replace(
        observation,
        ingested_at_utc="2026-07-17T08:00:00Z",
        revision_at_utc="2026-07-18T02:00:00Z",
    )
    assert earlier_ingest.ingested_at_utc < earlier_ingest.first_tradable_at_utc


def test_d3_raw_and_adjusted_views_are_separate(tmp_path: Path) -> None:
    raw = _csv()
    result = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw),
        as_of_utc="2026-07-18T02:00:00Z",
    )
    observation = result.observations[0]
    assert observation.raw_payload()["close"] == "10.5"
    assert observation.raw_payload()["price_view"] == "RAW"
    assert observation.research_payload()["close"] == "8.4"
    assert observation.research_payload()["price_view"] == "FORWARD_ADJUSTED"
    assert observation.adjustment_factor == Decimal("0.8")


def test_d4_all_layers_have_deterministic_lineage(tmp_path: Path) -> None:
    raw = _csv()
    path = _write(tmp_path, raw)
    registration = _registered(raw)
    first = calibrate_registered_a_share_daily_csv(path, registration, as_of_utc="2026-07-18T02:00:00Z")
    second = calibrate_registered_a_share_daily_csv(path, registration, as_of_utc="2026-07-18T02:00:00Z")
    assert tuple(item.layer for item in first.manifests) == ("RAW", "NORMALIZED", "RESEARCH")
    assert first.manifests[1].parent_sha256 == first.manifests[0].content_sha256
    assert first.manifests[2].parent_sha256 == first.manifests[1].content_sha256
    assert first.result_sha256 == second.result_sha256


def test_d5_missing_adjustment_and_rights_block_research(tmp_path: Path) -> None:
    raw = _csv(factor="")
    result = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw, rights_state="UNRESOLVED", retention_state="UNRESOLVED"),
        as_of_utc="2026-07-18T02:00:00Z",
    )
    assert result.quality_state == "BLOCKED"
    assert result.finding_codes == (
        "ADJUSTMENT_FACTOR_MISSING",
        "COMMERCIAL_RIGHTS_UNRESOLVED",
        "RETENTION_RIGHTS_UNRESOLVED",
    )
    assert result.manifests[2].record_count == 0
    with pytest.raises(ValueError, match="unavailable"):
        result.observations[0].research_payload()


def test_d5_digest_tamper_fails_closed(tmp_path: Path) -> None:
    raw = _csv()
    path = _write(tmp_path, raw)
    registration = _registered(raw)
    path.write_bytes(raw + b"\n")
    with pytest.raises(ValueError, match="byte length mismatch"):
        calibrate_registered_a_share_daily_csv(path, registration, as_of_utc="2026-07-18T02:00:00Z")


def test_d5_unknown_status_blocks_research(tmp_path: Path) -> None:
    raw = _csv(status="UNKNOWN", volume="0")
    result = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw),
        as_of_utc="2026-07-18T02:00:00Z",
    )
    assert result.quality_state == "BLOCKED"
    assert result.finding_codes == ("TRADING_STATUS_UNKNOWN",)


def test_d6_ready_result_grants_no_external_or_execution_authority(tmp_path: Path) -> None:
    raw = _csv()
    registration = _registered(raw)
    result = calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        registration,
        as_of_utc="2026-07-18T02:00:00Z",
    )
    assert result.quality_state == "READY_FOR_RESEARCH"
    assert result.finding_codes == ()
    assert registration.provider_selected is False
    assert registration.usage_scope == "LOCAL_EVALUATION_ONLY"
