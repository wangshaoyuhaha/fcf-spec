from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    AShareDailyRowSupplement,
    RegisteredLocalDailyExport,
    canonicalize_registered_local_daily_export,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
)
from apps.fcp_0036_guojin_qmt_registered_local_daily_batch_coverage_reconciliation_app_1 import (
    RegisteredExpectedTradingDateSet,
    RegisteredQmtDailyBatch,
    reconcile_registered_qmt_daily_batches,
)


AS_OF = "2026-07-23T03:00:00Z"


def _qmt_bytes(*dates: str, close_20: str = "5.20") -> bytes:
    rows = {
        "20260717": "20260717,5.00,5.10,4.90,5.05,100.0,50000.00",
        "20260720": f"20260720,5.10,5.30,5.00,{close_20},110.0,57200.00",
        "20260721": "20260721,5.20,5.40,5.10,5.30,120.0,63600.00",
    }
    return (
        "timetag,open,high,low,close,volumn,amount\n"
        + "\n".join(rows[value] for value in dates)
        + "\n"
    ).encode("ascii")


def _expected_bytes(*dates: str) -> bytes:
    return ("trade_date\n" + "\n".join(dates) + "\n").encode("ascii")


def _registration(
    raw: bytes,
    *,
    artifact_id: str,
    source_id: str = "guojin-qmt-local-export",
) -> RegisteredLocalDailyExport:
    return RegisteredLocalDailyExport(
        artifact_id=artifact_id,
        source_id=source_id,
        artifact_sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
        registered_at_utc="2026-07-21T12:40:00Z",
        rights_state="DECLARED_LOCAL_RESEARCH",
        retention_state="SESSION_ONLY",
    )


def _profile() -> QmtLocalDailyExportProfile:
    return QmtLocalDailyExportProfile(
        profile_id="guojin-qmt-daily-batch-v1",
        source_id="guojin-qmt-local-export",
        instrument_id="600028.XSHG",
        requested_start_date="2026-07-17",
        requested_end_date="2026-07-21",
    )


def _write(path: Path, raw: bytes) -> Path:
    path.write_bytes(raw)
    return path


def _batch(path: Path, raw: bytes, sequence: int) -> RegisteredQmtDailyBatch:
    return RegisteredQmtDailyBatch(
        batch_id=f"batch-{sequence:02d}",
        sequence=sequence,
        file_path=path,
        registration=_registration(raw, artifact_id=f"qmt-batch-{sequence:02d}"),
    )


def _expected(path: Path, raw: bytes) -> RegisteredExpectedTradingDateSet:
    return RegisteredExpectedTradingDateSet(
        registration=_registration(
            raw,
            artifact_id="expected-trading-dates-v1",
            source_id="operator-registered-trading-dates",
        ),
        instrument_id="600028.XSHG",
    )


