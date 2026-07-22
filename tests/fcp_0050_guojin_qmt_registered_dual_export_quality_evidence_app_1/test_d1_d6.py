from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
)
from apps.fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_app_1 import (
    QmtRegisteredRowCapObservation,
    build_qmt_dual_export_quality_evidence,
    build_qmt_dual_export_registered_record,
)


AS_OF = "2026-07-22T01:00:00Z"


def _raw_bytes() -> bytes:
    return (
        "timetag,open,high,low,close,volumn,amount\n"
        "20260717,10,12,9,11,100,110000\n"
        "20260720,11,13,10,12,100,120000\n"
        "20260721,12,14,11,13,100,130000\n"
    ).encode("ascii")


def _front_bytes() -> bytes:
    return (
        "timetag,open,high,low,close,volumn,amount\n"
        "20260717,9.5,11.5,8.5,10.5,100,110000\n"
        "20260720,10.5,12.5,9.5,11.5,100,120000\n"
        "20260721,12,14,11,13,100,130000\n"
    ).encode("ascii")


def _registration(raw: bytes, artifact_id: str) -> RegisteredLocalDailyExport:
    return RegisteredLocalDailyExport(
        artifact_id=artifact_id,
        source_id="guojin-qmt-local-export",
        artifact_sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
        registered_at_utc="2026-07-22T00:30:00Z",
        rights_state="DECLARED_LOCAL_RESEARCH",
        retention_state="SESSION_ONLY",
    )


def _profile() -> QmtLocalDailyExportProfile:
    return QmtLocalDailyExportProfile(
        profile_id="qmt-600028-dual-export-v1",
        source_id="guojin-qmt-local-export",
        instrument_id="600028.XSHG",
        requested_start_date="2026-07-17",
        requested_end_date="2026-07-21",
    )


def _cap(rows: int = 3) -> QmtRegisteredRowCapObservation:
    return QmtRegisteredRowCapObservation(
        observation_id="qmt-local-export-row-cap-v1",
        observed_cap_rows=rows,
        observed_at_utc="2026-07-22T00:45:00Z",
    )


def _write(path: Path, payload: bytes) -> Path:
    path.write_bytes(payload)
    return path


def _build(tmp_path: Path, *, raw: bytes | None = None, front: bytes | None = None, cap_rows: int = 3):
    raw_payload = raw or _raw_bytes()
    front_payload = front or _front_bytes()
    return build_qmt_dual_export_quality_evidence(
        _write(tmp_path / "raw.txt", raw_payload),
        _registration(raw_payload, "qmt-raw-v1"),
        _write(tmp_path / "front.txt", front_payload),
        _registration(front_payload, "qmt-front-v1"),
        _profile(),
        _cap(cap_rows),
        evidence_id="fcp-0050-qmt-dual-export-quality-v1",
        normalized_artifact_id="qmt-normalized-v1",
        as_of_utc=AS_OF,
    )


def test_d1_registers_exact_distinct_local_artifacts(tmp_path: Path) -> None:
    evidence = _build(tmp_path)

    assert evidence.raw_registration.artifact_sha256 == hashlib.sha256(
        _raw_bytes()
    ).hexdigest()
    assert evidence.front_registration.artifact_sha256 == hashlib.sha256(
        _front_bytes()
    ).hexdigest()
    assert evidence.raw_registration.artifact_sha256 != evidence.front_registration.artifact_sha256
    assert evidence.raw_provider_bytes_committed is False
    assert evidence.local_paths_committed is False


def test_d2_validates_100_share_lot_notional_consistency(tmp_path: Path) -> None:
    evidence = _build(tmp_path)

    assert evidence.volume_lot_size == 100
    assert evidence.lot_size_consistency_state == "CONSISTENT_WITH_100_SHARE_LOTS"
    assert "LOT_SIZE_100_NOTIONAL_RANGE_CONSISTENT" in evidence.finding_codes

    invalid = _raw_bytes().replace(b"110000", b"200000", 1)
    invalid_front = _front_bytes().replace(b"110000", b"200000", 1)
    with pytest.raises(ValueError, match="inconsistent with 100-share lots"):
        _build(tmp_path, raw=invalid, front=invalid_front)


def test_d3_requires_exact_raw_front_date_volume_amount_parity(tmp_path: Path) -> None:
    evidence = _build(tmp_path)
    assert evidence.raw_front_parity_state == "DATE_VOLUME_AMOUNT_EXACT"

    changed = _front_bytes().replace(b",100,110000", b",101,110000", 1)
    with pytest.raises(ValueError, match="changed volume or amount"):
        _build(tmp_path, front=changed)


def test_d4_preserves_additive_offsets_and_boundaries_as_reference(tmp_path: Path) -> None:
    evidence = _build(tmp_path)

    assert evidence.offset_distribution == (("0", 1), ("0.5", 2))
    assert evidence.boundary_dates == ("2026-07-21",)
    assert evidence.adjustment_factor_authority is False
    assert len(evidence.row_ledger_sha256) == 64


def test_d5_row_cap_remains_observation_not_completeness_authority(tmp_path: Path) -> None:
    evidence = _build(tmp_path)

    assert evidence.row_cap_state == "AT_REGISTERED_CAP"
    assert evidence.row_cap_observation.pagination_authority is False
    assert evidence.row_cap_observation.completeness_authority is False
    assert evidence.historical_completeness_claimed is False
    assert "HISTORICAL_COMPLETENESS_UNPROVEN" in evidence.finding_codes
    assert "MULTI_BATCH_COVERAGE_MISSING" in evidence.finding_codes

    below = _build(tmp_path, cap_rows=500)
    assert below.row_cap_state == "BELOW_REGISTERED_CAP"
    assert "BELOW_REGISTERED_ROW_CAP" in below.finding_codes


def test_d6_registered_record_excludes_paths_and_raw_values(tmp_path: Path) -> None:
    record = build_qmt_dual_export_registered_record(_build(tmp_path))
    text = repr(record)

    assert record["quality"]["quality_state"] == "BLOCKED_PENDING_SUPPLEMENTS"
    assert record["operator_review_required"] is True
    assert record["artifact_pair"]["raw_provider_bytes_committed"] is False
    assert record["artifact_pair"]["local_paths_committed"] is False
    assert "raw.txt" not in text
    assert "front.txt" not in text
    assert "110000" not in text
    payload = dict(record)
    record_sha256 = payload.pop("record_sha256")
    assert record_sha256 == canonical_sha256(payload)


def test_evidence_is_deterministic_and_preserves_blocking_gaps(tmp_path: Path) -> None:
    first = _build(tmp_path)
    second = _build(tmp_path)

    assert first.evidence_hash == second.evidence_hash
    assert first.row_ledger_sha256 == second.row_ledger_sha256
    for finding in (
        "ADJUSTMENT_FACTOR_MISSING",
        "EXPECTED_TRADING_CALENDAR_MISSING",
        "EXTERNAL_SDK_ENTITLEMENT_UNRESOLVED",
        "INDEPENDENT_SOURCE_RECONCILIATION_MISSING",
        "POINT_IN_TIME_SUPPLEMENTS_MISSING",
        "TRADING_STATUS_UNKNOWN",
    ):
        assert finding in first.finding_codes


def test_evidence_cannot_gain_authority(tmp_path: Path) -> None:
    evidence = _build(tmp_path)

    for changes in (
        {"operator_review_required": False},
        {"adjustment_factor_authority": True},
        {"historical_completeness_claimed": True},
        {"provider_selected": True},
        {"gap_closed": True},
        {"sdk_used": True},
        {"network_used": True},
        {"raw_provider_bytes_committed": True},
        {"local_paths_committed": True},
    ):
        with pytest.raises(ValueError, match="cannot gain source, factor, runtime, or GAP authority"):
            replace(evidence, **changes)


def test_row_cap_observation_cannot_claim_pagination_or_completeness() -> None:
    with pytest.raises(ValueError, match="grants no pagination or completeness authority"):
        replace(_cap(), pagination_authority=True)
    with pytest.raises(ValueError, match="grants no pagination or completeness authority"):
        replace(_cap(), completeness_authority=True)


def test_exact_upstream_schema_and_artifact_hash_are_enforced(tmp_path: Path) -> None:
    changed_header = _raw_bytes().replace(b"volumn", b"volume", 1)
    with pytest.raises(ValueError, match="columns are not exact"):
        _build(tmp_path, raw=changed_header)

    raw = _raw_bytes()
    path = _write(tmp_path / "raw.txt", raw)
    front = _front_bytes()
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        build_qmt_dual_export_quality_evidence(
            path,
            replace(_registration(raw, "qmt-raw-v1"), artifact_sha256="0" * 64),
            _write(tmp_path / "front.txt", front),
            _registration(front, "qmt-front-v1"),
            _profile(),
            _cap(),
            evidence_id="fcp-0050-qmt-dual-export-quality-v1",
            normalized_artifact_id="qmt-normalized-v1",
            as_of_utc=AS_OF,
        )