def _reconcile(
    tmp_path: Path,
    batch_specs: tuple[tuple[bytes, int], ...],
    expected_values: tuple[str, ...] = (
        "2026-07-17",
        "2026-07-20",
        "2026-07-21",
    ),
    **changes: object,
):
    batches = tuple(
        _batch(_write(tmp_path / f"batch-{sequence}.txt", raw), raw, sequence)
        for raw, sequence in batch_specs
    )
    expected_raw = _expected_bytes(*expected_values)
    expected_path = _write(tmp_path / "expected.csv", expected_raw)
    values: dict[str, object] = {
        "batches": batches,
        "profile": _profile(),
        "expected_dates_file_path": expected_path,
        "expected_dates": _expected(expected_path, expected_raw),
        "output_artifact_id": "qmt-batch-merged-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return reconcile_registered_qmt_daily_batches(**values)


def test_identical_overlap_is_deduplicated_with_exact_coverage(
    tmp_path: Path,
) -> None:
    first = _qmt_bytes("20260717", "20260720")
    second = _qmt_bytes("20260720", "20260721")

    result = _reconcile(tmp_path, ((first, 1), (second, 2)))

    assert result.quality_state == (
        "COVERAGE_RECONCILED_CANONICAL_SUPPLEMENTS_REQUIRED"
    )
    assert result.operator_review_required is True
    assert result.provider_selected is False
    assert result.manifest.row_count == 3
    assert result.manifest.expected_date_count == 3
    assert result.manifest.identical_overlap_count == 1
    assert result.manifest.missing_dates == ()
    assert result.manifest.unexpected_dates == ()
    assert result.manifest.conflict_dates == ()
    assert "IDENTICAL_OVERLAP_DEDUPLICATED" in result.finding_codes
    assert "2026-07-18" not in result.merged_csv.decode("ascii")
    assert "2026-07-19" not in result.merged_csv.decode("ascii")


def test_reconciliation_is_deterministic(tmp_path: Path) -> None:
    first = _qmt_bytes("20260717", "20260720")
    second = _qmt_bytes("20260720", "20260721")

    first_result = _reconcile(tmp_path, ((first, 1), (second, 2)))
    second_result = _reconcile(tmp_path, ((first, 1), (second, 2)))

    assert first_result.merged_csv == second_result.merged_csv
    assert first_result.manifest.manifest_hash == second_result.manifest.manifest_hash


def test_conflicting_overlap_is_quarantined(tmp_path: Path) -> None:
    first = _qmt_bytes("20260717", "20260720")
    second = _qmt_bytes("20260720", "20260721", close_20="5.25")

    result = _reconcile(tmp_path, ((first, 1), (second, 2)))

    assert result.quality_state == "QUARANTINED_CONFLICT"
    assert result.manifest.conflict_dates == ("2026-07-20",)
    assert "2026-07-20" in result.manifest.missing_dates
    assert "CONFLICTING_OVERLAP_QUARANTINED" in result.finding_codes
    assert b"2026-07-20" not in result.merged_csv


def test_missing_and_unexpected_registered_dates_remain_visible(
    tmp_path: Path,
) -> None:
    raw = _qmt_bytes("20260717", "20260721")
    result = _reconcile(
        tmp_path,
        ((raw, 1),),
        expected_values=("2026-07-17", "2026-07-20"),
    )

    assert result.quality_state == "BLOCKED_COVERAGE_MISMATCH"
    assert result.manifest.missing_dates == ("2026-07-20",)
    assert result.manifest.unexpected_dates == ("2026-07-21",)
    assert "EXPECTED_TRADING_DATES_MISSING" in result.finding_codes
    assert "UNREGISTERED_TRADING_DATES_PRESENT" in result.finding_codes


def test_declared_row_cap_is_a_visible_finding(tmp_path: Path) -> None:
    first = _qmt_bytes("20260717", "20260720")
    second = _qmt_bytes("20260720", "20260721")
    result = _reconcile(
        tmp_path,
        ((first, 1), (second, 2)),
        declared_row_cap=2,
    )

    assert result.manifest.row_cap_batch_ids == ("batch-01", "batch-02")
    assert "DECLARED_ROW_CAP_OBSERVED" in result.finding_codes


@pytest.mark.parametrize(
    ("expected_values", "match"),
    [
        (("2026-07-20", "2026-07-17"), "unique and ordered"),
        (("2026-07-17", "2026-07-17"), "unique and ordered"),
        (("2026-02-30",), "ISO date"),
    ],
)
def test_expected_trading_dates_are_exact_registered_evidence(
    tmp_path: Path,
    expected_values: tuple[str, ...],
    match: str,
) -> None:
    raw = _qmt_bytes("20260717")
    with pytest.raises(ValueError, match=match):
        _reconcile(tmp_path, ((raw, 1),), expected_values=expected_values)


def test_expected_date_registration_rejects_byte_tampering(tmp_path: Path) -> None:
    raw = _qmt_bytes("20260717")
    expected_raw = _expected_bytes("2026-07-17")
    path = _write(tmp_path / "expected.csv", expected_raw + b"\n")
    batch = _batch(_write(tmp_path / "batch.txt", raw), raw, 1)

    with pytest.raises(ValueError, match="byte length mismatch"):
        reconcile_registered_qmt_daily_batches(
            (batch,),
            _profile(),
            path,
            _expected(path, expected_raw),
            output_artifact_id="qmt-batch-merged-v1",
            as_of_utc=AS_OF,
        )


def test_expected_dates_cannot_use_natural_day_inference() -> None:
    raw = _expected_bytes("2026-07-17")
    registration = _registration(
        raw,
        artifact_id="expected-trading-dates-v1",
        source_id="operator-registered-trading-dates",
    )
    with pytest.raises(ValueError, match="explicit Operator registration"):
        RegisteredExpectedTradingDateSet(
            registration=registration,
            instrument_id="600028.XSHG",
            natural_day_inference_allowed=True,
        )


def test_batch_sequence_and_source_lineage_are_closed(tmp_path: Path) -> None:
    raw = _qmt_bytes("20260717")
    path = _write(tmp_path / "batch.txt", raw)
    expected_raw = _expected_bytes("2026-07-17")
    expected_path = _write(tmp_path / "expected.csv", expected_raw)
    invalid_sequence = _batch(path, raw, 2)

    with pytest.raises(ValueError, match="ordered and contiguous"):
        reconcile_registered_qmt_daily_batches(
            (invalid_sequence,),
            _profile(),
            expected_path,
            _expected(expected_path, expected_raw),
            output_artifact_id="qmt-batch-merged-v1",
            as_of_utc=AS_OF,
        )

    wrong_source = RegisteredQmtDailyBatch(
        batch_id="batch-01",
        sequence=1,
        file_path=path,
        registration=_registration(
            raw,
            artifact_id="qmt-batch-01",
            source_id="different-source",
        ),
    )
    with pytest.raises(ValueError, match="source lineage"):
        reconcile_registered_qmt_daily_batches(
            (wrong_source,),
            _profile(),
            expected_path,
            _expected(expected_path, expected_raw),
            output_artifact_id="qmt-batch-merged-v1",
            as_of_utc=AS_OF,
        )


def test_merged_bytes_enter_fcp_0019_without_weakening_blockers(
    tmp_path: Path,
) -> None:
    first = _qmt_bytes("20260717", "20260720")
    second = _qmt_bytes("20260720", "20260721")
    result = _reconcile(tmp_path, ((first, 1), (second, 2)))
    merged_path = _write(tmp_path / "merged.csv", result.merged_csv)
    supplements = tuple(
        AShareDailyRowSupplement(
            instrument_id="600028.XSHG",
            trade_date=trade_date,
            event_at_utc=f"{trade_date}T07:00:00Z",
            available_at_utc=f"{trade_date}T07:05:00Z",
            first_tradable_at_utc=f"{trade_date}T07:05:00Z",
            ingested_at_utc=f"{trade_date}T08:00:00Z",
            revision_at_utc=f"{trade_date}T08:00:00Z",
            trading_status="UNKNOWN",
            adjustment_factor=None,
            factor_version=None,
            factor_available_at_utc=None,
        )
        for trade_date in ("2026-07-17", "2026-07-20", "2026-07-21")
    )

    bridged = canonicalize_registered_local_daily_export(
        merged_path,
        result.merged_registration,
        result.bridge_profile,
        supplements,
        output_artifact_id="qmt-batch-canonical-v1",
        as_of_utc=AS_OF,
    )

    assert bridged.quality_state == "BLOCKED"
    assert bridged.finding_codes == (
        "ADJUSTMENT_FACTOR_MISSING",
        "TRADING_STATUS_UNKNOWN",
    )


def test_result_rejects_merged_byte_tampering(tmp_path: Path) -> None:
    raw = _qmt_bytes("20260717")
    result = _reconcile(
        tmp_path,
        ((raw, 1),),
        expected_values=("2026-07-17",),
    )

    with pytest.raises(ValueError, match="registration SHA-256 mismatch"):
        replace(result, merged_csv=result.merged_csv + b"\n")
